"""Async FFmpeg worker process for handling multiple cameras concurrently.

This module implements an async event loop worker that uses FFmpeg subprocess
pipelines for video ingestion. This provides better performance than OpenCV
by isolating decoder threads from the Python GIL.
"""
import asyncio
import logging
import time
import multiprocessing
import os
import sys
import signal
import subprocess
from typing import Dict, Any, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor
from collections import deque

import numpy as np
import cv2
import psutil

from matrice_common.optimize import FrameOptimizer

from .ffmpeg_config import FFmpegConfig, is_ffmpeg_available
from .ffmpeg_camera_streamer import FFmpegPipeline


# Disable threading in numerical libraries
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"


def pin_to_cores(worker_id: int, total_workers: int) -> Optional[List[int]]:
    """Pin worker process to specific CPU cores for cache locality.

    Args:
        worker_id: Worker identifier (0-indexed)
        total_workers: Total number of worker processes

    Returns:
        List of CPU core indices this worker is pinned to, or None if pinning failed
    """
    try:
        p = psutil.Process()
        cpu_count = psutil.cpu_count(logical=True)
        cores_per_worker = max(1, cpu_count // total_workers)

        start_core = worker_id * cores_per_worker
        end_core = min(start_core + cores_per_worker, cpu_count)

        core_list = list(range(start_core, end_core))
        if core_list:
            p.cpu_affinity(core_list)
            return core_list
    except Exception:
        pass
    return None


class AsyncFFmpegWorker:
    """Async worker process that handles multiple cameras using FFmpeg pipelines.

    This worker runs an async event loop to handle I/O-bound operations
    for multiple cameras efficiently, using FFmpeg subprocesses for video
    decoding instead of OpenCV.
    """

    def __init__(
        self,
        worker_id: int,
        camera_configs: List[Dict[str, Any]],
        stream_config: Dict[str, Any],
        stop_event: multiprocessing.Event,
        health_queue: multiprocessing.Queue,
        command_queue: Optional[multiprocessing.Queue] = None,
        response_queue: Optional[multiprocessing.Queue] = None,
        ffmpeg_config: Optional[FFmpegConfig] = None,
        # SHM mode options
        use_shm: bool = False,
        shm_slot_count: int = 1000,
        shm_frame_format: str = "BGR",
        # Performance options
        pin_cpu_affinity: bool = True,
        total_workers: int = 1,
        # Frame optimizer options
        frame_optimizer_enabled: bool = True,
        frame_optimizer_config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize async FFmpeg worker.

        Args:
            worker_id: Unique identifier for this worker
            camera_configs: List of camera configurations to handle
            stream_config: Streaming configuration (Redis, Kafka, etc.)
            stop_event: Event to signal worker shutdown
            health_queue: Queue for reporting health status
            command_queue: Queue for receiving dynamic camera commands
            response_queue: Queue for sending command responses
            ffmpeg_config: FFmpeg configuration options
            use_shm: Enable SHM mode for raw frame sharing
            shm_slot_count: Number of frame slots per camera ring buffer
            shm_frame_format: Frame format for SHM storage
            pin_cpu_affinity: Pin worker to specific CPU cores
            total_workers: Total number of workers for CPU affinity calculation
            frame_optimizer_enabled: Enable frame optimizer for skipping similar frames
            frame_optimizer_config: Frame optimizer configuration dict
        """
        self.worker_id = worker_id
        self.camera_configs = camera_configs
        self.stream_config = stream_config
        self.stop_event = stop_event
        self.health_queue = health_queue
        self.command_queue = command_queue
        self.response_queue = response_queue
        self.ffmpeg_config = ffmpeg_config or FFmpegConfig()

        # Setup logging
        self.logger = logging.getLogger(f"AsyncFFmpegWorker-{worker_id}")
        self.logger.info(f"Initializing FFmpeg worker {worker_id} with {len(camera_configs)} cameras")

        # Track camera tasks and pipelines
        self.camera_tasks: Dict[str, asyncio.Task] = {}
        self.pipelines: Dict[str, FFmpegPipeline] = {}

        # Redis/stream client
        self.redis_client = None

        # SHM configuration
        self.use_shm = use_shm
        self.shm_slot_count = shm_slot_count
        self.shm_frame_format = shm_frame_format
        self._shm_buffers: Dict[str, Any] = {}
        self._last_shm_frame_idx: Dict[str, int] = {}

        # Initialize frame optimizer for skipping similar frames
        frame_optimizer_config = frame_optimizer_config or {}
        self.frame_optimizer = FrameOptimizer(
            enabled=frame_optimizer_enabled,
            scale=frame_optimizer_config.get("scale", 0.4),
            diff_threshold=frame_optimizer_config.get("diff_threshold", 15),
            similarity_threshold=frame_optimizer_config.get("similarity_threshold", 0.05),
            bg_update_interval=frame_optimizer_config.get("bg_update_interval", 10),
        )
        self._last_sent_frame_ids: Dict[str, str] = {}  # stream_key -> last sent frame_id

        # Register atexit handler for SHM cleanup
        if use_shm:
            import atexit
            atexit.register(self._cleanup_shm_on_exit)

        # CPU affinity
        self.pin_cpu_affinity = pin_cpu_affinity
        self.total_workers = total_workers
        self.pinned_cores: Optional[List[int]] = None

        # Apply CPU affinity
        if pin_cpu_affinity:
            self.pinned_cores = pin_to_cores(worker_id, total_workers)
            if self.pinned_cores:
                self.logger.info(
                    f"Worker {worker_id}: CPU affinity pinned to cores "
                    f"{self.pinned_cores[0]}-{self.pinned_cores[-1]}"
                )

        # Thread pool for blocking FFmpeg operations
        num_cameras = len(camera_configs)
        num_threads = min(64, max(8, num_cameras))
        self.executor = ThreadPoolExecutor(max_workers=num_threads)

        # Metrics
        self._encoding_times: deque = deque(maxlen=100)
        self._frame_times: deque = deque(maxlen=100)
        self._frames_encoded = 0
        self._encoding_errors = 0
        self._last_metrics_log = time.time()
        self._process_info = psutil.Process(os.getpid())

        # Per-camera metrics for periodic FPS logging
        self._metrics_log_interval = 30.0  # Log metrics every 30 seconds
        self._frames_per_camera: Dict[str, int] = {}
        self._last_fps_check_time = time.time()

        self.logger.info(
            f"Worker {worker_id}: FFmpeg worker initialized with {num_threads} threads"
        )

    async def initialize(self):
        """Initialize async resources (Redis client, etc.)."""
        try:
            from matrice_common.stream import MatriceStream, StreamType

            self.stream = MatriceStream(
                stream_type=StreamType.REDIS,
                enable_shm_batching=True,
                **self.stream_config
            )

            self.redis_client = self.stream.async_client
            await self.redis_client.setup_client()

            self.logger.info(f"Worker {self.worker_id}: Initialized async Redis client")
        except Exception as e:
            self.logger.error(f"Worker {self.worker_id}: Failed to initialize: {e}")
            raise

    def _cleanup_shm_on_exit(self):
        """Cleanup SHM buffers on exit."""
        for camera_id, shm_buffer in list(self._shm_buffers.items()):
            try:
                shm_buffer.close()
            except Exception:
                pass

    def _get_or_create_shm_buffer(self, camera_id: str, width: int, height: int):
        """Get existing or create new SHM buffer for camera.

        Args:
            camera_id: Camera stream key
            width: Frame width
            height: Frame height

        Returns:
            ShmRingBuffer instance for this camera
        """
        if camera_id not in self._shm_buffers:
            from matrice_common.stream.shm_ring_buffer import ShmRingBuffer
            format_map = {
                "BGR": ShmRingBuffer.FORMAT_BGR,
                "RGB": ShmRingBuffer.FORMAT_RGB,
                "NV12": ShmRingBuffer.FORMAT_NV12
            }
            frame_format = format_map.get(self.shm_frame_format, ShmRingBuffer.FORMAT_BGR)
            self._shm_buffers[camera_id] = ShmRingBuffer(
                camera_id=camera_id,
                width=width,
                height=height,
                frame_format=frame_format,
                slot_count=self.shm_slot_count,
                create=True
            )
            self.logger.info(
                f"Worker {self.worker_id}: Created SHM buffer for {camera_id} - "
                f"{width}x{height} @ {self.shm_frame_format}, {self.shm_slot_count} slots"
            )
        return self._shm_buffers[camera_id]

    async def run(self):
        """Main worker loop - starts async tasks for all cameras."""
        try:
            await self.initialize()

            # Start camera tasks
            for camera_config in self.camera_configs:
                await self._add_camera_internal(camera_config)

            # Report initial health
            self._report_health("running", len(self.camera_tasks))

            # Start command handler if queue provided
            command_task = None
            if self.command_queue:
                command_task = asyncio.create_task(
                    self._command_handler(),
                    name="command-handler"
                )

            # Monitor loop
            while not self.stop_event.is_set():
                # Check for completed/failed tasks
                for stream_key, task in list(self.camera_tasks.items()):
                    if task.done():
                        try:
                            task.result()
                        except Exception as e:
                            self.logger.error(f"Camera {stream_key} task failed: {e}")
                        del self.camera_tasks[stream_key]

                self._report_health("running", len(self.camera_tasks))

                # Log metrics periodically
                if time.time() - self._last_metrics_log > self._metrics_log_interval:
                    self._log_metrics()

                await asyncio.sleep(1.0)

            # Shutdown
            self.logger.info(f"Worker {self.worker_id}: Stop event detected, shutting down...")

            if command_task and not command_task.done():
                command_task.cancel()
                try:
                    await command_task
                except asyncio.CancelledError:
                    pass

            await self._shutdown()

        except Exception as e:
            self.logger.error(f"Worker {self.worker_id}: Fatal error: {e}", exc_info=True)
            self._report_health("error", error=str(e))
            raise

    async def _camera_handler(self, camera_config: Dict[str, Any]):
        """Handle a single camera with FFmpeg pipeline.

        Args:
            camera_config: Camera configuration dictionary
        """
        stream_key = camera_config['stream_key']
        stream_group_key = camera_config.get('stream_group_key', 'default')
        source = camera_config['source']
        topic = camera_config['topic']
        fps = camera_config.get('fps', 30)
        quality = camera_config.get('quality', 90)
        width = camera_config.get('width', 0)
        height = camera_config.get('height', 0)
        camera_location = camera_config.get('camera_location', 'Unknown')
        simulate_video_file_stream = camera_config.get('simulate_video_file_stream', False)

        # Retry settings
        MIN_RETRY_COOLDOWN = 5
        MAX_RETRY_COOLDOWN = 30
        retry_cycle = 0
        max_consecutive_failures = 10

        # Create FFmpeg config for this camera
        cam_config = FFmpegConfig(
            hwaccel=self.ffmpeg_config.hwaccel,
            pixel_format=self.ffmpeg_config.pixel_format,
            low_latency=self.ffmpeg_config.low_latency,
            loop=simulate_video_file_stream,
            output_width=width,
            output_height=height,
        )

        while not self.stop_event.is_set():
            pipeline = None
            consecutive_failures = 0
            frame_counter = 0

            try:
                # Create FFmpeg pipeline
                pipeline = FFmpegPipeline(
                    source=str(source),
                    width=width,
                    height=height,
                    config=cam_config,
                    stream_key=stream_key,
                )
                self.pipelines[stream_key] = pipeline

                retry_cycle = 0
                self.logger.info(
                    f"Worker {self.worker_id}: Camera {stream_key} connected via FFmpeg - "
                    f"{pipeline.width}x{pipeline.height} @ {fps} FPS"
                )

                # Frame processing loop
                while not self.stop_event.is_set():
                    try:
                        read_start = time.time()

                        # Read frame from FFmpeg pipeline (async)
                        frame = await pipeline.read_frame_async(self.executor)
                        read_time = time.time() - read_start

                        if frame is None:
                            consecutive_failures += 1
                            if consecutive_failures >= max_consecutive_failures:
                                self.logger.warning(
                                    f"Worker {self.worker_id}: Camera {stream_key} - "
                                    f"{max_consecutive_failures} consecutive failures, reconnecting..."
                                )
                                break
                            await asyncio.sleep(0.1)
                            continue

                        consecutive_failures = 0
                        frame_counter += 1

                        # Process and send frame (SHM mode vs JPEG mode)
                        if self.use_shm:
                            await self._process_frame_shm_mode(
                                frame=frame,
                                stream_key=stream_key,
                                stream_group_key=stream_group_key,
                                topic=topic,
                                width=pipeline.width,
                                height=pipeline.height,
                                frame_counter=frame_counter,
                                camera_location=camera_location,
                                read_time=read_time,
                            )
                        else:
                            await self._process_and_send_frame(
                                frame=frame,
                                stream_key=stream_key,
                                stream_group_key=stream_group_key,
                                topic=topic,
                                width=pipeline.width,
                                height=pipeline.height,
                                quality=quality,
                                frame_counter=frame_counter,
                                camera_location=camera_location,
                                read_time=read_time,
                            )

                        # Maintain target FPS
                        frame_interval = 1.0 / fps
                        elapsed = time.time() - read_start
                        sleep_time = max(0, frame_interval - elapsed)
                        if sleep_time > 0:
                            await asyncio.sleep(sleep_time)

                    except asyncio.CancelledError:
                        self.logger.info(f"Camera {stream_key} task cancelled")
                        return
                    except Exception as e:
                        self.logger.error(f"Error processing camera {stream_key}: {e}")
                        consecutive_failures += 1
                        if consecutive_failures >= max_consecutive_failures:
                            break
                        await asyncio.sleep(1.0)

            except asyncio.CancelledError:
                return
            except Exception as e:
                self.logger.error(f"Camera {stream_key} connection error: {e}")
            finally:
                if pipeline:
                    pipeline.close()
                    if stream_key in self.pipelines:
                        del self.pipelines[stream_key]

            if self.stop_event.is_set():
                break

            # Exponential backoff before retry
            cooldown = min(MAX_RETRY_COOLDOWN, MIN_RETRY_COOLDOWN + retry_cycle)
            self.logger.info(f"Retrying camera {stream_key} in {cooldown}s")
            await asyncio.sleep(cooldown)
            retry_cycle += 1

    async def _process_and_send_frame(
        self,
        frame: np.ndarray,
        stream_key: str,
        stream_group_key: str,
        topic: str,
        width: int,
        height: int,
        quality: int,
        frame_counter: int,
        camera_location: str,
        read_time: float,
    ):
        """Process frame and send to Redis.

        Args:
            frame: Raw frame from FFmpeg
            stream_key: Stream identifier
            stream_group_key: Stream group identifier
            topic: Redis topic
            width: Frame width
            height: Frame height
            quality: JPEG quality
            frame_counter: Current frame number
            camera_location: Camera location
            read_time: Time taken to read frame
        """
        frame_start = time.time()

        # Check frame similarity BEFORE encoding (saves CPU if frame is similar)
        is_similar, similarity_score = self.frame_optimizer.is_similar(frame, stream_key)
        reference_frame_id = self._last_sent_frame_ids.get(stream_key)

        import uuid

        if is_similar and reference_frame_id:
            # Frame is similar - send message with empty content + cached_frame_id
            message = {
                "frame_id": str(uuid.uuid4()),
                "input_name": stream_key,
                "input_stream": {
                    "content": b"",  # EMPTY content for cached frame
                    "metadata": {
                        "width": width,
                        "height": height,
                        "frame_count": frame_counter,
                        "camera_location": camera_location,
                        "stream_group_key": stream_group_key,
                        "encoding_type": "cached",
                        "codec": "cached",
                        "feed_type": "ffmpeg",
                        "timestamp": time.time(),
                        "similarity_score": similarity_score,
                        "cached_frame_id": reference_frame_id,
                    },
                },
            }

            # Send to Redis
            write_start = time.time()
            await self.redis_client.add_message(topic, message)
            write_time = time.time() - write_start

            # Track metrics (no encoding)
            self._frames_per_camera[stream_key] = self._frames_per_camera.get(stream_key, 0) + 1
            total_time = time.time() - frame_start
            self._frame_times.append(total_time)
            return

        # Frame is different - encode and send full frame
        encode_start = time.time()
        success, jpeg_buffer = cv2.imencode(
            '.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        )
        encode_time = time.time() - encode_start

        if not success:
            self._encoding_errors += 1
            return

        self._frames_encoded += 1
        self._frames_per_camera[stream_key] = self._frames_per_camera.get(stream_key, 0) + 1
        self._encoding_times.append(encode_time)

        frame_data = bytes(jpeg_buffer)

        # Build message
        new_frame_id = str(uuid.uuid4())
        message = {
            "frame_id": new_frame_id,
            "input_name": stream_key,
            "input_stream": {
                "content": frame_data,
                "metadata": {
                    "width": width,
                    "height": height,
                    "frame_count": frame_counter,
                    "camera_location": camera_location,
                    "stream_group_key": stream_group_key,
                    "encoding_type": "jpeg",
                    "codec": "h264",
                    "feed_type": "ffmpeg",
                    "timestamp": time.time(),
                },
            },
        }

        # Send to Redis
        write_start = time.time()
        await self.redis_client.add_message(topic, message)
        write_time = time.time() - write_start

        # Track this frame_id as the last sent for future reference frames
        self._last_sent_frame_ids[stream_key] = new_frame_id
        self.frame_optimizer.set_last_frame_id(stream_key, new_frame_id)

        # Track metrics
        total_time = time.time() - frame_start
        self._frame_times.append(total_time)

    async def _process_frame_shm_mode(
        self,
        frame: np.ndarray,
        stream_key: str,
        stream_group_key: str,
        topic: str,
        width: int,
        height: int,
        frame_counter: int,
        camera_location: str,
        read_time: float,
    ):
        """SHM_MODE: Write raw frame to SHM, send metadata to Redis.

        Args:
            frame: Raw frame from FFmpeg (BGR format)
            stream_key: Stream identifier
            stream_group_key: Stream group identifier
            topic: Redis topic
            width: Frame width
            height: Frame height
            frame_counter: Current frame number
            camera_location: Camera location
            read_time: Time taken to read frame
        """
        frame_start = time.time()

        # Check frame similarity BEFORE writing to SHM (saves SHM writes for static scenes)
        is_similar, similarity_score = self.frame_optimizer.is_similar(frame, stream_key)
        reference_frame_idx = self._last_shm_frame_idx.get(stream_key)

        if is_similar and reference_frame_idx is not None:
            # Frame is similar - send metadata with reference to previous frame
            ts_ns = int(time.time() * 1e9)
            shm_buffer = self._shm_buffers.get(stream_key)

            await self.redis_client.add_shm_metadata(
                stream_name=topic,
                cam_id=stream_key,
                shm_name=shm_buffer.shm_name if shm_buffer else "",
                frame_idx=reference_frame_idx,  # Reference to cached frame
                slot=None,  # No new slot written
                ts_ns=ts_ns,
                width=width,
                height=height,
                format=self.shm_frame_format,
                is_similar=True,
                reference_frame_idx=reference_frame_idx,
                similarity_score=similarity_score,
                stream_group_key=stream_group_key,
                camera_location=camera_location,
                frame_counter=frame_counter,
            )

            # Track metrics (no SHM write)
            self._frames_per_camera[stream_key] = self._frames_per_camera.get(stream_key, 0) + 1
            total_time = time.time() - frame_start
            self._frame_times.append(total_time)
            return

        # Frame is different - write to SHM
        # Get or create SHM buffer
        shm_buffer = self._get_or_create_shm_buffer(stream_key, width, height)

        # Convert frame to target format if needed
        if self.shm_frame_format == "RGB":
            raw_bytes = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).tobytes()
        elif self.shm_frame_format == "NV12":
            from matrice_common.stream.shm_ring_buffer import bgr_to_nv12
            raw_bytes = bgr_to_nv12(frame)
        else:  # BGR default
            raw_bytes = frame.tobytes()

        # Write to SHM
        frame_idx, slot = shm_buffer.write_frame(raw_bytes)
        self._last_shm_frame_idx[stream_key] = frame_idx

        # Send metadata to Redis
        ts_ns = int(time.time() * 1e9)
        await self.redis_client.add_shm_metadata(
            stream_name=topic,
            cam_id=stream_key,
            shm_name=shm_buffer.shm_name,
            frame_idx=frame_idx,
            slot=slot,
            ts_ns=ts_ns,
            width=width,
            height=height,
            format=self.shm_frame_format,
            is_similar=False,
            stream_group_key=stream_group_key,
            camera_location=camera_location,
            frame_counter=frame_counter,
        )

        # Track metrics
        self._frames_encoded += 1
        self._frames_per_camera[stream_key] = self._frames_per_camera.get(stream_key, 0) + 1
        total_time = time.time() - frame_start
        self._frame_times.append(total_time)

    async def _command_handler(self):
        """Process commands from the manager."""
        while not self.stop_event.is_set():
            try:
                command = await asyncio.get_event_loop().run_in_executor(
                    None, self._get_command_nonblocking
                )
                if command:
                    await self._process_command(command)
                else:
                    await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in command handler: {e}")
                await asyncio.sleep(1.0)

    def _get_command_nonblocking(self):
        try:
            return self.command_queue.get_nowait()
        except Exception:
            return None

    async def _process_command(self, command: Dict[str, Any]):
        """Process a command."""
        cmd_type = command.get('type')
        self.logger.info(f"Processing command: {cmd_type}")

        try:
            if cmd_type == 'add_camera':
                camera_config = command.get('camera_config')
                success = await self._add_camera_internal(camera_config)
                self._send_response(cmd_type, camera_config.get('stream_key'), success)
            elif cmd_type == 'remove_camera':
                stream_key = command.get('stream_key')
                success = await self._remove_camera_internal(stream_key)
                self._send_response(cmd_type, stream_key, success)
            elif cmd_type == 'update_camera':
                camera_config = command.get('camera_config')
                stream_key = command.get('stream_key')
                await self._remove_camera_internal(stream_key)
                success = await self._add_camera_internal(camera_config)
                self._send_response(cmd_type, stream_key, success)
        except Exception as e:
            self.logger.error(f"Error processing command {cmd_type}: {e}")
            self._send_response(cmd_type, command.get('stream_key'), False, str(e))

    async def _add_camera_internal(self, camera_config: Dict[str, Any]) -> bool:
        """Add a camera and start its streaming task."""
        stream_key = camera_config.get('stream_key')
        if not stream_key:
            return False

        if stream_key in self.camera_tasks:
            self.logger.warning(f"Camera {stream_key} already exists")
            return False

        try:
            task = asyncio.create_task(
                self._camera_handler(camera_config),
                name=f"ffmpeg-camera-{stream_key}"
            )
            self.camera_tasks[stream_key] = task
            self.logger.info(f"Added FFmpeg camera {stream_key}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add camera {stream_key}: {e}")
            return False

    async def _remove_camera_internal(self, stream_key: str) -> bool:
        """Remove a camera and stop its streaming task."""
        if stream_key not in self.camera_tasks:
            return False

        try:
            task = self.camera_tasks[stream_key]
            if not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=5.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass

            del self.camera_tasks[stream_key]

            if stream_key in self.pipelines:
                self.pipelines[stream_key].close()
                del self.pipelines[stream_key]

            self.logger.info(f"Removed camera {stream_key}")
            return True
        except Exception as e:
            self.logger.error(f"Error removing camera {stream_key}: {e}")
            return False

    def _send_response(self, cmd_type: str, stream_key: str, success: bool, error: str = None):
        """Send response back to manager."""
        if self.response_queue:
            try:
                self.response_queue.put_nowait({
                    'worker_id': self.worker_id,
                    'command_type': cmd_type,
                    'stream_key': stream_key,
                    'success': success,
                    'error': error,
                    'timestamp': time.time()
                })
            except Exception:
                pass

    async def _shutdown(self):
        """Gracefully shutdown worker."""
        self.logger.info(f"Worker {self.worker_id}: Starting shutdown")

        # Cancel all camera tasks
        for stream_key, task in self.camera_tasks.items():
            if not task.done():
                task.cancel()

        if self.camera_tasks:
            await asyncio.gather(*self.camera_tasks.values(), return_exceptions=True)

        # Close all pipelines
        for stream_key, pipeline in list(self.pipelines.items()):
            pipeline.close()
        self.pipelines.clear()

        # Cleanup SHM buffers
        if self.use_shm:
            for camera_id, shm_buffer in list(self._shm_buffers.items()):
                try:
                    shm_buffer.close()
                except Exception:
                    pass
            self._shm_buffers.clear()

        # Close Redis client
        if self.redis_client:
            await self.redis_client.close()

        # Shutdown executor
        self.executor.shutdown(wait=True, cancel_futures=False)

        self._report_health("stopped")
        self.logger.info(f"Worker {self.worker_id}: Shutdown complete")

    def _report_health(self, status: str, active_cameras: int = 0, error: Optional[str] = None):
        """Report health status to main process."""
        try:
            proc_cpu = 0
            proc_memory_mb = 0
            try:
                proc_cpu = self._process_info.cpu_percent(interval=None)
                proc_memory_mb = self._process_info.memory_info().rss / 1024 / 1024
            except Exception:
                pass

            avg_encoding_ms = 0
            if self._encoding_times:
                avg_encoding_ms = sum(self._encoding_times) / len(self._encoding_times) * 1000

            health_report = {
                'worker_id': self.worker_id,
                'status': status,
                'active_cameras': active_cameras,
                'timestamp': time.time(),
                'error': error,
                'metrics': {
                    'cpu_percent': proc_cpu,
                    'memory_mb': proc_memory_mb,
                    'frames_encoded': self._frames_encoded,
                    'encoding_errors': self._encoding_errors,
                    'avg_encoding_ms': avg_encoding_ms,
                    'pinned_cores': self.pinned_cores,
                    'backend': 'ffmpeg',
                },
            }
            self.health_queue.put_nowait(health_report)
        except Exception:
            pass

    def _log_metrics(self) -> None:
        """Log periodic metrics summary for all cameras."""
        current_time = time.time()
        elapsed = current_time - self._last_fps_check_time
        if elapsed <= 0:
            return

        # Calculate total FPS across all cameras
        total_frames = sum(self._frames_per_camera.values())
        total_fps = total_frames / elapsed if elapsed > 0 else 0
        num_active = len(self._frames_per_camera)
        avg_fps_per_camera = total_fps / num_active if num_active > 0 else 0

        # Get timing stats
        avg_encoding_ms = 0
        if self._encoding_times:
            avg_encoding_ms = sum(self._encoding_times) / len(self._encoding_times) * 1000

        avg_frame_ms = 0
        if self._frame_times:
            avg_frame_ms = sum(self._frame_times) / len(self._frame_times) * 1000

        # Get process stats
        try:
            cpu_percent = self._process_info.cpu_percent(interval=None)
            memory_mb = self._process_info.memory_info().rss / 1024 / 1024
        except Exception:
            cpu_percent = 0
            memory_mb = 0

        # Log summary
        mode_str = "SHM" if self.use_shm else "JPEG"
        self.logger.info(
            f"Worker {self.worker_id} metrics ({mode_str}): "
            f"cameras={num_active}, total_fps={total_fps:.1f}, avg_fps={avg_fps_per_camera:.1f}, "
            f"avg_encode={avg_encoding_ms:.1f}ms, avg_frame={avg_frame_ms:.1f}ms, "
            f"cpu={cpu_percent:.1f}%, mem={memory_mb:.0f}MB"
        )

        # Reset per-camera frame counters
        self._frames_per_camera.clear()
        self._last_fps_check_time = current_time
        self._last_metrics_log = current_time


def run_ffmpeg_worker(
    worker_id: int,
    camera_configs: List[Dict[str, Any]],
    stream_config: Dict[str, Any],
    stop_event: multiprocessing.Event,
    health_queue: multiprocessing.Queue,
    command_queue: multiprocessing.Queue = None,
    response_queue: multiprocessing.Queue = None,
    ffmpeg_config_dict: Optional[Dict[str, Any]] = None,
    use_shm: bool = False,
    shm_slot_count: int = 1000,
    shm_frame_format: str = "BGR",
    pin_cpu_affinity: bool = True,
    total_workers: int = 1,
    frame_optimizer_enabled: bool = True,
    frame_optimizer_config: Optional[Dict[str, Any]] = None,
):
    """Entry point for FFmpeg worker process.

    Args:
        worker_id: Worker identifier
        camera_configs: List of camera configurations
        stream_config: Streaming configuration
        stop_event: Shutdown event
        health_queue: Health reporting queue
        command_queue: Queue for receiving dynamic camera commands
        response_queue: Queue for sending command responses
        ffmpeg_config_dict: FFmpeg configuration as dict
        use_shm: Enable SHM mode
        shm_slot_count: Number of frame slots per camera ring buffer
        shm_frame_format: Frame format for SHM storage
        pin_cpu_affinity: Pin worker to specific CPU cores
        total_workers: Total number of workers
        frame_optimizer_enabled: Enable frame optimizer
        frame_optimizer_config: Frame optimizer configuration dict
    """
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(asctime)s - FFmpegWorker-{worker_id} - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(f"AsyncFFmpegWorker-{worker_id}")
    logger.info(f"Starting FFmpeg worker {worker_id}")

    # Create FFmpeg config from dict
    ffmpeg_config = None
    if ffmpeg_config_dict:
        ffmpeg_config = FFmpegConfig(**ffmpeg_config_dict)

    try:
        worker = AsyncFFmpegWorker(
            worker_id=worker_id,
            camera_configs=camera_configs,
            stream_config=stream_config,
            stop_event=stop_event,
            health_queue=health_queue,
            command_queue=command_queue,
            response_queue=response_queue,
            ffmpeg_config=ffmpeg_config,
            use_shm=use_shm,
            shm_slot_count=shm_slot_count,
            shm_frame_format=shm_frame_format,
            pin_cpu_affinity=pin_cpu_affinity,
            total_workers=total_workers,
            frame_optimizer_enabled=frame_optimizer_enabled,
            frame_optimizer_config=frame_optimizer_config,
        )

        asyncio.run(worker.run())

    except Exception as e:
        logger.error(f"Worker {worker_id} failed: {e}", exc_info=True)
        raise
