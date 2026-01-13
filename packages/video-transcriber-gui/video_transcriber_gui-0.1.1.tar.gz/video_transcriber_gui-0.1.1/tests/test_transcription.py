"""Tests for transcription wrapper."""
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from video_transcriber_gui.transcription import transcribe, TranscriptionError


class TestTranscribe:
    """Tests for transcribe() wrapper function."""

    def test_calls_video_transcriber_with_correct_arguments(self, tmp_path):
        video_path = tmp_path / "test.mp4"
        video_path.touch()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch("video_transcriber_gui.transcription.transcribe_video") as mock:
            mock.return_value = str(output_dir / "transcript.zip")
            transcribe(video_path, output_dir)

            mock.assert_called_once_with(
                video_path=str(video_path),
                output_dir=str(output_dir),
                model_size="base",
                include_timestamps=False,
                audio_only=False,
            )

    def test_returns_path_to_zip_file(self, tmp_path):
        video_path = tmp_path / "test.mp4"
        video_path.touch()
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        expected_zip = output_dir / "transcript.zip"

        with patch("video_transcriber_gui.transcription.transcribe_video") as mock:
            mock.return_value = str(expected_zip)
            result = transcribe(video_path, output_dir)

            assert result == expected_zip
            assert isinstance(result, Path)

    def test_raises_transcription_error_on_failure(self, tmp_path):
        video_path = tmp_path / "test.mp4"
        video_path.touch()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch("video_transcriber_gui.transcription.transcribe_video") as mock:
            mock.side_effect = Exception("Whisper failed")

            with pytest.raises(TranscriptionError) as exc_info:
                transcribe(video_path, output_dir)

            assert "Whisper failed" in str(exc_info.value)

    def test_raises_error_for_nonexistent_video(self, tmp_path):
        video_path = tmp_path / "nonexistent.mp4"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with pytest.raises(TranscriptionError) as exc_info:
            transcribe(video_path, output_dir)

        assert "does not exist" in str(exc_info.value)

    def test_passes_include_timestamps_option(self, tmp_path):
        video_path = tmp_path / "test.mp4"
        video_path.touch()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch("video_transcriber_gui.transcription.transcribe_video") as mock:
            mock.return_value = str(output_dir / "transcript.zip")
            transcribe(video_path, output_dir, include_timestamps=True)

            mock.assert_called_once_with(
                video_path=str(video_path),
                output_dir=str(output_dir),
                model_size="base",
                include_timestamps=True,
                audio_only=False,
            )

    def test_passes_audio_only_option(self, tmp_path):
        video_path = tmp_path / "test.mp4"
        video_path.touch()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch("video_transcriber_gui.transcription.transcribe_video") as mock:
            mock.return_value = str(output_dir / "transcript.zip")
            transcribe(video_path, output_dir, audio_only=True)

            mock.assert_called_once_with(
                video_path=str(video_path),
                output_dir=str(output_dir),
                model_size="base",
                include_timestamps=False,
                audio_only=True,
            )
