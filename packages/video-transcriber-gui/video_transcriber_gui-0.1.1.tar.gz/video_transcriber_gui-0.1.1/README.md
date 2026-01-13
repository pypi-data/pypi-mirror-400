# video-transcriber-gui

A command line GUI for [video-transcriber](https://github.com/romilly/video-transcriber) built with [Textual](https://textual.textualize.io/).

## Features

- Select MP4 video files via a file browser dialog
- Platform-aware default directories (`~/Videos` on Linux/Windows, `~/Movies` on macOS)
- Transcribe videos using OpenAI's Whisper model (runs locally)
- Output saved to `./output` directory as a ZIP containing markdown and slide images

## Requirements

- Python 3.10+
- ffmpeg (for audio extraction)

## Installation

Create and activate a virtual environment, then install:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install video-transcriber-gui
```

## Usage

With the virtual environment activated:

```bash
video-gui
```

**Note:** The first run will download the Whisper "base" model (~140MB), which may take several minutes depending on your connection.

### Controls

- Click **Select Video** to open the file picker
- Select an `.mp4` file and click **Open**
- Click **Transcribe** to start processing
- Press `q`, `Ctrl+Q`, or `Ctrl+C` to quit

## Development

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[test]
pytest
```

## License

MIT
