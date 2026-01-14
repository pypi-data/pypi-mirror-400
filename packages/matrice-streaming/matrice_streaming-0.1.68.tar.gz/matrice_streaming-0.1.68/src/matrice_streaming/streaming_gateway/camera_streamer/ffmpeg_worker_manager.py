"""Worker manager for coordinating multiple FFmpeg async camera workers.

This module manages a pool of FFmpeg-based async worker processes,
distributing cameras across them and monitoring their health.
"""
import logging
import multiprocessing
import os
import sys
import time
import signal
from typing import List, Dict, Any, Optional
from dataclasses import asdict

from .async_ffmpeg_worker import run_ffmpeg_worker
from .ffmpeg_config import FFmpegConfig, is_ffmpeg_available


class FFmpegWorkerManager:
    """Manages multiple FFmpeg async camera worker processes.

    This manager coordinates worker processes, distributing cameras
    across them for optimal throughput using FFmpeg subprocesses
    for video ingestion.
    """

    def __init__(
        self,
        camera_configs: List[Dict[str, Any]],
        stream_config: Dict[str, Any],
        num_workers: Optional[int] = None,
        cpu_percentage: float = 0.9,
        max_cameras_per_worker: int = 100,
        # FFmpeg configuration
        ffmpeg_config: Optional[FFmpegConfig] = None,
        # SHM options
        use_shm: bool = False,
        shm_slot_count: int = 1000,
        shm_frame_format: str = "BGR",
        # Performance options
        pin_cpu_affinity: bool = True,
    ):
        """Initialize FFmpeg worker manager.

        Args:
            camera_configs: List of all camera configurations
            stream_config: Streaming configuration (Redis, Kafka, etc.)
            num_workers: Number of worker processes (default: auto-calculated)
            cpu_percentage: Percentage of CPU cores to use (default: 0.9)
            max_cameras_per_worker: Maximum cameras per worker (default: 100)
            ffmpeg_config: FFmpeg configuration options
            use_shm: Enable SHM mode for raw frame sharing
            shm_slot_count: Number of frame slots per camera ring buffer
            shm_frame_format: Frame format for SHM storage
            pin_cpu_affinity: Pin workers to specific CPU cores
        """
        self.camera_configs = camera_configs
        self.stream_config = stream_config
        self.ffmpeg_config = ffmpeg_config or FFmpegConfig()

        # Validate FFmpeg availability
        if not is_ffmpeg_available():
            raise RuntimeError("FFmpeg is not available on this system")

        self.logger = logging.getLogger(__name__)

        # Calculate worker count
        if num_workers is None:
            cpu_count = os.cpu_count() or 4
            num_cameras = len(camera_configs)

            if cpu_count >= 16 or num_cameras >= 100:
                target_cameras_per_worker = 25
                calculated_workers = max(4, min(num_cameras // target_cameras_per_worker, 50))
            else:
                calculated_workers = max(4, int(cpu_count * cpu_percentage))

            self.num_workers = min(calculated_workers, num_cameras) if num_cameras > 0 else calculated_workers
        else:
            self.num_workers = num_workers

        self.max_cameras_per_worker = max_cameras_per_worker

        # Log scaling info
        cpu_count = os.cpu_count() or 4
        self.logger.info(
            f"FFmpeg worker scaling: {cpu_count} CPU cores, "
            f"using {self.num_workers} workers for {len(camera_configs)} cameras"
        )

        # SHM configuration
        self.use_shm = use_shm
        self.shm_slot_count = shm_slot_count
        self.shm_frame_format = shm_frame_format

        # Performance configuration
        self.pin_cpu_affinity = pin_cpu_affinity

        if pin_cpu_affinity:
            self.logger.info("CPU affinity pinning ENABLED")

        # Multiprocessing primitives
        self.stop_event = multiprocessing.Event()
        self.health_queue = multiprocessing.Queue()

        # Worker processes
        self.workers: List[multiprocessing.Process] = []
        self.worker_camera_assignments: Dict[int, List[Dict[str, Any]]] = {}

        # Health monitoring
        self.last_health_reports: Dict[int, Dict[str, Any]] = {}

        # Dynamic camera support
        self.command_queues: Dict[int, multiprocessing.Queue] = {}
        self.response_queue = multiprocessing.Queue()

        # Camera tracking
        self.camera_to_worker: Dict[str, int] = {}
        self.worker_camera_count: Dict[int, int] = {}

        self.logger.info(
            f"FFmpegWorkerManager initialized: {self.num_workers} workers, "
            f"{len(camera_configs)} cameras, hwaccel={self.ffmpeg_config.hwaccel}"
        )

    def start(self):
        """Start all workers and begin streaming."""
        try:
            self._distribute_cameras()

            self.logger.info(f"Starting {self.num_workers} FFmpeg worker processes...")
            for worker_id in range(self.num_workers):
                self._start_worker(worker_id)

            self.logger.info(
                f"All FFmpeg workers started! "
                f"Streaming {len(self.camera_configs)} cameras across {self.num_workers} workers"
            )
        except Exception as e:
            self.logger.error(f"Failed to start FFmpeg workers: {e}")
            self.stop()
            raise

    def _distribute_cameras(self):
        """Distribute cameras across workers using static partitioning."""
        total_cameras = len(self.camera_configs)
        cameras_per_worker = total_cameras // self.num_workers
        remainder = total_cameras % self.num_workers

        self.logger.info(
            f"Distributing {total_cameras} cameras: "
            f"~{cameras_per_worker} per worker"
        )

        camera_idx = 0
        for worker_id in range(self.num_workers):
            num_cameras = cameras_per_worker + (1 if worker_id < remainder else 0)
            worker_cameras = self.camera_configs[camera_idx:camera_idx + num_cameras]
            self.worker_camera_assignments[worker_id] = worker_cameras

            self.logger.info(
                f"Worker {worker_id}: {len(worker_cameras)} cameras "
                f"(indices {camera_idx} to {camera_idx + num_cameras - 1})"
            )

            camera_idx += num_cameras

    def _start_worker(self, worker_id: int):
        """Start a single FFmpeg worker process.

        Args:
            worker_id: Worker identifier
        """
        worker_cameras = self.worker_camera_assignments.get(worker_id, [])

        command_queue = multiprocessing.Queue()
        self.command_queues[worker_id] = command_queue

        self.worker_camera_count[worker_id] = len(worker_cameras)

        for cam_config in worker_cameras:
            stream_key = cam_config.get('stream_key')
            if stream_key:
                self.camera_to_worker[stream_key] = worker_id

        # Convert FFmpeg config to dict for pickling
        ffmpeg_config_dict = asdict(self.ffmpeg_config)

        try:
            if sys.platform == 'win32':
                ctx = multiprocessing.get_context('spawn')
            else:
                ctx = multiprocessing.get_context('fork')

            worker = ctx.Process(
                target=run_ffmpeg_worker,
                args=(
                    worker_id,
                    worker_cameras,
                    self.stream_config,
                    self.stop_event,
                    self.health_queue,
                    command_queue,
                    self.response_queue,
                    ffmpeg_config_dict,
                    self.use_shm,
                    self.shm_slot_count,
                    self.shm_frame_format,
                    self.pin_cpu_affinity,
                    self.num_workers,
                ),
                name=f"FFmpegWorker-{worker_id}",
                daemon=False,
            )
            worker.start()
            self.workers.append(worker)

            self.logger.info(
                f"Started FFmpeg worker {worker_id} (PID: {worker.pid}) "
                f"with {len(worker_cameras)} cameras"
            )
        except Exception as e:
            self.logger.error(f"Failed to start FFmpeg worker {worker_id}: {e}")
            raise

    def monitor(self, duration: Optional[float] = None):
        """Monitor workers and collect health reports.

        Args:
            duration: How long to monitor (None = indefinite)
        """
        self.logger.info("Starting health monitoring...")

        start_time = time.time()
        last_summary_time = start_time

        try:
            while not self.stop_event.is_set():
                if duration and (time.time() - start_time) >= duration:
                    self.logger.info(f"Monitoring duration ({duration}s) complete")
                    break

                # Collect health reports
                while not self.health_queue.empty():
                    try:
                        report = self.health_queue.get_nowait()
                        worker_id = report['worker_id']
                        self.last_health_reports[worker_id] = report

                        if report['status'] in ['error', 'stopped']:
                            self.logger.warning(
                                f"Worker {worker_id} status: {report['status']} "
                                f"(error: {report.get('error', 'None')})"
                            )
                    except Exception as e:
                        self.logger.error(f"Error processing health report: {e}")

                # Check worker processes
                for i, worker in enumerate(self.workers):
                    if not worker.is_alive() and not self.stop_event.is_set():
                        self.logger.error(
                            f"FFmpeg worker {i} (PID: {worker.pid}) died! "
                            f"Exit code: {worker.exitcode}"
                        )

                # Print summary periodically
                if time.time() - last_summary_time >= 10.0:
                    self._print_health_summary()
                    last_summary_time = time.time()

                time.sleep(0.5)

        except KeyboardInterrupt:
            self.logger.info("Monitoring interrupted by user")

    def _print_health_summary(self):
        """Print summary of worker health."""
        running_workers = sum(1 for w in self.workers if w.is_alive())
        total_cameras = sum(
            report.get('active_cameras', 0)
            for report in self.last_health_reports.values()
        )

        self.logger.info(
            f"FFmpeg Health Summary: {running_workers}/{len(self.workers)} workers alive, "
            f"{total_cameras} active cameras"
        )

    def stop(self, timeout: float = 15.0):
        """Stop all workers gracefully.

        Args:
            timeout: Maximum time to wait per worker (seconds)
        """
        self.logger.info("Stopping all FFmpeg workers...")

        self.stop_event.set()

        for i, worker in enumerate(self.workers):
            if worker.is_alive():
                self.logger.info(f"Waiting for FFmpeg worker {i} to stop...")
                worker.join(timeout=timeout)

                if worker.is_alive():
                    self.logger.warning(f"FFmpeg worker {i} did not stop, terminating...")
                    worker.terminate()
                    worker.join(timeout=5.0)

                    if worker.is_alive():
                        self.logger.error(f"FFmpeg worker {i} could not be stopped!")
                    else:
                        self.logger.info(f"FFmpeg worker {i} terminated")
                else:
                    self.logger.info(f"FFmpeg worker {i} stopped gracefully")

        self.logger.info("=" * 60)
        self.logger.info("FFMPEG WORKERS SHUTDOWN COMPLETE")
        self.logger.info("=" * 60)

    def add_camera(self, camera_config: Dict[str, Any]) -> bool:
        """Add a camera to the least-loaded worker at runtime.

        Args:
            camera_config: Camera configuration dictionary

        Returns:
            bool: True if camera was added successfully
        """
        stream_key = camera_config.get('stream_key')
        if not stream_key:
            self.logger.error("Camera config missing stream_key")
            return False

        if stream_key in self.camera_to_worker:
            self.logger.warning(f"Camera {stream_key} already exists")
            return False

        target_worker_id = self._find_least_loaded_worker()
        if target_worker_id is None:
            self.logger.error("All workers at capacity")
            return False

        command = {
            'type': 'add_camera',
            'camera_config': camera_config,
            'timestamp': time.time()
        }

        try:
            self.command_queues[target_worker_id].put(command, timeout=5.0)
            self.camera_to_worker[stream_key] = target_worker_id
            self.worker_camera_count[target_worker_id] += 1
            self.logger.info(f"Sent add_camera for {stream_key} to FFmpeg worker {target_worker_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send add_camera command: {e}")
            return False

    def remove_camera(self, stream_key: str) -> bool:
        """Remove a camera from its assigned worker.

        Args:
            stream_key: Unique identifier for the camera stream

        Returns:
            bool: True if camera removal was initiated
        """
        if stream_key not in self.camera_to_worker:
            self.logger.warning(f"Camera {stream_key} not found")
            return False

        worker_id = self.camera_to_worker[stream_key]

        command = {
            'type': 'remove_camera',
            'stream_key': stream_key,
            'timestamp': time.time()
        }

        try:
            self.command_queues[worker_id].put(command, timeout=5.0)
            del self.camera_to_worker[stream_key]
            self.worker_camera_count[worker_id] -= 1
            self.logger.info(f"Sent remove_camera for {stream_key} to FFmpeg worker {worker_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send remove_camera command: {e}")
            return False

    def _find_least_loaded_worker(self) -> Optional[int]:
        """Find the worker with the least cameras that's not at capacity."""
        available_workers = []
        for worker_id, count in self.worker_camera_count.items():
            if count < self.max_cameras_per_worker and worker_id in self.command_queues:
                if worker_id < len(self.workers) and self.workers[worker_id].is_alive():
                    available_workers.append((worker_id, count))

        if not available_workers:
            return None

        return min(available_workers, key=lambda x: x[1])[0]

    def get_camera_assignments(self) -> Dict[str, int]:
        """Get current camera-to-worker assignments."""
        return self.camera_to_worker.copy()

    def get_worker_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics about workers and cameras."""
        while not self.health_queue.empty():
            try:
                report = self.health_queue.get_nowait()
                worker_id = report.get('worker_id')
                if worker_id is not None:
                    self.last_health_reports[worker_id] = report
            except Exception:
                break

        return {
            'num_workers': len(self.workers),
            'running_workers': sum(1 for w in self.workers if w.is_alive()),
            'total_cameras': sum(self.worker_camera_count.values()),
            'camera_assignments': self.camera_to_worker.copy(),
            'worker_camera_counts': self.worker_camera_count.copy(),
            'backend': 'ffmpeg',
            'ffmpeg_config': {
                'hwaccel': self.ffmpeg_config.hwaccel,
                'pixel_format': self.ffmpeg_config.pixel_format,
                'low_latency': self.ffmpeg_config.low_latency,
            },
            'health_reports': {
                worker_id: {
                    'status': report.get('status', 'unknown'),
                    'active_cameras': report.get('active_cameras', 0),
                    'timestamp': report.get('timestamp', 0),
                    'metrics': report.get('metrics', {}),
                }
                for worker_id, report in self.last_health_reports.items()
            },
        }

    def run(self, duration: Optional[float] = None):
        """Start workers and monitor until stopped.

        Args:
            duration: How long to run (None = until interrupted)
        """
        try:
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            self.start()
            self.monitor(duration=duration)

        except Exception as e:
            self.logger.error(f"Error in run loop: {e}", exc_info=True)
        finally:
            self.stop()

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        signal_name = signal.Signals(signum).name
        self.logger.info(f"Received {signal_name}, initiating graceful shutdown...")
        self.stop_event.set()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
