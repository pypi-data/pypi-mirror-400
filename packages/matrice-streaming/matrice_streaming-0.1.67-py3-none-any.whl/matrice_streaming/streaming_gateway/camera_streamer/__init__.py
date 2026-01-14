from .camera_streamer import CameraStreamer
from .worker_manager import WorkerManager
from .async_camera_worker import AsyncCameraWorker

# GStreamer components (optional - graceful import)
try:
    from .gstreamer_camera_streamer import (
        GStreamerCameraStreamer,
        GStreamerConfig,
        GStreamerPipeline,
        is_gstreamer_available,
    )
    from .gstreamer_worker import (
        GStreamerAsyncWorker,
        run_gstreamer_worker,
    )
    from .gstreamer_worker_manager import GStreamerWorkerManager

    GSTREAMER_AVAILABLE = is_gstreamer_available()
except (ImportError, ValueError, AttributeError, RuntimeError, TypeError):
    # ImportError: gi module not available
    # ValueError: gi.require_version fails when GStreamer not installed
    # AttributeError/RuntimeError/TypeError: other initialization errors
    # Suppress warnings - these are optional dependencies
    GSTREAMER_AVAILABLE = False
    GStreamerCameraStreamer = None
    GStreamerConfig = None
    GStreamerPipeline = None
    GStreamerAsyncWorker = None
    GStreamerWorkerManager = None

    def is_gstreamer_available():
        return False

# NVDEC components (optional - graceful import)
try:
    from .nvdec_worker_manager import (
        NVDECWorkerManager,
        is_nvdec_available,
        get_available_gpu_count,
    )
    NVDEC_AVAILABLE = is_nvdec_available()
except (ImportError, AttributeError, RuntimeError, TypeError, ValueError) as e:
    # NVDEC not available (requires CuPy, PyNvVideoCodec, cuda_shm_ring_buffer)
    # Suppress warnings - these are optional dependencies
    NVDEC_AVAILABLE = False
    NVDECWorkerManager = None

    def is_nvdec_available():
        return False

    def get_available_gpu_count():
        return 1

__all__ = [
    # Original components
    "CameraStreamer",
    "WorkerManager",
    "AsyncCameraWorker",
    # GStreamer components
    "GStreamerCameraStreamer",
    "GStreamerConfig",
    "GStreamerPipeline",
    "GStreamerAsyncWorker",
    "GStreamerWorkerManager",
    "is_gstreamer_available",
    "GSTREAMER_AVAILABLE",
    # NVDEC components
    "NVDECWorkerManager",
    "is_nvdec_available",
    "get_available_gpu_count",
    "NVDEC_AVAILABLE",
]