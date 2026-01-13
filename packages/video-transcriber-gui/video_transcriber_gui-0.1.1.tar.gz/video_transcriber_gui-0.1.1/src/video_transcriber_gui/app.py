"""Main Textual application for video transcription."""
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.widgets import Button, Checkbox, Label, Header, Footer
from textual_fspicker import FileOpen, Filters

from video_transcriber_gui.config import get_default_video_directory, get_output_directory
from video_transcriber_gui.transcription import transcribe, TranscriptionError


class VideoTranscriberApp(App):
    """A Textual app for transcribing video presentations."""

    TITLE = "Video Transcriber"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
    ]

    CSS = """
    Screen {
        align: center middle;
    }

    #container {
        width: 60;
        height: auto;
        padding: 1 2;
        border: solid green;
    }

    #status-label {
        width: 100%;
        height: 3;
        content-align: center middle;
        margin: 1 0;
    }

    Button {
        width: 100%;
        margin: 1 0;
    }
    """

    def __init__(self):
        super().__init__()
        self.selected_file: Path | None = None
        self.status_text: str = "No video selected"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("No video selected", id="status-label")
        yield Button("Select Video", id="select-video-btn")
        yield Checkbox("Include timestamps", id="include-timestamps")
        yield Checkbox("Audio only", id="audio-only")
        yield Button("Transcribe", id="transcribe-btn", disabled=True)
        yield Footer()

    def set_selected_file(self, file_path: Path) -> None:
        """Set the selected video file and update the UI."""
        self.selected_file = file_path
        self.status_text = f"Selected: {file_path.name}"
        self.query_one("#status-label", Label).update(self.status_text)
        self.query_one("#transcribe-btn", Button).disabled = False

    def update_status(self, text: str) -> None:
        """Update the status label and internal status text."""
        self.status_text = text
        self.query_one("#status-label", Label).update(text)

    @on(Button.Pressed, "#select-video-btn")
    @work
    async def open_file_dialog(self) -> None:
        """Open the file selection dialog."""
        filters = Filters(("MP4 Videos", lambda p: p.suffix.lower() == ".mp4"),)
        default_path = get_default_video_directory()

        if opened := await self.push_screen_wait(FileOpen(default_path, filters=filters)):
            self.set_selected_file(opened)

    @on(Button.Pressed, "#transcribe-btn")
    def on_transcribe_pressed(self) -> None:
        """Handle transcribe button press."""
        self.start_transcription()

    def start_transcription(self) -> None:
        """Start the transcription process."""
        self.update_status("Transcribing...")
        self.query_one("#transcribe-btn", Button).disabled = True
        include_timestamps = self.query_one("#include-timestamps", Checkbox).value
        audio_only = self.query_one("#audio-only", Checkbox).value
        self.run_transcription(include_timestamps, audio_only)

    @work(thread=True)
    def run_transcription(
        self, include_timestamps: bool, audio_only: bool
    ) -> None:
        """Run transcription in a background thread."""
        try:
            output_dir = get_output_directory()
            result = transcribe(
                self.selected_file,
                output_dir,
                include_timestamps=include_timestamps,
                audio_only=audio_only,
            )
            self.call_from_thread(self.on_transcription_complete, result)
        except TranscriptionError as e:
            self.call_from_thread(self.on_transcription_error, str(e))

    def on_transcription_complete(self, result_path: Path) -> None:
        """Handle successful transcription completion."""
        self.update_status(f"Complete: {result_path.name}")
        self.query_one("#transcribe-btn", Button).disabled = False

    def on_transcription_error(self, error_message: str) -> None:
        """Handle transcription error."""
        self.update_status(f"Error: {error_message}")
        self.query_one("#transcribe-btn", Button).disabled = False


def main():
    """Entry point for the application."""
    app = VideoTranscriberApp()
    app.run()


if __name__ == "__main__":
    main()
