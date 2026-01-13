"""Tests for the main Textual application."""
from pathlib import Path
from unittest.mock import patch, AsyncMock

import pytest

from video_transcriber_gui.app import VideoTranscriberApp


class TestVideoTranscriberApp:
    """Tests for the main application using Pilot API."""

    async def test_app_has_title(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            assert app.title == "Video Transcriber"

    async def test_app_has_select_video_button(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            button = app.query_one("#select-video-btn")
            assert button is not None
            assert "Select Video" in str(button.label)

    async def test_app_has_transcribe_button(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            button = app.query_one("#transcribe-btn")
            assert button is not None
            assert "Transcribe" in str(button.label)

    async def test_transcribe_button_disabled_initially(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            button = app.query_one("#transcribe-btn")
            assert button.disabled

    async def test_app_has_status_label(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            label = app.query_one("#status-label")
            assert label is not None


class TestFileSelection:
    """Tests for file selection behavior."""

    async def test_selecting_file_updates_status_label(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            # Simulate file selection by directly setting the selected file
            test_path = Path("/tmp/test_video.mp4")
            app.set_selected_file(test_path)
            await pilot.pause()

            # Verify status was updated by checking status_text attribute
            assert app.status_text == f"Selected: {test_path.name}"

    async def test_selecting_file_enables_transcribe_button(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            test_path = Path("/tmp/test_video.mp4")
            app.set_selected_file(test_path)
            await pilot.pause()

            button = app.query_one("#transcribe-btn")
            assert not button.disabled

    async def test_selected_file_is_stored(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            test_path = Path("/tmp/test_video.mp4")
            app.set_selected_file(test_path)

            assert app.selected_file == test_path


class TestTranscription:
    """Tests for transcription execution."""

    async def test_start_transcription_updates_status_immediately(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            test_path = Path("/tmp/test_video.mp4")
            app.set_selected_file(test_path)

            # Patch run_transcription to do nothing (so we can check immediate state)
            with patch.object(app, "run_transcription"):
                app.start_transcription()
                # Status should show transcribing before worker runs
                assert app.status_text == "Transcribing..."

    async def test_transcribe_shows_result_on_success(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            test_path = Path("/tmp/test_video.mp4")
            app.set_selected_file(test_path)
            expected_zip = Path("/tmp/output/result.zip")

            with patch("video_transcriber_gui.app.transcribe") as mock:
                mock.return_value = expected_zip
                app.start_transcription()
                # Wait for worker to complete
                await pilot.pause()
                await pilot.pause()

                assert "result.zip" in app.status_text or "Complete" in app.status_text

    async def test_transcribe_shows_error_on_failure(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            test_path = Path("/tmp/test_video.mp4")
            app.set_selected_file(test_path)

            with patch("video_transcriber_gui.app.transcribe") as mock:
                from video_transcriber_gui.transcription import TranscriptionError
                mock.side_effect = TranscriptionError("Test error")
                app.start_transcription()
                await pilot.pause()
                await pilot.pause()

                assert "Error" in app.status_text or "failed" in app.status_text.lower()


class TestTranscriptionOptions:
    """Tests for transcription option checkboxes."""

    async def test_app_has_include_timestamps_checkbox(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            checkbox = app.query_one("#include-timestamps")
            assert checkbox is not None

    async def test_include_timestamps_defaults_to_unchecked(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            checkbox = app.query_one("#include-timestamps")
            assert checkbox.value is False

    async def test_app_has_audio_only_checkbox(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            checkbox = app.query_one("#audio-only")
            assert checkbox is not None

    async def test_audio_only_defaults_to_unchecked(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            checkbox = app.query_one("#audio-only")
            assert checkbox.value is False

    async def test_transcribe_passes_checkbox_values(self):
        app = VideoTranscriberApp()
        async with app.run_test() as pilot:
            test_path = Path("/tmp/test_video.mp4")
            app.set_selected_file(test_path)

            # Check both checkboxes
            app.query_one("#include-timestamps").value = True
            app.query_one("#audio-only").value = True

            with patch("video_transcriber_gui.app.transcribe") as mock:
                mock.return_value = Path("/tmp/output/result.zip")
                app.start_transcription()
                await pilot.pause()
                await pilot.pause()

                mock.assert_called_once()
                call_kwargs = mock.call_args[1]
                assert call_kwargs["include_timestamps"] is True
                assert call_kwargs["audio_only"] is True
