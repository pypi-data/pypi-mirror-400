"""Tests for platform-aware configuration."""
import sys
from pathlib import Path
from unittest.mock import patch

from video_transcriber_gui.config import (
    get_default_video_directory,
    get_output_directory,
)


class TestGetDefaultVideoDirectory:
    """Tests for get_default_video_directory()."""

    def test_returns_path_object(self):
        result = get_default_video_directory()
        assert isinstance(result, Path)

    def test_linux_returns_videos_directory(self):
        with patch.object(sys, "platform", "linux"):
            result = get_default_video_directory()
            assert result == Path.home() / "Videos"

    def test_darwin_returns_movies_directory(self):
        with patch.object(sys, "platform", "darwin"):
            result = get_default_video_directory()
            assert result == Path.home() / "Movies"

    def test_windows_returns_videos_directory(self):
        with patch.object(sys, "platform", "win32"):
            result = get_default_video_directory()
            assert result == Path.home() / "Videos"


class TestGetOutputDirectory:
    """Tests for get_output_directory()."""

    def test_returns_path_object(self):
        result = get_output_directory()
        assert isinstance(result, Path)

    def test_returns_output_subdirectory_of_cwd(self):
        result = get_output_directory()
        assert result == Path.cwd() / "output"

    def test_creates_directory_if_not_exists(self, tmp_path):
        with patch("video_transcriber_gui.config.Path.cwd", return_value=tmp_path):
            result = get_output_directory()
            assert result.exists()
            assert result.is_dir()
