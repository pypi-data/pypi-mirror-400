"""Wrapper around video-transcriber library."""
from pathlib import Path

from video_transcriber.transcribe import transcribe_video


class TranscriptionError(Exception):
    """Raised when transcription fails."""

    pass


def transcribe(
    video_path: Path,
    output_dir: Path,
    include_timestamps: bool = False,
    audio_only: bool = False,
) -> Path:
    """Transcribe a video file and return the path to the output zip.

    Args:
        video_path: Path to the input video file
        output_dir: Directory where the output zip will be saved
        include_timestamps: Whether to include timestamps in the markdown output
        audio_only: If True, only transcribe audio without extracting frames

    Returns:
        Path to the generated zip file

    Raises:
        TranscriptionError: If the video file doesn't exist or transcription fails
    """
    if not video_path.exists():
        raise TranscriptionError(f"Video file does not exist: {video_path}")

    try:
        zip_path = transcribe_video(
            video_path=str(video_path),
            output_dir=str(output_dir),
            model_size="base",
            include_timestamps=include_timestamps,
            audio_only=audio_only,
        )
        return Path(zip_path)
    except Exception as e:
        raise TranscriptionError(f"Transcription failed: {e}") from e
