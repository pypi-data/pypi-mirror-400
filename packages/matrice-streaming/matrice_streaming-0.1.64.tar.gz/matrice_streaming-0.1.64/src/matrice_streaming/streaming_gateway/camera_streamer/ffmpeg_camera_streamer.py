"""FFmpeg-based camera streamer for high-performance video ingestion.

This module implements a drop-in replacement for CameraStreamer using
FFmpeg subprocess pipes instead of OpenCV. Key advantages:
- No OpenCV wrapper overhead
- No Python ↔ C per-frame calls
- Fewer memory copies
- Better FFmpeg scheduling
- Decoder threads isolated from Python GIL
"""
import asyncio
import logging
import subprocess
import signal
import time
import threading
import os
import sys
from typing import Dict, Any, Optional, List, Union, Tuple
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from collections import deque

import numpy as np
import cv2
import psutil

from matrice_common.optimize import FrameOptimizer
from matrice_common.stream.shm_ring_buffer import ShmRingBuffer

from .ffmpeg_config import FFmpegConfig, is_ffmpeg_available, detect_hwaccel


class FFmpegPipeline:
    """FFmpeg subprocess-based frame capture pipeline.

    This class manages an FFmpeg subprocess that decodes video and outputs
    raw frames via stdout pipe. It provides both sync and async interfaces.
    """

    def __init__(
        self,
        source: str,
        width: int,
        height: int,
        config: Optional[FFmpegConfig] = None,
        stream_key: str = "default",
    ):
        """Initialize FFmpeg pipeline.

        Args:
            source: Video source (file path, RTSP URL, HTTP URL, device)
            width: Frame width (0 = auto-detect from source)
            height: Frame height (0 = auto-detect from source)
            config: FFmpeg configuration options
            stream_key: Stream identifier for logging
        """
        self.source = source
        self.config = config or FFmpegConfig()
        self.stream_key = stream_key
        self.logger = logging.getLogger(f"FFmpegPipeline-{stream_key}")

        # Get source dimensions if not specified
        if width == 0 or height == 0:
            detected_width, detected_height = self._detect_dimensions(source)
            width = width or detected_width
            height = height or detected_height

        # Apply downscale if configured
        if self.config.output_width > 0:
            width = self.config.output_width
        if self.config.output_height > 0:
            height = self.config.output_height

        self.width = width
        self.height = height

        # Calculate frame size based on pixel format
        self.bytes_per_pixel = self._get_bytes_per_pixel(self.config.pixel_format)
        self.frame_size = width * height * self.bytes_per_pixel

        # Process state
        self.proc: Optional[subprocess.Popen] = None
        self.is_running = False
        self._restart_count = 0
        self._last_frame_time = 0.0

        # Metrics
        self.frames_read = 0
        self.frames_dropped = 0
        self.errors = 0
        self.bytes_read = 0
        self.latencies: deque = deque(maxlen=1000)

        # Start the pipeline
        self._start()

    def _get_bytes_per_pixel(self, pixel_format: str) -> int:
        """Get bytes per pixel for the given format."""
        formats = {
            "bgr24": 3,
            "rgb24": 3,
            "nv12": 1.5,  # Y plane + UV interleaved
            "gray": 1,
        }
        return int(formats.get(pixel_format, 3))

    def _detect_dimensions(self, source: str) -> Tuple[int, int]:
        """Detect video dimensions using ffprobe.

        Args:
            source: Video source

        Returns:
            Tuple of (width, height), defaults to (640, 480) on failure
        """
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "csv=p=0",
                source
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                parts = result.stdout.strip().split(",")
                if len(parts) >= 2:
                    return int(parts[0]), int(parts[1])
        except Exception as e:
            self.logger.warning(f"Failed to detect dimensions: {e}")

        return 640, 480  # Default fallback

    def _start(self):
        """Start the FFmpeg subprocess."""
        if self.proc is not None:
            self._stop()

        # Build command
        cmd = self.config.to_ffmpeg_args(
            self.source, self.width, self.height
        )

        self.logger.info(f"Starting FFmpeg pipeline: {' '.join(cmd[:10])}...")

        try:
            self.proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=self.frame_size * self.config.buffer_frames,
            )
            self.is_running = True
            self._restart_count += 1
            self.logger.info(
                f"FFmpeg pipeline started (PID: {self.proc.pid}, "
                f"frame_size: {self.frame_size}, restart: {self._restart_count})"
            )
        except Exception as e:
            self.logger.error(f"Failed to start FFmpeg: {e}")
            self.is_running = False
            raise

    def _stop(self):
        """Stop the FFmpeg subprocess gracefully."""
        if self.proc is None:
            return

        try:
            # Close stdout first to signal EOF
            if self.proc.stdout:
                self.proc.stdout.close()

            # Try graceful termination
            self.proc.terminate()
            try:
                self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=1)

            self.logger.info(f"FFmpeg pipeline stopped (PID: {self.proc.pid})")
        except Exception as e:
            self.logger.warning(f"Error stopping FFmpeg: {e}")
            try:
                self.proc.kill()
            except Exception:
                pass
        finally:
            self.proc = None
            self.is_running = False

    def read_frame(self) -> Optional[np.ndarray]:
        """Read one raw frame from FFmpeg pipe (blocking).

        Returns:
            numpy array of shape (height, width, 3) or None if failed
        """
        if self.proc is None or self.proc.poll() is not None:
            self.is_running = False
            return None

        start_time = time.time()

        try:
            data = self.proc.stdout.read(self.frame_size)

            if len(data) != self.frame_size:
                self.frames_dropped += 1
                self.logger.debug(f"Incomplete frame: got {len(data)}, expected {self.frame_size}")
                return None

            # Convert to numpy array
            frame = np.frombuffer(data, dtype=np.uint8)
            frame = frame.reshape((self.height, self.width, self.bytes_per_pixel))

            # Record metrics
            self.frames_read += 1
            self.bytes_read += len(data)
            latency = time.time() - start_time
            self.latencies.append(latency)
            self._last_frame_time = time.time()

            return frame

        except Exception as e:
            self.errors += 1
            self.logger.error(f"Error reading frame: {e}")
            return None

    async def read_frame_async(
        self,
        executor: Optional[ThreadPoolExecutor] = None
    ) -> Optional[np.ndarray]:
        """Read frame asynchronously using executor.

        Args:
            executor: Thread pool executor (uses default if None)

        Returns:
            numpy array or None if failed
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, self.read_frame)

    def restart(self) -> bool:
        """Restart the FFmpeg pipeline.

        Returns:
            True if restart succeeded
        """
        try:
            self._stop()
            time.sleep(self.config.reconnect_delay)
            self._start()
            return True
        except Exception as e:
            self.logger.error(f"Failed to restart pipeline: {e}")
            return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get pipeline metrics.

        Returns:
            Dictionary of metrics
        """
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        return {
            "frames_read": self.frames_read,
            "frames_dropped": self.frames_dropped,
            "errors": self.errors,
            "bytes_read": self.bytes_read,
            "restart_count": self._restart_count,
            "is_running": self.is_running,
            "avg_latency_ms": avg_latency * 1000,
            "width": self.width,
            "height": self.height,
            "frame_size": self.frame_size,
        }

    def close(self):
        """Close the pipeline and release resources."""
        self._stop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class FFmpegCameraStreamer:
    """FFmpeg-based camera streamer with same API as CameraStreamer.

    This class provides a drop-in replacement for CameraStreamer using
    FFmpeg subprocess pipelines for video ingestion. It supports:
    - Background streaming to Redis/Kafka
    - Dynamic camera add/remove/update
    - Frame optimization (similarity detection)
    - SHM mode for raw frame sharing
    """

    def __init__(
        self,
        session,
        service_id: str,
        server_type: str = "redis",
        video_codec: Optional[str] = None,
        gateway_util=None,
        ffmpeg_config: Optional[FFmpegConfig] = None,
        # SHM mode options
        use_shm: bool = False,
        shm_slot_count: int = 1000,
        shm_frame_format: str = "BGR",
        # Frame optimizer options
        frame_optimizer_enabled: bool = True,
        frame_optimizer_config: Optional[Dict[str, Any]] = None,
        # CPU affinity options
        pin_cpu_affinity: bool = False,
        cpu_affinity_core: Optional[int] = None,
    ):
        """Initialize FFmpeg camera streamer.

        Args:
            session: Session object for authentication
            service_id: Service identifier
            server_type: Backend type (redis or kafka)
            video_codec: Video codec (h264 or h265)
            gateway_util: Gateway utility for API interactions
            ffmpeg_config: FFmpeg configuration
            use_shm: Enable SHM mode for raw frame sharing
            shm_slot_count: Number of frame slots per camera ring buffer
            shm_frame_format: Frame format for SHM storage ("BGR", "RGB", or "NV12")
            frame_optimizer_enabled: Enable frame optimizer for skipping similar frames
            frame_optimizer_config: Frame optimizer configuration dict
            pin_cpu_affinity: Pin process to specific CPU core
            cpu_affinity_core: CPU core to pin to (None = auto-assign)
        """
        self.session = session
        self.service_id = service_id
        self.server_type = server_type
        self.video_codec = video_codec
        self.gateway_util = gateway_util
        self.ffmpeg_config = ffmpeg_config or FFmpegConfig()

        self.logger = logging.getLogger("FFmpegCameraStreamer")

        # Validate FFmpeg availability
        if not is_ffmpeg_available():
            raise RuntimeError("FFmpeg is not available on this system")

        # Auto-detect hardware acceleration if set to auto
        if self.ffmpeg_config.hwaccel == "auto":
            self.ffmpeg_config.hwaccel = detect_hwaccel()
            self.logger.info(f"Auto-detected hwaccel: {self.ffmpeg_config.hwaccel}")

        # Stream management
        self.pipelines: Dict[str, FFmpegPipeline] = {}
        self.streaming_threads: List[threading.Thread] = []
        self._stop_streaming = False
        self._stream_lock = threading.RLock()

        # Topic registration
        self.stream_topics: Dict[str, str] = {}  # stream_key -> topic
        self._setup_topics: set = set()

        # Statistics
        self._transmission_stats = {
            "total_frames": 0,
            "total_bytes": 0,
            "start_time": None,
        }

        # MatriceStream client
        self.stream_client = None

        # ================================================================
        # SHM Mode Configuration
        # ================================================================
        self.use_shm = use_shm
        self.shm_slot_count = shm_slot_count
        self.shm_frame_format = shm_frame_format
        self._shm_buffers: Dict[str, ShmRingBuffer] = {}
        self._last_shm_frame_idx: Dict[str, int] = {}

        # Register signal handlers for SHM cleanup
        if use_shm:
            self._setup_signal_handlers()
            self.logger.info(
                f"SHM mode ENABLED: format={shm_frame_format}, slots={shm_slot_count}"
            )

        # ================================================================
        # Frame Optimizer Configuration
        # ================================================================
        frame_optimizer_config = frame_optimizer_config or {}
        self.frame_optimizer = FrameOptimizer(
            enabled=frame_optimizer_enabled,
            scale=frame_optimizer_config.get("scale", 0.4),
            diff_threshold=frame_optimizer_config.get("diff_threshold", 15),
            similarity_threshold=frame_optimizer_config.get("similarity_threshold", 0.05),
            bg_update_interval=frame_optimizer_config.get("bg_update_interval", 10),
        )
        self._last_sent_frame_ids: Dict[str, str] = {}

        # ================================================================
        # CPU Affinity Configuration
        # ================================================================
        self.pin_cpu_affinity = pin_cpu_affinity
        self.cpu_affinity_core = cpu_affinity_core
        self.pinned_cores: Optional[List[int]] = None

        if pin_cpu_affinity:
            self._apply_cpu_affinity()

        self.logger.info(
            f"FFmpegCameraStreamer initialized: "
            f"hwaccel={self.ffmpeg_config.hwaccel}, "
            f"pixel_format={self.ffmpeg_config.pixel_format}, "
            f"shm={use_shm}, optimizer={frame_optimizer_enabled}"
        )

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful SHM cleanup on termination."""
        def cleanup_handler(signum, frame):
            """Handle SIGTERM/SIGINT for graceful SHM cleanup."""
            sig_name = signal.Signals(signum).name if hasattr(signal.Signals, 'name') else str(signum)
            self.logger.info(f"Received {sig_name}, cleaning up SHM buffers...")
            self._cleanup_shm_buffers()
            # Re-raise the signal to allow normal termination
            signal.signal(signum, signal.SIG_DFL)
            os.kill(os.getpid(), signum)

        # Register signal handlers
        signal.signal(signal.SIGINT, cleanup_handler)
        if sys.platform != 'win32':
            signal.signal(signal.SIGTERM, cleanup_handler)

        # Also register atexit handler
        import atexit
        atexit.register(self._cleanup_shm_buffers)

    def _cleanup_shm_buffers(self):
        """Cleanup all SHM buffers."""
        for camera_id, shm_buffer in list(self._shm_buffers.items()):
            try:
                shm_buffer.close()
                self.logger.info(f"Closed SHM buffer for {camera_id}")
            except Exception as e:
                self.logger.warning(f"Failed to cleanup SHM {camera_id}: {e}")
        self._shm_buffers.clear()

    def _apply_cpu_affinity(self):
        """Apply CPU affinity pinning."""
        try:
            p = psutil.Process()
            if self.cpu_affinity_core is not None:
                # Pin to specific core
                self.pinned_cores = [self.cpu_affinity_core]
            else:
                # Auto-assign to first available core
                cpu_count = psutil.cpu_count(logical=True)
                self.pinned_cores = [0] if cpu_count > 0 else None

            if self.pinned_cores:
                p.cpu_affinity(self.pinned_cores)
                self.logger.info(f"CPU affinity pinned to cores: {self.pinned_cores}")
        except Exception as e:
            self.logger.warning(f"Failed to set CPU affinity: {e}")
            self.pinned_cores = None

    def _get_or_create_shm_buffer(
        self, stream_key: str, width: int, height: int
    ) -> ShmRingBuffer:
        """Get existing or create new SHM buffer for stream.

        Args:
            stream_key: Stream identifier
            width: Frame width
            height: Frame height

        Returns:
            ShmRingBuffer instance for this stream
        """
        if stream_key not in self._shm_buffers:
            format_map = {
                "BGR": ShmRingBuffer.FORMAT_BGR,
                "RGB": ShmRingBuffer.FORMAT_RGB,
                "NV12": ShmRingBuffer.FORMAT_NV12,
            }
            frame_format = format_map.get(self.shm_frame_format, ShmRingBuffer.FORMAT_BGR)

            self._shm_buffers[stream_key] = ShmRingBuffer(
                camera_id=stream_key,
                width=width,
                height=height,
                frame_format=frame_format,
                slot_count=self.shm_slot_count,
                create=True,
            )
            self.logger.info(
                f"Created SHM buffer for {stream_key}: "
                f"{width}x{height} {self.shm_frame_format}, {self.shm_slot_count} slots"
            )
        return self._shm_buffers[stream_key]

    def register_stream_topic(self, stream_key: str, topic: str):
        """Register a topic for a stream.

        Args:
            stream_key: Stream identifier
            topic: Topic name for this stream
        """
        with self._stream_lock:
            self.stream_topics[stream_key] = topic
            self.logger.debug(f"Registered topic {topic} for stream {stream_key}")

    def setup_stream_for_topic(self, topic: str):
        """Setup stream for a topic (create topic if needed).

        Args:
            topic: Topic name to setup
        """
        with self._stream_lock:
            if topic in self._setup_topics:
                return

            # Initialize stream client if needed
            if self.stream_client is None:
                self._init_stream_client()

            self._setup_topics.add(topic)
            self.logger.debug(f"Setup topic: {topic}")

    def _init_stream_client(self):
        """Initialize the MatriceStream client."""
        try:
            from matrice_common.stream import MatriceStream, StreamType

            # Get connection info from gateway util
            if self.gateway_util:
                conn_info = self.gateway_util.get_and_wait_for_connection_info()
            else:
                conn_info = {}

            # Create MatriceStream
            stream_type = StreamType.REDIS if self.server_type == "redis" else StreamType.KAFKA
            self.stream_client = MatriceStream(
                stream_type=stream_type,
                **conn_info
            )

            self.logger.info("MatriceStream client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize stream client: {e}")
            raise

    def start_background_stream(
        self,
        input: Union[str, int],
        fps: int = 30,
        stream_key: str = "default",
        stream_group_key: str = "default",
        quality: int = 90,
        width: Optional[int] = None,
        height: Optional[int] = None,
        simulate_video_file_stream: bool = False,
        camera_location: str = "Unknown",
    ) -> bool:
        """Start background streaming for a camera.

        Args:
            input: Video source (file path, URL, or device ID)
            fps: Target FPS
            stream_key: Unique stream identifier
            stream_group_key: Stream group identifier
            quality: JPEG quality (1-100)
            width: Target width (None = use source)
            height: Target height (None = use source)
            simulate_video_file_stream: Loop video files
            camera_location: Camera location description

        Returns:
            True if stream started successfully
        """
        with self._stream_lock:
            if stream_key in self.pipelines:
                self.logger.warning(f"Stream {stream_key} already exists")
                return False

            try:
                # Create FFmpeg config for this stream
                stream_config = FFmpegConfig(
                    hwaccel=self.ffmpeg_config.hwaccel,
                    pixel_format=self.ffmpeg_config.pixel_format,
                    low_latency=self.ffmpeg_config.low_latency,
                    loop=simulate_video_file_stream,
                    realtime=not simulate_video_file_stream,
                    output_width=width or 0,
                    output_height=height or 0,
                    quality=quality,
                )

                # Convert device ID to string if needed
                source = str(input) if isinstance(input, int) else input

                # Create pipeline
                pipeline = FFmpegPipeline(
                    source=source,
                    width=width or 0,
                    height=height or 0,
                    config=stream_config,
                    stream_key=stream_key,
                )
                self.pipelines[stream_key] = pipeline

                # Start streaming thread
                thread = threading.Thread(
                    target=self._stream_loop,
                    args=(stream_key, stream_group_key, fps, quality, camera_location),
                    name=f"FFmpegStream-{stream_key}",
                    daemon=True,
                )
                self.streaming_threads.append(thread)
                thread.start()

                if self._transmission_stats["start_time"] is None:
                    self._transmission_stats["start_time"] = time.time()

                self.logger.info(
                    f"Started FFmpeg stream: {stream_key} from {source} "
                    f"({pipeline.width}x{pipeline.height} @ {fps} FPS)"
                )
                return True

            except Exception as e:
                self.logger.error(f"Failed to start stream {stream_key}: {e}")
                return False

    def _stream_loop(
        self,
        stream_key: str,
        stream_group_key: str,
        fps: int,
        quality: int,
        camera_location: str,
    ):
        """Main streaming loop for a camera (runs in thread).

        Args:
            stream_key: Stream identifier
            stream_group_key: Stream group identifier
            fps: Target FPS
            quality: JPEG quality
            camera_location: Camera location
        """
        pipeline = self.pipelines.get(stream_key)
        if not pipeline:
            return

        topic = self.stream_topics.get(stream_key, f"{stream_key}_topic")
        frame_interval = 1.0 / fps
        frame_counter = 0

        self.logger.info(f"Stream loop started for {stream_key}")

        while not self._stop_streaming:
            loop_start = time.time()

            try:
                # Read frame from FFmpeg pipeline
                frame = pipeline.read_frame()

                if frame is None:
                    if not self._stop_streaming:
                        # Try to restart pipeline
                        self.logger.warning(f"No frame from {stream_key}, restarting...")
                        if not pipeline.restart():
                            time.sleep(1.0)
                    continue

                frame_counter += 1

                # ================================================================
                # SHM Mode vs JPEG Mode
                # ================================================================
                if self.use_shm:
                    self._process_frame_shm_mode(
                        frame=frame,
                        stream_key=stream_key,
                        stream_group_key=stream_group_key,
                        topic=topic,
                        width=pipeline.width,
                        height=pipeline.height,
                        frame_counter=frame_counter,
                        camera_location=camera_location,
                    )
                else:
                    self._process_frame_jpeg_mode(
                        frame=frame,
                        stream_key=stream_key,
                        stream_group_key=stream_group_key,
                        topic=topic,
                        width=pipeline.width,
                        height=pipeline.height,
                        quality=quality,
                        frame_counter=frame_counter,
                        camera_location=camera_location,
                    )

                # Maintain target FPS
                elapsed = time.time() - loop_start
                sleep_time = max(0, frame_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            except Exception as e:
                self.logger.error(f"Error in stream loop {stream_key}: {e}")
                time.sleep(0.1)

        self.logger.info(f"Stream loop stopped for {stream_key}")

    def _process_frame_jpeg_mode(
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
    ):
        """Process frame in JPEG mode with frame optimizer.

        Args:
            frame: Raw frame from FFmpeg
            stream_key: Stream identifier
            stream_group_key: Stream group identifier
            topic: Topic name
            width: Frame width
            height: Frame height
            quality: JPEG quality
            frame_counter: Current frame number
            camera_location: Camera location
        """
        # Check frame similarity BEFORE encoding
        is_similar, similarity_score = self.frame_optimizer.is_similar(frame, stream_key)
        reference_frame_id = self._last_sent_frame_ids.get(stream_key)

        import uuid

        if is_similar and reference_frame_id:
            # Frame is similar - send cached reference
            message = {
                "frame_id": str(uuid.uuid4()),
                "input_name": stream_key,
                "input_stream": {
                    "content": b"",  # Empty for cached frame
                    "metadata": {
                        "width": width,
                        "height": height,
                        "frame_count": frame_counter,
                        "camera_location": camera_location,
                        "stream_group_key": stream_group_key,
                        "encoding_type": "cached",
                        "codec": "cached",
                        "timestamp": time.time(),
                        "similarity_score": similarity_score,
                        "cached_frame_id": reference_frame_id,
                    },
                },
            }

            if self.stream_client:
                try:
                    self.stream_client.add_message(topic, message, key=stream_key)
                    self._transmission_stats["total_frames"] += 1
                except Exception as e:
                    self.logger.error(f"Failed to send cached frame: {e}")
            return

        # Frame is different - encode and send full frame
        success, jpeg_buffer = cv2.imencode(
            '.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        )

        if not success:
            self.logger.warning(f"JPEG encode failed for {stream_key}")
            return

        frame_data = bytes(jpeg_buffer)

        # Build and send message
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
                    "timestamp": time.time(),
                },
            },
        }

        if self.stream_client:
            try:
                self.stream_client.add_message(topic, message, key=stream_key)
                self._transmission_stats["total_frames"] += 1
                self._transmission_stats["total_bytes"] += len(frame_data)

                # Track this frame_id for future references
                self._last_sent_frame_ids[stream_key] = new_frame_id
                self.frame_optimizer.set_last_frame_id(stream_key, new_frame_id)
            except Exception as e:
                self.logger.error(f"Failed to send frame: {e}")

    def _process_frame_shm_mode(
        self,
        frame: np.ndarray,
        stream_key: str,
        stream_group_key: str,
        topic: str,
        width: int,
        height: int,
        frame_counter: int,
        camera_location: str,
    ):
        """Process frame in SHM mode - write raw frame to SHM, metadata to Redis.

        Args:
            frame: Raw frame from FFmpeg (BGR format)
            stream_key: Stream identifier
            stream_group_key: Stream group identifier
            topic: Topic name
            width: Frame width
            height: Frame height
            frame_counter: Current frame number
            camera_location: Camera location
        """
        # Check frame similarity BEFORE writing to SHM
        is_similar, similarity_score = self.frame_optimizer.is_similar(frame, stream_key)
        reference_frame_idx = self._last_shm_frame_idx.get(stream_key)

        if is_similar and reference_frame_idx is not None:
            # Frame is similar - send metadata with reference to previous frame
            ts_ns = int(time.time() * 1e9)
            shm_buffer = self._shm_buffers.get(stream_key)

            if self.stream_client:
                try:
                    self.stream_client.add_shm_metadata(
                        stream_name=topic,
                        cam_id=stream_key,
                        shm_name=shm_buffer.shm_name if shm_buffer else "",
                        frame_idx=reference_frame_idx,
                        slot=None,
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
                    self._transmission_stats["total_frames"] += 1
                except Exception as e:
                    self.logger.error(f"Failed to send SHM metadata: {e}")
            return

        # Frame is different - write to SHM
        shm_buffer = self._get_or_create_shm_buffer(stream_key, width, height)

        # Convert frame to target format
        if self.shm_frame_format == "RGB":
            raw_bytes = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).tobytes()
        elif self.shm_frame_format == "NV12":
            from matrice_common.stream.shm_ring_buffer import bgr_to_nv12
            raw_bytes = bgr_to_nv12(frame)
        else:  # BGR default
            raw_bytes = frame.tobytes()

        # Write to SHM ring buffer
        frame_idx, slot = shm_buffer.write_frame(raw_bytes)
        self._last_shm_frame_idx[stream_key] = frame_idx

        # Send metadata to stream backend
        ts_ns = int(time.time() * 1e9)
        if self.stream_client:
            try:
                self.stream_client.add_shm_metadata(
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
                self._transmission_stats["total_frames"] += 1
                self._transmission_stats["total_bytes"] += len(raw_bytes)
            except Exception as e:
                self.logger.error(f"Failed to send SHM metadata: {e}")

    def _build_message(
        self,
        frame_data: bytes,
        stream_key: str,
        stream_group_key: str,
        width: int,
        height: int,
        frame_counter: int,
        camera_location: str,
    ) -> Dict[str, Any]:
        """Build a message for the stream backend.

        Args:
            frame_data: JPEG encoded frame
            stream_key: Stream identifier
            stream_group_key: Stream group identifier
            width: Frame width
            height: Frame height
            frame_counter: Current frame number
            camera_location: Camera location

        Returns:
            Message dictionary
        """
        import uuid

        return {
            "frame_id": str(uuid.uuid4()),
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
                    "codec": "h264",  # JPEG encoded
                    "timestamp": time.time(),
                },
            },
        }

    def stop_streaming(self, stream_key: Optional[str] = None):
        """Stop streaming for one or all cameras.

        Args:
            stream_key: Stream to stop (None = stop all)
        """
        with self._stream_lock:
            if stream_key:
                # Stop specific stream
                if stream_key in self.pipelines:
                    self.pipelines[stream_key].close()
                    del self.pipelines[stream_key]
                    self.logger.info(f"Stopped stream: {stream_key}")

                # Cleanup SHM buffer for this stream
                if stream_key in self._shm_buffers:
                    try:
                        self._shm_buffers[stream_key].close()
                        del self._shm_buffers[stream_key]
                        self.logger.info(f"Closed SHM buffer for {stream_key}")
                    except Exception as e:
                        self.logger.warning(f"Failed to close SHM buffer {stream_key}: {e}")
            else:
                # Stop all streams
                self._stop_streaming = True

                for key, pipeline in list(self.pipelines.items()):
                    pipeline.close()
                    self.logger.info(f"Stopped stream: {key}")

                self.pipelines.clear()

                # Wait for threads
                for thread in self.streaming_threads:
                    if thread.is_alive():
                        thread.join(timeout=5.0)

                self.streaming_threads.clear()

                # Cleanup all SHM buffers
                if self.use_shm:
                    self._cleanup_shm_buffers()

                self.logger.info("All FFmpeg streams stopped")

    def get_transmission_stats(self) -> Dict[str, Any]:
        """Get transmission statistics.

        Returns:
            Dictionary of statistics
        """
        with self._stream_lock:
            stats = self._transmission_stats.copy()
            stats["active_streams"] = len(self.pipelines)
            stats["pipeline_stats"] = {
                key: pipeline.get_metrics()
                for key, pipeline in self.pipelines.items()
            }

            if stats["start_time"]:
                elapsed = time.time() - stats["start_time"]
                stats["avg_fps"] = stats["total_frames"] / elapsed if elapsed > 0 else 0
                stats["throughput_mbps"] = (stats["total_bytes"] * 8 / 1_000_000) / elapsed if elapsed > 0 else 0

            return stats

    def reset_transmission_stats(self):
        """Reset transmission statistics."""
        with self._stream_lock:
            self._transmission_stats = {
                "total_frames": 0,
                "total_bytes": 0,
                "start_time": time.time() if self.pipelines else None,
            }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_streaming()
