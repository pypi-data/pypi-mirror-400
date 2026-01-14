"""NVDEC Worker Manager for StreamingGateway integration.

This module provides a simplified manager for the NVDEC hardware decoding backend.
Unlike other backends, NVDEC uses static camera configuration at startup and outputs
to CUDA IPC ring buffers (NV12 format) for zero-copy GPU inference pipelines.
"""

import logging
import multiprocessing as mp
import time
from typing import Dict, List, Optional, Any

from .nvdec import (
    nvdec_pool_process,
    StreamConfig,
    CUPY_AVAILABLE,
    PYNVCODEC_AVAILABLE,
    RING_BUFFER_AVAILABLE,
)

logger = logging.getLogger(__name__)


def is_nvdec_available() -> bool:
    """Check if NVDEC backend is available.

    Requires:
        - CuPy with CUDA support
        - PyNvVideoCodec for NVDEC hardware decode
        - cuda_shm_ring_buffer module for CUDA IPC
    """
    return CUPY_AVAILABLE and PYNVCODEC_AVAILABLE and RING_BUFFER_AVAILABLE


def get_available_gpu_count() -> int:
    """Detect the number of available CUDA GPUs.

    Returns:
        Number of available GPUs, or 1 if detection fails.
    """
    if not CUPY_AVAILABLE:
        return 1

    try:
        import cupy as cp
        return cp.cuda.runtime.getDeviceCount()
    except Exception as e:
        logger.warning(f"Failed to detect GPU count: {e}, defaulting to 1")
        return 1


class NVDECWorkerManager:
    """Manager for NVDEC worker processes - static camera configuration.

    This manager wraps the existing nvdec_pool_process function to integrate
    with StreamingGateway. Key differences from other worker managers:

    - Static camera configuration (no dynamic add/remove)
    - Outputs to CUDA IPC ring buffers (not Redis/Kafka)
    - NV12 format output (50% smaller than RGB)
    - One worker process per GPU
    """

    def __init__(
        self,
        camera_configs: List[Dict[str, Any]],
        stream_config: Dict[str, Any],  # Unused but kept for interface consistency
        gpu_id: int = 0,
        num_gpus: int = 0,  # 0 = auto-detect all available GPUs
        nvdec_pool_size: int = 8,
        nvdec_burst_size: int = 4,
        frame_width: int = 640,
        frame_height: int = 640,
        num_slots: int = 32,
        target_fps: int = 0,  # 0 = use per-camera FPS from config
        duration_sec: float = 0,  # 0 = infinite
    ):
        """Initialize NVDEC Worker Manager.

        Args:
            camera_configs: List of camera configuration dicts with keys:
                - camera_id or stream_key: Unique identifier (used for ring buffer naming)
                - source: Video file path or RTSP URL
                - width: Optional frame width (default: frame_width)
                - height: Optional frame height (default: frame_height)
                - fps: FPS limit for this camera (used by default)
            stream_config: Stream configuration (unused, for interface consistency)
            gpu_id: Primary GPU device ID (starting GPU for round-robin assignment)
            num_gpus: Number of GPUs to use (0 = auto-detect all available GPUs)
            nvdec_pool_size: Number of NVDEC decoders per GPU
            nvdec_burst_size: Frames per stream before rotating to next
            frame_width: Default output frame width (used if camera config doesn't specify)
            frame_height: Default output frame height (used if camera config doesn't specify)
            num_slots: Ring buffer slots per camera
            target_fps: Global FPS override (0 = use per-camera FPS from config)
            duration_sec: Duration to run (0 = infinite until stop)
        """
        if not is_nvdec_available():
            raise RuntimeError(
                "NVDEC not available. Requires CuPy, PyNvVideoCodec, and cuda_shm_ring_buffer"
            )

        self.camera_configs = camera_configs
        self.stream_config = stream_config
        self.gpu_id = gpu_id

        # Auto-detect GPUs if num_gpus is 0
        if num_gpus <= 0:
            detected_gpus = get_available_gpu_count()
            self.num_gpus = min(detected_gpus, 8)  # Max 8 GPUs
            logger.info(f"Auto-detected {detected_gpus} GPU(s), using {self.num_gpus}")
        else:
            self.num_gpus = min(num_gpus, 8)  # Max 8 GPUs
        self.nvdec_pool_size = nvdec_pool_size
        self.nvdec_burst_size = nvdec_burst_size
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.num_slots = num_slots
        self.target_fps = target_fps
        self.duration_sec = duration_sec if duration_sec > 0 else float('inf')

        self._workers: List[mp.Process] = []
        self._stop_event: Optional[mp.Event] = None
        self._result_queue: Optional[mp.Queue] = None
        self._shared_frame_count: Optional[mp.Value] = None
        self._start_time: Optional[float] = None
        self._is_running = False

        # Convert camera configs to StreamConfig objects and assign to GPUs
        self._stream_configs: List[StreamConfig] = []
        self._gpu_camera_assignments: Dict[int, List[StreamConfig]] = {
            i: [] for i in range(self.num_gpus)
        }
        self._camera_to_gpu: Dict[str, int] = {}

        self._prepare_camera_configs()

        logger.info(
            f"NVDECWorkerManager initialized: {len(camera_configs)} cameras, "
            f"{self.num_gpus} GPU(s), pool_size={nvdec_pool_size}"
        )

    def _prepare_camera_configs(self):
        """Convert dict configs to StreamConfig and distribute across GPUs.

        Ring buffers are named using camera_id for SHM identification.
        Per-camera FPS from config is used by default (target_fps=0 means use config FPS).
        """
        for i, config in enumerate(self.camera_configs):
            # Extract camera ID (support both camera_id and stream_key)
            # This ID is used for naming the CUDA IPC ring buffer
            camera_id = config.get('camera_id') or config.get('stream_key') or f"cam_{i:04d}"

            # Extract video source
            source = config.get('source') or config.get('video_path')
            if not source:
                logger.warning(f"Camera {camera_id} has no source, skipping")
                continue

            # Extract dimensions (use per-camera config or fallback to defaults)
            width = config.get('width') or self.frame_width
            height = config.get('height') or self.frame_height

            # Determine FPS: use global override if set, otherwise per-camera FPS from config
            if self.target_fps > 0:
                # Global FPS override is set
                fps = self.target_fps
            else:
                # Use per-camera FPS from config (default streaming FPS)
                fps = config.get('fps', 10)  # Default to 10 FPS if not specified

            # Assign to GPU (round-robin starting from gpu_id)
            gpu_id = (self.gpu_id + i) % self.num_gpus

            stream_config = StreamConfig(
                camera_id=camera_id,
                video_path=source,
                width=width,
                height=height,
                target_fps=fps,
                gpu_id=gpu_id,
            )

            self._stream_configs.append(stream_config)
            self._gpu_camera_assignments[gpu_id].append(stream_config)
            self._camera_to_gpu[camera_id] = gpu_id

            logger.debug(f"Camera {camera_id}: source={source}, {width}x{height}@{fps}fps, GPU{gpu_id}")

    def start(self) -> None:
        """Start NVDEC worker processes (one per GPU)."""
        if self._is_running:
            logger.warning("NVDECWorkerManager is already running")
            return

        if not self._stream_configs:
            logger.warning("No cameras configured, nothing to start")
            return

        ctx = mp.get_context("spawn")
        self._stop_event = ctx.Event()
        self._result_queue = ctx.Queue()
        self._shared_frame_count = ctx.Value('i', 0)
        self._start_time = time.perf_counter()

        # Start one process per GPU that has cameras
        for gpu_id in range(self.num_gpus):
            gpu_cameras = self._gpu_camera_assignments[gpu_id]
            if not gpu_cameras:
                continue

            p = ctx.Process(
                target=nvdec_pool_process,
                args=(
                    gpu_id,                     # process_id
                    gpu_cameras,                # camera_configs (List[StreamConfig])
                    self.nvdec_pool_size,       # pool_size
                    self.duration_sec,          # duration_sec
                    self._result_queue,         # result_queue
                    self._stop_event,           # stop_event
                    self.nvdec_burst_size,      # burst_size
                    self.num_slots,             # num_slots
                    self.target_fps,            # target_fps
                    self._shared_frame_count,   # shared_frame_count
                ),
                name=f"NVDECWorker-GPU{gpu_id}",
                daemon=False,
            )
            p.start()
            self._workers.append(p)
            logger.info(f"Started NVDEC worker on GPU {gpu_id} with {len(gpu_cameras)} cameras")

        self._is_running = True
        logger.info(f"NVDECWorkerManager started: {len(self._workers)} workers")

    def stop(self, timeout: float = 15.0) -> None:
        """Stop all worker processes.

        Args:
            timeout: Maximum time to wait for each worker to stop gracefully
        """
        if not self._is_running:
            logger.warning("NVDECWorkerManager is not running")
            return

        logger.info("Stopping NVDECWorkerManager...")

        # Signal workers to stop
        if self._stop_event:
            self._stop_event.set()

        # Wait for workers to finish
        for p in self._workers:
            p.join(timeout=timeout)
            if p.is_alive():
                logger.warning(f"Worker {p.name} did not stop gracefully, terminating")
                p.terminate()
                p.join(timeout=2.0)

        self._workers.clear()
        self._is_running = False
        logger.info("NVDECWorkerManager stopped")

    def get_worker_statistics(self) -> Dict[str, Any]:
        """Return statistics from workers.

        Returns:
            Dict with keys:
                - num_workers: Number of worker processes
                - running_workers: Number of currently running workers
                - total_cameras: Total cameras across all workers
                - gpu_assignments: Cameras per GPU
                - total_frames: Total frames processed (from shared counter)
                - elapsed_sec: Time since start
                - aggregate_fps: Overall FPS
                - per_stream_fps: Average FPS per camera
                - backend: 'nvdec'
                - gpu_results: Per-GPU results from result queue
        """
        stats = {
            'backend': 'nvdec',
            'num_workers': len(self._workers),
            'running_workers': sum(1 for p in self._workers if p.is_alive()),
            'total_cameras': len(self._stream_configs),
            'gpu_assignments': {
                gpu_id: len(cameras)
                for gpu_id, cameras in self._gpu_camera_assignments.items()
            },
            'nvdec_config': {
                'gpu_id': self.gpu_id,
                'num_gpus': self.num_gpus,
                'pool_size': self.nvdec_pool_size,
                'burst_size': self.nvdec_burst_size,
                'frame_size': f"{self.frame_width}x{self.frame_height}",
                'num_slots': self.num_slots,
                'target_fps': self.target_fps,
            },
        }

        # Add frame count and FPS
        if self._shared_frame_count:
            total_frames = self._shared_frame_count.value
            stats['total_frames'] = total_frames

            if self._start_time:
                elapsed = time.perf_counter() - self._start_time
                stats['elapsed_sec'] = elapsed
                stats['aggregate_fps'] = total_frames / elapsed if elapsed > 0 else 0
                stats['per_stream_fps'] = (
                    stats['aggregate_fps'] / len(self._stream_configs)
                    if self._stream_configs else 0
                )

        # Collect any available results from queue (non-blocking)
        gpu_results = []
        if self._result_queue:
            while True:
                try:
                    result = self._result_queue.get_nowait()
                    gpu_results.append(result)
                except:
                    break
        stats['gpu_results'] = gpu_results

        return stats

    def get_camera_assignments(self) -> Dict[str, int]:
        """Return mapping of camera_id to GPU ID.

        Returns:
            Dict mapping camera_id -> gpu_id
        """
        return self._camera_to_gpu.copy()

    def add_camera(self, camera_config: Dict[str, Any]) -> bool:
        """Not supported - NVDEC uses static camera configuration.

        Raises:
            NotImplementedError: Always raised
        """
        raise NotImplementedError(
            "NVDEC backend uses static camera configuration. "
            "Cameras must be configured at initialization."
        )

    def remove_camera(self, stream_key: str) -> bool:
        """Not supported - NVDEC uses static camera configuration.

        Raises:
            NotImplementedError: Always raised
        """
        raise NotImplementedError(
            "NVDEC backend uses static camera configuration. "
            "Cameras cannot be removed at runtime."
        )

    def update_camera(self, camera_config: Dict[str, Any]) -> bool:
        """Not supported - NVDEC uses static camera configuration.

        Raises:
            NotImplementedError: Always raised
        """
        raise NotImplementedError(
            "NVDEC backend uses static camera configuration. "
            "Cameras cannot be updated at runtime."
        )

    @property
    def is_running(self) -> bool:
        """Check if the manager is currently running."""
        return self._is_running

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
