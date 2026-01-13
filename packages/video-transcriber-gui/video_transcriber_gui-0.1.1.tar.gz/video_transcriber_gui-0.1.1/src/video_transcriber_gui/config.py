"""Platform-aware configuration for video-transcriber-gui."""
import sys
from pathlib import Path


def get_default_video_directory() -> Path:
    """Return the default video directory for the current platform.

    Returns:
        ~/Videos on Linux and Windows
        ~/Movies on macOS
    """
    if sys.platform == "darwin":
        return Path.home() / "Movies"
    return Path.home() / "Videos"


def get_output_directory() -> Path:
    """Return the output directory, creating it if necessary.

    Returns:
        ./output relative to current working directory
    """
    output_dir = Path.cwd() / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir
