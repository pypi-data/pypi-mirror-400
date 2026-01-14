"""FFmpeg configuration for streaming gateway.

This module provides configuration dataclasses for FFmpeg-based video streaming,
following the same pattern as GStreamerConfig for consistency.
"""
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class FFmpegConfig:
    """Configuration for FFmpeg-based streaming.

    This configuration controls how FFmpeg subprocesses are spawned
    for video ingestion, with options for hardware acceleration,
    low-latency settings, and output format control.
    """

    # Decoding settings
    threads: int = 1                      # Single decode thread per stream (prevents thread explosion)
    buffer_frames: int = 4                # Pipe buffer size in frames
    hwaccel: str = "auto"                 # Hardware acceleration: auto, cuda, vaapi, videotoolbox, none

    # Input settings
    realtime: bool = False                # -re flag for source FPS timing (simulates live camera)
    loop: bool = True                     # Loop video files indefinitely
    low_latency: bool = True              # Enable nobuffer, low_delay flags

    # Output format
    pixel_format: str = "bgr24"           # Output format: bgr24 (OpenCV), rgb24, nv12
    output_width: int = 0                 # Downscale width (0 = use source resolution)
    output_height: int = 0                # Downscale height (0 = use source resolution)

    # JPEG encoding settings (when encoding output)
    quality: int = 90                     # JPEG quality (1-100)
    encode_output: bool = False           # If True, encode frames to JPEG before sending

    # Connection settings
    tcp_timeout: int = 5                  # TCP timeout in seconds for RTSP/HTTP
    rtsp_transport: str = "tcp"           # RTSP transport: tcp, udp, http
    reconnect_delay: float = 1.0          # Delay between reconnection attempts

    # Debug/logging
    loglevel: str = "error"               # FFmpeg log level: quiet, error, warning, info, debug
    probesize: int = 5000000              # Probe size in bytes for format detection
    analyzeduration: int = 5000000        # Analyze duration in microseconds

    def to_ffmpeg_args(self, source: str, width: int = 0, height: int = 0) -> List[str]:
        """Build FFmpeg command line arguments.

        Args:
            source: Input source (file path, RTSP URL, etc.)
            width: Frame width (0 = auto-detect)
            height: Frame height (0 = auto-detect)

        Returns:
            List of command line arguments for FFmpeg
        """
        cmd = ["ffmpeg"]

        # Logging
        cmd.extend(["-loglevel", self.loglevel])
        cmd.extend(["-nostdin"])

        # Realtime simulation
        if self.realtime:
            cmd.extend(["-re"])

        # Looping for video files
        if self.loop and not source.startswith("rtsp://") and not source.startswith("http://"):
            cmd.extend(["-stream_loop", "-1"])

        # Low-latency flags
        if self.low_latency:
            cmd.extend(["-fflags", "nobuffer"])
            cmd.extend(["-flags", "low_delay"])

        # Probe settings
        cmd.extend(["-probesize", str(self.probesize)])
        cmd.extend(["-analyzeduration", str(self.analyzeduration)])

        # Hardware acceleration
        if self.hwaccel != "none":
            cmd.extend(["-hwaccel", self.hwaccel])

        # RTSP-specific settings
        if source.startswith("rtsp://"):
            cmd.extend(["-rtsp_transport", self.rtsp_transport])
            cmd.extend(["-stimeout", str(self.tcp_timeout * 1000000)])  # microseconds

        # Input source
        cmd.extend(["-i", source])

        # Disable audio
        cmd.extend(["-an"])

        # Video sync mode
        cmd.extend(["-vsync", "0"])

        # Thread count for decoding
        cmd.extend(["-threads", str(self.threads)])

        # Downscale filter
        output_w = self.output_width if self.output_width > 0 else width
        output_h = self.output_height if self.output_height > 0 else height
        if output_w > 0 and output_h > 0:
            cmd.extend(["-vf", f"scale={output_w}:{output_h}"])

        # Output format: raw video to pipe
        cmd.extend(["-f", "rawvideo"])
        cmd.extend(["-pix_fmt", self.pixel_format])
        cmd.extend(["pipe:1"])

        return cmd


def is_ffmpeg_available() -> bool:
    """Check if FFmpeg is available on the system.

    Returns:
        True if FFmpeg is available, False otherwise
    """
    import subprocess
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def get_ffmpeg_version() -> Optional[str]:
    """Get FFmpeg version string.

    Returns:
        Version string or None if FFmpeg is not available
    """
    import subprocess
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # First line contains version
            first_line = result.stdout.split('\n')[0]
            return first_line
        return None
    except Exception:
        return None


def detect_hwaccel() -> str:
    """Detect available hardware acceleration.

    Returns:
        Best available hwaccel option: cuda, vaapi, videotoolbox, or none
    """
    import subprocess
    import sys

    # Check for NVIDIA CUDA (Linux/Windows)
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            return "cuda"
    except Exception:
        pass

    # Check for VAAPI (Linux)
    if sys.platform.startswith("linux"):
        try:
            import os
            if os.path.exists("/dev/dri/renderD128"):
                return "vaapi"
        except Exception:
            pass

    # Check for VideoToolbox (macOS)
    if sys.platform == "darwin":
        return "videotoolbox"

    return "none"
