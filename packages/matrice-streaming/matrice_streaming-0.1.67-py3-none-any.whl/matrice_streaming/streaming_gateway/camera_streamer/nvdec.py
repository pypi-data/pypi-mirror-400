#!/usr/bin/env python3
"""Streaming Gateway - CUDA IPC Video Producer (NVDEC Hardware Decode).

This module implements the producer side of the zero-copy video pipeline
using NVDEC hardware video decoding for maximum throughput.

Architecture:
=============

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                    STREAMING GATEWAY (Producer)                         │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │   ┌─────────────────────────────────────────────────────────────────┐   │
    │   │                   NVDEC Decoder Pool                            │   │
    │   │                                                                 │   │
    │   │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │   │
    │   │  │  Decoder 0     │  │  Decoder 1     │  │  Decoder N     │     │   │
    │   │  │                │  │                │  │                │     │   │
    │   │  │   NVDEC HW     │  │   NVDEC HW     │  │   NVDEC HW     │     │   │
    │   │  │   decode       │  │   decode       │  │   decode       │     │   │
    │   │  │       ↓        │  │       ↓        │  │       ↓        │     │   │
    │   │  │  NV12 Resize   │  │  NV12 Resize   │  │  NV12 Resize   │     │   │
    │   │  │       ↓        │  │       ↓        │  │       ↓        │     │   │
    │   │  │   CUDA IPC     │  │   CUDA IPC     │  │   CUDA IPC     │     │   │
    │   │  │   Ring Buf     │  │   Ring Buf     │  │   Ring Buf     │     │   │
    │   │  │  (NV12 0.6MB)  │  │  (NV12 0.6MB)  │  (NV12 0.6MB)     │     │   │
    │   │  └────────────────┘  └────────────────┘  └────────────────┘     │   │
    │   │                                                                 │   │
    │   └─────────────────────────────────────────────────────────────────┘   │
    │                               │                                         │
    │                    Output: NV12 (H*1.5, W) uint8 = 0.6 MB               │
    │                    50% less IPC bandwidth than RGB                      │
    │                               ↓                                         │
    └───────────────────────────────┼─────────────────────────────────────────┘
                                    │
                         Consumer reads via CUDA IPC
                         → NV12→RGB→CHW→FP16 in one kernel
                         → TensorRT inference

Usage:
======
    python streaming_gateway.py --video videoplayback.mp4 --num-streams 100

Requirements:
=============
    - PyNvVideoCodec for NVDEC hardware decode
    - CuPy with CUDA support
    - cuda_shm_ring_buffer module
"""

import argparse
import logging
import multiprocessing as mp
import os
import time
import threading
import queue as thread_queue
import hashlib
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse, urlunparse

import numpy as np

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False
    cp = None

try:
    import PyNvVideoCodec as nvc
    PYNVCODEC_AVAILABLE = True
except ImportError:
    PYNVCODEC_AVAILABLE = False
    nvc = None

try:
    from matrice_common.stream.cuda_shm_ring_buffer import CudaIpcRingBuffer, GlobalFrameCounter
    RING_BUFFER_AVAILABLE = True
except (ImportError, AttributeError, RuntimeError, TypeError):
    # ImportError: module not found
    # AttributeError: cp.ndarray is None (cupy not available)
    # RuntimeError/TypeError: other initialization errors
    RING_BUFFER_AVAILABLE = False
    CudaIpcRingBuffer = None
    GlobalFrameCounter = None

logger = logging.getLogger(__name__)

def setup_logging(quiet: bool = True):
    """Configure logging level based on quiet mode."""
    level = logging.WARNING if quiet else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.getLogger('cuda_shm_ring_buffer').setLevel(logging.WARNING if quiet else logging.INFO)


# =============================================================================
# Video Downloader for HTTPS URLs (PyNvVideoCodec's FFmpeg lacks HTTPS support)
# =============================================================================

class VideoDownloader:
    """Downloads and caches video files from HTTPS URLs.

    PyNvVideoCodec uses a bundled FFmpeg that doesn't have HTTPS support.
    This class downloads HTTPS videos to local files before passing them
    to the NVDEC demuxer.

    Features:
    - URL deduplication: same video URL (ignoring query params) is only downloaded once
    - Disk caching: reuses existing files across runs
    - Progress tracking for large files
    - Dynamic timeout based on file size
    """

    # Configuration
    DOWNLOAD_TIMEOUT = 300  # Base timeout in seconds
    DOWNLOAD_TIMEOUT_PER_100MB = 300  # Additional seconds per 100MB
    MAX_DOWNLOAD_TIMEOUT = 6000  # 100 minutes max
    DOWNLOAD_CHUNK_SIZE = 8192

    # Singleton instance for process-wide caching
    _instance: Optional['VideoDownloader'] = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern for process-wide cache sharing."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the video downloader."""
        if self._initialized:
            return

        self._initialized = True
        self.downloaded_files: Dict[str, str] = {}
        self._normalized_url_to_path: Dict[str, str] = {}
        self._download_lock = threading.Lock()
        self.temp_dir = Path(tempfile.gettempdir()) / "nvdec_video_cache"
        self.temp_dir.mkdir(exist_ok=True)
        logger.info(f"VideoDownloader initialized, cache dir: {self.temp_dir}")

    def prepare_source(self, video_path: str, camera_id: str) -> str:
        """Prepare video source, downloading HTTPS URLs if needed.

        Args:
            video_path: Video file path, RTSP URL, or HTTPS URL
            camera_id: Camera identifier for logging

        Returns:
            Local file path (downloaded if HTTPS) or original path
        """
        if not self._is_https_url(video_path):
            return video_path

        if not REQUESTS_AVAILABLE:
            logger.warning(f"requests module not available, cannot download HTTPS URL for {camera_id}")
            return video_path

        local_path = self._download_video(video_path, camera_id)
        if local_path:
            return local_path

        logger.warning(f"Failed to download {video_path} for {camera_id}, will try URL directly (may fail)")
        return video_path

    def _is_https_url(self, source: str) -> bool:
        """Check if source is an HTTPS URL."""
        return source.startswith('https://')

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by stripping query parameters for deduplication."""
        parsed = urlparse(url)
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            '', '', ''  # params, query, fragment
        ))

    def _get_url_hash(self, normalized_url: str) -> str:
        """Generate a short hash for consistent file naming."""
        return hashlib.md5(normalized_url.encode()).hexdigest()[:12]

    def _download_video(self, url: str, camera_id: str) -> Optional[str]:
        """Download video file from HTTPS URL with caching.

        Thread-safe: uses lock to prevent duplicate downloads.

        Args:
            url: HTTPS video URL
            camera_id: Camera identifier for logging

        Returns:
            Local file path or None if download failed
        """
        normalized_url = self._normalize_url(url)
        file_ext = Path(url.split('?')[0]).suffix or '.mp4'
        url_hash = self._get_url_hash(normalized_url)
        expected_path = self.temp_dir / f"video_{url_hash}{file_ext}"
        expected_path_str = str(expected_path)

        # Quick check: file already on disk
        if expected_path.exists():
            existing_size = expected_path.stat().st_size
            logger.info(
                f"[{camera_id}] Reusing cached video: {expected_path.name} "
                f"({existing_size / (1024*1024):.1f}MB)"
            )
            with self._download_lock:
                self.downloaded_files[url] = expected_path_str
                self._normalized_url_to_path[normalized_url] = expected_path_str
            return expected_path_str

        # Check memory cache
        with self._download_lock:
            if url in self.downloaded_files:
                local_path = self.downloaded_files[url]
                if os.path.exists(local_path):
                    logger.debug(f"[{camera_id}] Using cached path (exact URL match)")
                    return local_path

            if normalized_url in self._normalized_url_to_path:
                local_path = self._normalized_url_to_path[normalized_url]
                if os.path.exists(local_path):
                    logger.info(f"[{camera_id}] Reusing download (same base URL)")
                    self.downloaded_files[url] = local_path
                    return local_path

        # Need to download - acquire lock to prevent duplicate downloads
        with self._download_lock:
            # Double-check after acquiring lock
            if expected_path.exists():
                self.downloaded_files[url] = expected_path_str
                self._normalized_url_to_path[normalized_url] = expected_path_str
                return expected_path_str

            return self._do_download(url, expected_path, camera_id)

    def _do_download(self, url: str, dest_path: Path, camera_id: str) -> Optional[str]:
        """Perform the actual download. Must be called with _download_lock held."""
        content_length = 0
        file_size_mb = 0.0
        bytes_downloaded = 0
        timeout = self.DOWNLOAD_TIMEOUT

        try:
            # HEAD request to get file size
            try:
                head_response = requests.head(url, timeout=10, allow_redirects=True)
                content_length = int(head_response.headers.get('Content-Length', 0))
                file_size_mb = content_length / (1024 * 1024)
            except Exception as e:
                logger.debug(f"[{camera_id}] HEAD request failed: {e}")

            # Calculate dynamic timeout
            if content_length > 0:
                timeout = min(
                    self.DOWNLOAD_TIMEOUT + int(file_size_mb // 100) * self.DOWNLOAD_TIMEOUT_PER_100MB,
                    self.MAX_DOWNLOAD_TIMEOUT
                )
                logger.info(f"[{camera_id}] Downloading {file_size_mb:.1f}MB (timeout: {timeout}s)")
            else:
                logger.info(f"[{camera_id}] Downloading video (size unknown, timeout: {timeout}s)")

            # Download with progress tracking
            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()

            if content_length == 0:
                content_length = int(response.headers.get('Content-Length', 0))
                file_size_mb = content_length / (1024 * 1024) if content_length > 0 else 0

            last_progress_log = 0

            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=self.DOWNLOAD_CHUNK_SIZE):
                    f.write(chunk)
                    bytes_downloaded += len(chunk)

                    # Log progress every 50MB for large files
                    if content_length > 50_000_000:
                        mb_downloaded = bytes_downloaded // (1024 * 1024)
                        if mb_downloaded - last_progress_log >= 50:
                            progress = (bytes_downloaded / content_length * 100) if content_length else 0
                            logger.info(
                                f"[{camera_id}] Download progress: "
                                f"{mb_downloaded}MB / {file_size_mb:.0f}MB ({progress:.1f}%)"
                            )
                            last_progress_log = mb_downloaded

            # Update caches
            normalized_url = self._normalize_url(url)
            dest_path_str = str(dest_path)
            self.downloaded_files[url] = dest_path_str
            self._normalized_url_to_path[normalized_url] = dest_path_str

            logger.info(
                f"[{camera_id}] Downloaded: {dest_path.name} "
                f"({bytes_downloaded / (1024*1024):.1f}MB)"
            )
            return dest_path_str

        except requests.Timeout:
            logger.error(
                f"[{camera_id}] Download timeout: {file_size_mb:.1f}MB, "
                f"got {bytes_downloaded/(1024*1024):.1f}MB in {timeout}s"
            )
        except requests.HTTPError as e:
            logger.error(f"[{camera_id}] HTTP error: {e.response.status_code} - {e.response.reason}")
        except IOError as e:
            logger.error(f"[{camera_id}] Disk I/O error: {e}")
        except Exception as e:
            logger.error(f"[{camera_id}] Download failed: {type(e).__name__}: {e}")

        # Cleanup partial download
        try:
            if dest_path.exists():
                dest_path.unlink()
        except Exception:
            pass

        return None

    def cleanup(self):
        """Clean up downloaded temporary files."""
        unique_files = set(self.downloaded_files.values())
        unique_files.update(self._normalized_url_to_path.values())

        for filepath in unique_files:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    logger.debug(f"Removed temp file: {filepath}")
            except Exception as e:
                logger.warning(f"Failed to remove temp file {filepath}: {e}")

        self.downloaded_files.clear()
        self._normalized_url_to_path.clear()


# Global video downloader instance
_video_downloader: Optional[VideoDownloader] = None


def get_video_downloader() -> VideoDownloader:
    """Get or create the global VideoDownloader instance."""
    global _video_downloader
    if _video_downloader is None:
        _video_downloader = VideoDownloader()
    return _video_downloader


@dataclass
class StreamConfig:
    """Configuration for a single video stream."""
    camera_id: str
    video_path: str
    width: int = 640
    height: int = 640
    target_fps: int = 10
    gpu_id: int = 0


@dataclass
class GatewayConfig:
    """Configuration for the streaming gateway."""
    video_path: str
    num_streams: int = 100
    target_fps: int = 0  # 0 = unlimited, >0 = FPS limit per stream
    frame_width: int = 640
    frame_height: int = 640
    gpu_id: int = 0
    num_gpus: int = 1
    duration_sec: float = 30.0
    nvdec_pool_size: int = 8
    nvdec_burst_size: int = 4
    num_slots: int = 32


@dataclass
class StreamState:
    """Track state for each logical stream in NVDEC pool."""
    stream_id: int
    camera_id: str
    video_path: str
    demuxer: Any
    frames_decoded: int = 0
    width: int = 640
    height: int = 640
    empty_packets: int = 0


# =============================================================================
# CUDA Kernel: NV12 Resize (no color conversion - 50% less bandwidth)
# =============================================================================

_nv12_resize_kernel = None


def _get_nv12_resize_kernel():
    """Get or compile the NV12 resize kernel.

    This kernel resizes NV12 directly (no color conversion).
    Output: concatenated Y (H×W) + UV ((H/2)×W) = H×W×1.5 bytes
    This is 50% smaller than RGB (H×W×3 bytes).

    Consumer will do: NV12→RGB→CHW→FP16 in one fused kernel.
    """
    global _nv12_resize_kernel
    if _nv12_resize_kernel is None and CUPY_AVAILABLE:
        _nv12_resize_kernel = cp.RawKernel(r'''
extern "C" __global__ void nv12_resize(
    const unsigned char* src_y,    // Source Y plane
    const unsigned char* src_uv,   // Source UV plane (interleaved)
    unsigned char* dst,            // Output: Y (H×W) followed by UV ((H/2)×W)
    int src_h, int src_w,
    int dst_h, int dst_w,
    int y_stride, int uv_stride
) {
    int dst_x = blockIdx.x * blockDim.x + threadIdx.x;
    int dst_y = blockIdx.y * blockDim.y + threadIdx.y;

    // Total height in output: dst_h (Y) + dst_h/2 (UV) = dst_h * 1.5
    int total_h = dst_h + dst_h / 2;
    if (dst_x >= dst_w || dst_y >= total_h) return;

    float scale_x = (float)src_w / dst_w;
    float scale_y = (float)src_h / dst_h;

    if (dst_y < dst_h) {
        // Y plane region: resize Y
        int src_x = min((int)(dst_x * scale_x), src_w - 1);
        int src_y_coord = min((int)(dst_y * scale_y), src_h - 1);
        int src_idx = src_y_coord * y_stride + src_x;
        int dst_idx = dst_y * dst_w + dst_x;
        dst[dst_idx] = src_y[src_idx];
    } else {
        // UV plane region: resize UV (UV is at half vertical resolution)
        int uv_dst_y = dst_y - dst_h;  // 0 to dst_h/2-1
        int uv_src_y = min((int)(uv_dst_y * scale_y), src_h / 2 - 1);

        // UV is interleaved, so we copy pairs (U, V) together
        int src_uv_x = min((int)((dst_x / 2) * 2 * scale_x), src_w - 2);
        src_uv_x = (src_uv_x / 2) * 2;  // Ensure even

        int src_idx = uv_src_y * uv_stride + src_uv_x + (dst_x % 2);
        int dst_idx = dst_h * dst_w + uv_dst_y * dst_w + dst_x;
        dst[dst_idx] = src_uv[src_idx];
    }
}
''', 'nv12_resize')
    return _nv12_resize_kernel


def nv12_resize(y_plane: cp.ndarray, uv_plane: cp.ndarray,
                y_stride: int, uv_stride: int,
                src_h: int, src_w: int,
                dst_h: int = 640, dst_w: int = 640) -> cp.ndarray:
    """Resize NV12 without color conversion.

    Output: concatenated Y (H×W) + UV ((H/2)×W) as single buffer.
    Total size: H×W + (H/2)×W = H×W×1.5 bytes (50% of RGB).
    """
    kernel = _get_nv12_resize_kernel()
    if kernel is None:
        return None

    total_h = dst_h + dst_h // 2
    output = cp.empty((total_h, dst_w), dtype=cp.uint8)

    block = (16, 16)
    grid = ((dst_w + 15) // 16, (total_h + 15) // 16)

    kernel(grid, block, (
        y_plane, uv_plane, output,
        cp.int32(src_h), cp.int32(src_w),
        cp.int32(dst_h), cp.int32(dst_w),
        cp.int32(y_stride), cp.int32(uv_stride)
    ))

    return output


def surface_to_nv12(frame, target_h: int = 640, target_w: int = 640) -> Optional[cp.ndarray]:
    """Convert NVDEC surface to resized NV12 (50% smaller than RGB).

    Output: (H + H/2, W) uint8 - concatenated Y + UV planes.
    Total size: H×W×1.5 bytes (vs H×W×3 for RGB).
    """
    if not CUPY_AVAILABLE or frame is None:
        return None

    try:
        cuda_views = frame.cuda()
        if not cuda_views or len(cuda_views) < 2:
            return None

        # Extract Y plane
        y_view = cuda_views[0]
        y_cai = y_view.__cuda_array_interface__
        y_shape = tuple(y_cai['shape'])
        y_strides = tuple(y_cai['strides'])
        y_ptr = y_cai['data'][0]
        src_h, src_w = y_shape[:2]
        y_stride = y_strides[0]

        y_size = src_h * y_stride
        y_mem = cp.cuda.UnownedMemory(y_ptr, y_size, owner=frame)
        y_memptr = cp.cuda.MemoryPointer(y_mem, 0)
        y_plane = cp.ndarray((src_h, src_w), dtype=cp.uint8, memptr=y_memptr,
                            strides=(y_stride, 1))

        # Extract UV plane
        uv_view = cuda_views[1]
        uv_cai = uv_view.__cuda_array_interface__
        uv_shape = tuple(uv_cai['shape'])
        uv_strides = tuple(uv_cai['strides'])
        uv_ptr = uv_cai['data'][0]
        uv_stride = uv_strides[0]

        uv_h = uv_shape[0]
        uv_w = uv_shape[1] if len(uv_shape) > 1 else src_w
        uv_size = uv_h * uv_stride
        uv_mem = cp.cuda.UnownedMemory(uv_ptr, uv_size, owner=frame)
        uv_memptr = cp.cuda.MemoryPointer(uv_mem, 0)
        uv_plane = cp.ndarray((uv_h, uv_w), dtype=cp.uint8, memptr=uv_memptr,
                             strides=(uv_stride, 1))

        # NV12 resize (no color conversion - 50% smaller output!)
        nv12_frame = nv12_resize(y_plane, uv_plane, y_stride, uv_stride,
                                  src_h, src_w, target_h, target_w)
        # Add channel dimension for ring buffer compatibility: (H*1.5, W) -> (H*1.5, W, 1)
        return nv12_frame[:, :, cp.newaxis] if nv12_frame is not None else None

    except Exception as e:
        # Safely encode error message (some CUDA errors contain non-ASCII chars like '×')
        try:
            err_msg = str(e).encode('ascii', errors='replace').decode('ascii')
        except Exception:
            err_msg = "unknown error"
        logger.warning(f"surface_to_nv12 failed: {err_msg}")
        return None


# =============================================================================
# NVDEC Decoder Pool
# =============================================================================

class NVDECDecoderPool:
    """Pool of NVDEC decoders that time-multiplex streams.

    Each decoder is exclusively owned by one worker thread.
    Outputs NV12: 1.5×H×W bytes (50% smaller than RGB).
    """

    def __init__(self, pool_size: int, gpu_id: int = 0):
        self.pool_size = pool_size
        self.gpu_id = gpu_id
        self.decoders = []
        self.streams_per_decoder: List[List[StreamState]] = [[] for _ in range(pool_size)]

        if not PYNVCODEC_AVAILABLE:
            raise RuntimeError("PyNvVideoCodec not available")

        if CUPY_AVAILABLE:
            cp.cuda.Device(gpu_id).use()

        for i in range(pool_size):
            try:
                decoder = nvc.CreateDecoder(
                    gpuid=gpu_id,
                    codec=nvc.cudaVideoCodec.H264,
                    usedevicememory=True
                )
                self.decoders.append(decoder)
            except Exception as e:
                logger.warning(f"Failed to create decoder {i}: {e}")
                break

        self.actual_pool_size = len(self.decoders)
        logger.info(f"Created NVDEC pool: {self.actual_pool_size}/{pool_size} decoders on GPU {gpu_id}")

    def assign_stream(self, stream_id: int, camera_id: str, video_path: str,
                      width: int = 640, height: int = 640) -> bool:
        """Assign a stream to a decoder (round-robin).

        Automatically downloads HTTPS URLs to local files since PyNvVideoCodec's
        bundled FFmpeg doesn't support HTTPS protocol.
        """
        if self.actual_pool_size == 0:
            return False

        decoder_idx = stream_id % self.actual_pool_size

        # Download HTTPS URLs to local files (PyNvVideoCodec lacks HTTPS support)
        downloader = get_video_downloader()
        local_path = downloader.prepare_source(video_path, camera_id)

        try:
            demuxer = nvc.CreateDemuxer(local_path)
        except Exception as e:
            logger.error(f"Failed to create demuxer for {camera_id}: {e}")
            return False

        stream_state = StreamState(
            stream_id=stream_id,
            camera_id=camera_id,
            video_path=local_path,  # Store local path for video looping
            demuxer=demuxer,
            width=width,
            height=height
        )
        self.streams_per_decoder[decoder_idx].append(stream_state)
        return True

    def decode_round(self, decoder_idx: int, frames_per_stream: int = 4,
                     target_h: int = 640, target_w: int = 640) -> Tuple[int, List[Tuple[str, cp.ndarray]]]:
        """Decode frames and convert to NV12.

        Returns:
            (total_frames, [(camera_id, nv12_tensor), ...])
        """
        if decoder_idx >= self.actual_pool_size:
            return 0, []

        decoder = self.decoders[decoder_idx]
        streams = self.streams_per_decoder[decoder_idx]
        total_frames = 0
        decoded_frames = []

        for stream in streams:
            frames_this_stream = 0

            while frames_this_stream < frames_per_stream:
                try:
                    packet = stream.demuxer.Demux()
                    if packet is None:
                        stream.demuxer = nvc.CreateDemuxer(stream.video_path)
                        stream.empty_packets = 0
                        packet = stream.demuxer.Demux()
                        if packet is None:
                            break

                    frames_before = frames_this_stream
                    for surface in decoder.Decode(packet):
                        tensor = surface_to_nv12(surface, target_h, target_w)

                        if tensor is not None:
                            decoded_frames.append((stream.camera_id, tensor))
                            frames_this_stream += 1
                            stream.frames_decoded += 1
                            total_frames += 1
                            stream.empty_packets = 0

                        if frames_this_stream >= frames_per_stream:
                            break

                    if frames_this_stream == frames_before:
                        stream.empty_packets += 1
                        if stream.empty_packets >= 3:
                            stream.demuxer = nvc.CreateDemuxer(stream.video_path)
                            stream.empty_packets = 0

                except Exception:
                    break

                if frames_this_stream >= frames_per_stream:
                    break

        return total_frames, decoded_frames

    def get_camera_ids_for_decoder(self, decoder_idx: int) -> List[str]:
        """Get camera IDs for a decoder."""
        if decoder_idx >= self.actual_pool_size:
            return []
        return [s.camera_id for s in self.streams_per_decoder[decoder_idx]]

    def close(self):
        """Close all decoders."""
        self.decoders.clear()
        for streams in self.streams_per_decoder:
            streams.clear()


# =============================================================================
# Worker Thread
# =============================================================================

def nvdec_pool_worker(
    worker_id: int,
    decoder_idx: int,
    pool: NVDECDecoderPool,
    ring_buffers: Dict[str, CudaIpcRingBuffer],
    frame_counter: GlobalFrameCounter,
    duration_sec: float,
    result_queue: thread_queue.Queue,
    stop_event: threading.Event,
    burst_size: int = 4,
    target_h: int = 640,
    target_w: int = 640,
    target_fps: int = 0,
    shared_frame_count: Optional[mp.Value] = None,
    gpu_frame_count: Optional[mp.Value] = None,
):
    """NVDEC worker thread.

    Decodes frames and writes NV12 tensors to ring buffers.
    Uses dedicated CUDA stream per worker for kernel overlap.
    Supports FPS limiting when target_fps > 0.

    Args:
        shared_frame_count: Global counter (all GPUs)
        gpu_frame_count: Per-GPU counter (this GPU only)
    """
    if CUPY_AVAILABLE:
        cp.cuda.Device(pool.gpu_id).use()
        cuda_stream = cp.cuda.Stream(non_blocking=True)
    else:
        cuda_stream = None

    local_frames = 0
    local_errors = 0
    frames_since_counter_update = 0
    counter_batch_size = 100
    start_time = time.perf_counter()
    camera_ids = pool.get_camera_ids_for_decoder(decoder_idx)
    num_streams = len(camera_ids)

    # FPS limiting: calculate frames per second target for this worker
    # Each worker handles num_streams cameras at target_fps each
    fps_limit_enabled = target_fps > 0 and num_streams > 0
    if fps_limit_enabled:
        # Total target frames per second for all streams handled by this worker
        worker_target_fps = target_fps * num_streams
        frame_interval = 1.0 / worker_target_fps
        next_frame_time = start_time
        fps_mode = f", FPS limit={target_fps}/stream"
    else:
        frame_interval = 0
        next_frame_time = 0
        fps_mode = ", unlimited FPS"

    logger.debug(f"Worker {worker_id}: decoder={decoder_idx}, cams={num_streams}{fps_mode}")

    while not stop_event.is_set():
        if time.perf_counter() - start_time >= duration_sec:
            break

        # FPS limiting: wait until next scheduled frame time
        if fps_limit_enabled:
            current_time = time.perf_counter()
            if current_time < next_frame_time:
                sleep_time = next_frame_time - current_time
                if sleep_time > 0.0001:  # Only sleep if > 100us
                    time.sleep(sleep_time)

        try:
            with cuda_stream:
                num_frames, decoded_frames = pool.decode_round(
                    decoder_idx,
                    frames_per_stream=burst_size,
                    target_h=target_h,
                    target_w=target_w
                )

                for cam_id, tensor in decoded_frames:
                    if cam_id in ring_buffers:
                        try:
                            ring_buffers[cam_id].write_frame_fast(tensor, sync=False)
                            local_frames += 1
                            frames_since_counter_update += 1

                            # Update global counter (all GPUs)
                            if shared_frame_count is not None:
                                with shared_frame_count.get_lock():
                                    shared_frame_count.value += 1

                            # Update per-GPU counter (this GPU only)
                            if gpu_frame_count is not None:
                                with gpu_frame_count.get_lock():
                                    gpu_frame_count.value += 1

                            # Update next frame time for FPS limiting
                            if fps_limit_enabled:
                                next_frame_time += frame_interval

                        except Exception as e:
                            local_errors += 1
                            if local_errors <= 3:
                                logger.error(f"Worker {worker_id} write error: {e}")

                if decoded_frames and len(ring_buffers) > 0:
                    next(iter(ring_buffers.values())).sync_writes()

            if num_frames == 0:
                time.sleep(0.0001)
                continue

            if frames_since_counter_update >= counter_batch_size:
                frame_counter.increment()
                frames_since_counter_update = 0

        except Exception as e:
            local_errors += 1
            if local_errors <= 3:
                logger.error(f"Worker {worker_id} error: {e}")

    if frames_since_counter_update > 0:
        frame_counter.increment()

    elapsed = time.perf_counter() - start_time
    result_queue.put({
        "worker_id": worker_id,
        "decoder_idx": decoder_idx,
        "elapsed_sec": elapsed,
        "total_frames": local_frames,
        "total_errors": local_errors,
        "num_streams": len(camera_ids),
        "fps": local_frames / elapsed if elapsed > 0 else 0,
    })


# =============================================================================
# GPU Process
# =============================================================================

def nvdec_pool_process(
    process_id: int,
    camera_configs: List[StreamConfig],
    pool_size: int,
    duration_sec: float,
    result_queue: mp.Queue,
    stop_event: mp.Event,
    burst_size: int = 4,
    num_slots: int = 32,
    target_fps: int = 0,
    shared_frame_count: Optional[mp.Value] = None,
    gpu_frame_counts: Optional[Dict[int, mp.Value]] = None,
    total_num_streams: int = 0,
    total_num_gpus: int = 1,
):
    """NVDEC process for one GPU.

    Creates NV12 ring buffers: (H*1.5, W) = 0.6 MB/frame.

    Args:
        gpu_frame_counts: Dict mapping gpu_id -> per-GPU frame counter (for per-GPU stats)
        shared_frame_count: Global frame counter (for overall stats)
        total_num_streams: Total streams across ALL GPUs (for global per-stream calc)
        total_num_gpus: Total number of GPUs (for context in logging)
    """
    if not camera_configs:
        return

    gpu_id = camera_configs[0].gpu_id
    target_h = camera_configs[0].height
    target_w = camera_configs[0].width

    # Get per-GPU counter (or fall back to shared if not provided)
    gpu_frame_count = gpu_frame_counts.get(gpu_id) if gpu_frame_counts else None

    if CUPY_AVAILABLE:
        cp.cuda.Device(gpu_id).use()

    # Initialize global frame counter
    frame_counter = GlobalFrameCounter(is_producer=True)
    if process_id == 0:
        frame_counter.initialize()
        logger.info(f"Process {process_id}: GlobalFrameCounter initialized")
    else:
        max_retries = 50
        for retry in range(max_retries):
            try:
                if os.path.exists("/dev/shm/global_frame_counter"):
                    frame_counter.connect()
                    logger.info(f"Process {process_id}: Connected to GlobalFrameCounter")
                    break
            except Exception:
                if retry == max_retries - 1:
                    raise
            time.sleep(0.1)
        else:
            raise RuntimeError(f"Process {process_id}: GlobalFrameCounter not found")

    # Create decoder pool
    try:
        pool = NVDECDecoderPool(pool_size, gpu_id)
    except Exception as e:
        logger.error(f"Process {process_id}: Failed to create decoder pool: {e}")
        result_queue.put({
            "process_id": process_id,
            "error": str(e),
            "total_frames": 0,
            "total_errors": 1,
        })
        return

    if pool.actual_pool_size == 0:
        result_queue.put({
            "process_id": process_id,
            "error": "No decoders created",
            "total_frames": 0,
            "total_errors": 1,
        })
        return

    # Create NV12 ring buffers: (H + H/2, W, 1) = 0.6 MB/frame
    ring_buffers: Dict[str, CudaIpcRingBuffer] = {}
    frame_size_mb = target_h * target_w * 1.5 / 1e6

    try:
        for i, config in enumerate(camera_configs):
            rb = CudaIpcRingBuffer.create_producer(
                config.camera_id,
                gpu_id=config.gpu_id,
                num_slots=num_slots,
                width=config.width,
                height=config.height + config.height // 2,  # H * 1.5 for NV12
                channels=1,
            )
            ring_buffers[config.camera_id] = rb

            pool.assign_stream(
                stream_id=i,
                camera_id=config.camera_id,
                video_path=config.video_path,
                width=config.width,
                height=config.height
            )

        logger.info(f"Process {process_id}: {pool.actual_pool_size} decoders, "
                   f"{len(camera_configs)} streams, NV12 ({frame_size_mb:.1f} MB/frame)")

        thread_stop_event = threading.Event()
        thread_result_queue = thread_queue.Queue()

        threads = []
        for decoder_idx in range(pool.actual_pool_size):
            t = threading.Thread(
                target=nvdec_pool_worker,
                args=(
                    process_id * 100 + decoder_idx,
                    decoder_idx,
                    pool,
                    ring_buffers,
                    frame_counter,
                    duration_sec,
                    thread_result_queue,
                    thread_stop_event,
                    burst_size,
                    target_h,
                    target_w,
                    target_fps,
                    shared_frame_count,
                    gpu_frame_count,  # Per-GPU counter
                )
            )
            t.start()
            threads.append(t)

        # Progress monitoring loop with current/avg FPS tracking
        start_time = time.perf_counter()
        last_report_time = start_time
        last_gpu_frame_count = 0
        last_global_frame_count = 0
        report_interval = 5.0
        processing_start_time = None
        gpu_frames_at_start = 0
        global_frames_at_start = 0
        num_gpu_streams = len(camera_configs)

        while not stop_event.is_set():
            current_time = time.perf_counter()
            if current_time - start_time >= duration_sec:
                break

            # Periodic progress report with current and average FPS
            if current_time - last_report_time >= report_interval:
                elapsed = current_time - start_time
                remaining = max(0, duration_sec - elapsed)

                # Get per-GPU frame count (this GPU only)
                gpu_frames = gpu_frame_count.value if gpu_frame_count else 0
                gpu_interval_frames = gpu_frames - last_gpu_frame_count
                gpu_interval_fps = gpu_interval_frames / report_interval
                gpu_per_stream_fps = gpu_interval_fps / num_gpu_streams if num_gpu_streams > 0 else 0

                # Get global frame count (all GPUs)
                global_frames = shared_frame_count.value if shared_frame_count else 0
                global_interval_frames = global_frames - last_global_frame_count
                global_interval_fps = global_interval_frames / report_interval
                global_per_stream_fps = global_interval_fps / total_num_streams if total_num_streams > 0 else 0

                # Track when processing actually starts (exclude warmup)
                if processing_start_time is None and gpu_frames > 0:
                    processing_start_time = last_report_time
                    gpu_frames_at_start = last_gpu_frame_count
                    global_frames_at_start = last_global_frame_count

                # Calculate average FPS excluding warmup
                if processing_start_time is not None:
                    processing_elapsed = current_time - processing_start_time

                    # Per-GPU averages
                    gpu_processing_frames = gpu_frames - gpu_frames_at_start
                    gpu_avg_fps = gpu_processing_frames / processing_elapsed if processing_elapsed > 0 else 0
                    gpu_avg_per_stream = gpu_avg_fps / num_gpu_streams if num_gpu_streams > 0 else 0

                    # Global averages
                    global_processing_frames = global_frames - global_frames_at_start
                    global_avg_fps = global_processing_frames / processing_elapsed if processing_elapsed > 0 else 0
                    global_avg_per_stream = global_avg_fps / total_num_streams if total_num_streams > 0 else 0

                    # Log per-GPU stats
                    logger.info(
                        f"GPU{gpu_id} [{elapsed:5.1f}s] {gpu_frames:,} frames ({num_gpu_streams} cams) | "
                        f"cur: {gpu_interval_fps:,.0f} FPS ({gpu_per_stream_fps:.1f}/cam) | "
                        f"avg: {gpu_avg_fps:,.0f} FPS ({gpu_avg_per_stream:.1f}/cam)"
                    )

                    # Log global stats (only from GPU0 to avoid spam)
                    if gpu_id == 0:
                        logger.info(
                            f"GLOBAL [{elapsed:5.1f}s] {global_frames:,} frames ({total_num_streams} cams, {total_num_gpus} GPUs) | "
                            f"cur: {global_interval_fps:,.0f} FPS ({global_per_stream_fps:.1f}/cam) | "
                            f"avg: {global_avg_fps:,.0f} FPS ({global_avg_per_stream:.1f}/cam) | "
                            f"{remaining:.0f}s left"
                        )

                last_gpu_frame_count = gpu_frames
                last_global_frame_count = global_frames
                last_report_time = current_time

            time.sleep(0.1)

        thread_stop_event.set()

        for t in threads:
            t.join(timeout=30.0)

        total_frames = 0
        total_errors = 0
        elapsed = time.perf_counter() - start_time

        while not thread_result_queue.empty():
            try:
                r = thread_result_queue.get_nowait()
                total_frames += r.get("total_frames", 0)
                total_errors += r.get("total_errors", 0)
            except:
                break

        pool.close()
        for rb in ring_buffers.values():
            rb.close()

        result_queue.put({
            "process_id": process_id,
            "elapsed_sec": elapsed,
            "total_frames": total_frames,
            "total_errors": total_errors,
            "num_streams": len(camera_configs),
            "pool_size": pool.actual_pool_size,
            "fps": total_frames / elapsed if elapsed > 0 else 0,
            "per_stream_fps": total_frames / elapsed / len(camera_configs) if elapsed > 0 and camera_configs else 0,
        })

    except Exception as e:
        logger.error(f"Process {process_id} error: {e}")
        import traceback
        traceback.print_exc()

        pool.close()
        for rb in ring_buffers.values():
            rb.close()

        result_queue.put({
            "process_id": process_id,
            "error": str(e),
            "total_frames": 0,
            "total_errors": 1,
        })


# =============================================================================
# Streaming Gateway
# =============================================================================

class StreamingGateway:
    """Multi-stream video producer outputting NV12 tensors (minimal IPC payload)."""

    def __init__(self, config: GatewayConfig):
        self.config = config
        self._workers: List[mp.Process] = []
        self._stop_event = mp.Event()
        self._result_queue = mp.Queue()

    def start(self) -> Dict:
        """Start the gateway."""
        if not CUPY_AVAILABLE:
            raise RuntimeError("CuPy is required")
        if not RING_BUFFER_AVAILABLE:
            raise RuntimeError("CUDA IPC ring buffer not available")
        if not PYNVCODEC_AVAILABLE:
            raise RuntimeError("PyNvVideoCodec required")
        return self._start_nvdec_pool()

    def _start_nvdec_pool(self) -> Dict:
        """Start NVDEC pool across GPUs."""
        num_gpus = min(self.config.num_gpus, 8)
        streams_per_gpu = self.config.num_streams // num_gpus
        extra_streams = self.config.num_streams % num_gpus

        logger.info(f"Starting NVDEC on {num_gpus} GPU(s): {self.config.num_streams} streams, "
                   f"pool_size={self.config.nvdec_pool_size}/GPU, output=NV12 (0.6 MB)")

        ctx = mp.get_context("spawn")
        self._stop_event = ctx.Event()
        self._result_queue = ctx.Queue()

        # Shared counter for real-time FPS tracking (use 'L' for large counts)
        shared_frame_count = ctx.Value('L', 0)

        stream_idx = 0
        for gpu_id in range(num_gpus):
            n_streams = streams_per_gpu + (1 if gpu_id < extra_streams else 0)

            gpu_configs = []
            for i in range(n_streams):
                config = StreamConfig(
                    camera_id=f"cam_{stream_idx:04d}",
                    video_path=self.config.video_path,
                    width=self.config.frame_width,
                    height=self.config.frame_height,
                    target_fps=self.config.target_fps,
                    gpu_id=gpu_id,
                )
                gpu_configs.append(config)
                stream_idx += 1

            p = ctx.Process(
                target=nvdec_pool_process,
                args=(gpu_id, gpu_configs, self.config.nvdec_pool_size,
                      self.config.duration_sec, self._result_queue, self._stop_event,
                      self.config.nvdec_burst_size, self.config.num_slots,
                      self.config.target_fps, shared_frame_count)
            )
            p.start()
            self._workers.append(p)
            logger.info(f"GPU {gpu_id}: {n_streams} streams")
            time.sleep(0.1)

        # Progress monitoring loop - print progress every 5 seconds
        start_time = time.perf_counter()
        last_report_time = start_time
        last_frame_count = 0
        report_interval = 5.0  # seconds
        processing_start_time = None  # Track when actual processing starts
        frames_at_processing_start = 0

        print(f"  [  0.0s] Started {num_gpus} GPU workers...")

        while any(p.is_alive() for p in self._workers):
            time.sleep(0.5)
            current_time = time.perf_counter()

            # Periodic progress report with real-time FPS
            if current_time - last_report_time >= report_interval:
                elapsed = current_time - start_time
                remaining = max(0, self.config.duration_sec - elapsed)

                # Read current frame count
                current_frames = shared_frame_count.value
                interval_frames = current_frames - last_frame_count
                interval_fps = interval_frames / report_interval  # Current throughput
                per_stream_fps = interval_fps / self.config.num_streams if self.config.num_streams > 0 else 0

                # Track when processing actually starts (exclude warmup from avg)
                if processing_start_time is None and current_frames > 0:
                    processing_start_time = last_report_time  # Use previous report time
                    frames_at_processing_start = last_frame_count

                # Calculate average FPS excluding warmup time
                if processing_start_time is not None:
                    processing_elapsed = current_time - processing_start_time
                    processing_frames = current_frames - frames_at_processing_start
                    avg_fps = processing_frames / processing_elapsed if processing_elapsed > 0 else 0
                    print(f"  [{elapsed:5.1f}s] {current_frames:,} frames | cur: {interval_fps:,.0f} FPS ({per_stream_fps:.1f}/stream) | avg: {avg_fps:,.0f} FPS | {remaining:.0f}s left")
                else:
                    print(f"  [{elapsed:5.1f}s] Warming up... | {remaining:.0f}s left")

                last_report_time = current_time
                last_frame_count = current_frames

        # Wait for all workers to fully complete
        for p in self._workers:
            p.join(timeout=5)

        results = []
        while not self._result_queue.empty():
            results.append(self._result_queue.get())

        for r in results:
            if "error" in r:
                logger.error(f"NVDEC error: {r['error']}")

        total_frames = sum(r.get("total_frames", 0) for r in results)
        total_errors = sum(r.get("total_errors", 0) for r in results)
        total_elapsed = max((r.get("elapsed_sec", 0) for r in results), default=0)

        aggregate_fps = total_frames / total_elapsed if total_elapsed > 0 else 0
        per_stream_fps = aggregate_fps / self.config.num_streams if self.config.num_streams > 0 else 0

        return {
            "num_streams": self.config.num_streams,
            "num_gpus": num_gpus,
            "pool_size": self.config.nvdec_pool_size,
            "duration_sec": total_elapsed,
            "total_frames": total_frames,
            "total_errors": total_errors,
            "aggregate_fps": aggregate_fps,
            "per_stream_fps": per_stream_fps,
            "gpu_results": results,
        }

    def stop(self):
        """Stop all workers."""
        self._stop_event.set()
        for p in self._workers:
            p.join(timeout=5)
            if p.is_alive():
                p.terminate()


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Streaming Gateway - CUDA IPC Producer (NV12)")
    parser.add_argument("--video", "-v", required=True, help="Video file path")
    parser.add_argument("--num-streams", "-n", type=int, default=100, help="Number of streams")
    parser.add_argument("--fps", type=int, default=0, help="Target FPS limit per stream (0=unlimited)")
    parser.add_argument("--width", type=int, default=640, help="Frame width")
    parser.add_argument("--height", type=int, default=640, help="Frame height")
    parser.add_argument("--duration", "-d", type=float, default=30.0, help="Duration in seconds")
    parser.add_argument("--gpu", type=int, default=0, help="Primary GPU ID")
    parser.add_argument("--num-gpus", "-g", type=int, default=1, help="Number of GPUs (1-8)")
    parser.add_argument("--pool-size", type=int, default=8, help="NVDEC pool size per GPU")
    parser.add_argument("--burst-size", type=int, default=4, help="Frames per stream before rotating")
    parser.add_argument("--slots", type=int, default=32, help="Ring buffer slots per camera")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode - only show final results")
    args = parser.parse_args()

    # Setup logging based on quiet mode
    setup_logging(quiet=args.quiet)

    config = GatewayConfig(
        video_path=args.video,
        num_streams=args.num_streams,
        target_fps=args.fps,
        frame_width=args.width,
        frame_height=args.height,
        gpu_id=args.gpu,
        num_gpus=args.num_gpus,
        duration_sec=args.duration,
        nvdec_pool_size=args.pool_size,
        nvdec_burst_size=args.burst_size,
        num_slots=args.slots,
    )

    frame_size = args.width * args.height * 1.5
    output_fmt = f"NV12 ({args.width}x{args.height}x1.5 = {frame_size/1e6:.1f} MB/frame)"
    fps_limit_str = f"{args.fps} FPS/stream" if args.fps > 0 else "unlimited"

    if not args.quiet:
        print("\n" + "=" * 60)
        print("      STREAMING GATEWAY - CUDA IPC Producer (NV12)")
        print("=" * 60)
        print(f"  Video:      {args.video}")
        print(f"  Streams:    {args.num_streams}")
        print(f"  GPUs:       {args.num_gpus}")
        print(f"  Pool size:  {args.pool_size} NVDEC decoders/GPU")
        print(f"  FPS limit:  {fps_limit_str}")
        print(f"  Output:     {output_fmt}")
        print(f"  Duration:   {args.duration}s")
        print("=" * 60)

    gateway = StreamingGateway(config)

    try:
        results = gateway.start()
        # Clean summary output
        print("\n")
        print("=" * 60)
        print("         STREAMING GATEWAY BENCHMARK RESULTS")
        print("=" * 60)
        print(f"  Video:        {args.video}")
        print(f"  Streams:      {args.num_streams}")
        print(f"  GPUs:         {args.num_gpus}")
        print(f"  FPS limit:    {fps_limit_str}")
        print(f"  Duration:     {args.duration}s")
        print("-" * 60)
        print(f"  Total Frames: {results['total_frames']:,}")
        print("-" * 60)
        print(f"  >>> AGGREGATE FPS: {results['aggregate_fps']:,.0f} <<<")
        print(f"  >>> PER-STREAM FPS: {results['per_stream_fps']:.1f} <<<")
        print("=" * 60)
        print()
    except KeyboardInterrupt:
        gateway.stop()
        print("\nStopped")


if __name__ == "__main__":
    main()
