# Audio Text

CLI tool to transcribe YouTube videos to text, designed for IELTS listening practice.

## Features

- Transcribe YouTube videos to text with timestamps
- Uses OpenAI Whisper for accurate speech-to-text
- Automatic audio chunking for long videos (up to 30 minutes)
- Interactive menu or direct CLI commands
- Export transcripts to TXT or JSON
- Local caching to avoid re-processing

## Installation

### Using Homebrew (macOS)

```bash
brew tap anhtt2211/tap
brew install audio-text-cli
```

### Using pip

```bash
pip install audio-text-cli
```

### Prerequisites

- Python 3.10+
- ffmpeg (required for audio processing)

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

## Usage

### Interactive Mode

Simply run without arguments to get an interactive menu:

```bash
audio-text
```

```
╭──────────────────────────────────────────────────────────────────────────────╮
│  ╔═╗┬ ┬┌┬┐┬┌─┐  ╔╦╗┌─┐─┐ ┬┌┬┐                                                │
│  ╠═╣│ │ ││││ │   ║ ├┤ ┌┴┬┘ │                                                 │
│  ╩ ╩└─┘─┴┘┴└─┘   ╩ └─┘┴ └─ ┴                                                 │
│                                                                              │
│ YouTube Video Transcription for IELTS Practice                               │
╰──────────────────────────────────────────────────────────────────────────────╯

  [1]    Transcribe a YouTube video
  [2]    List saved transcripts
  [3]    View a transcript
  [4]    Export transcript to file
  [5]    Delete a transcript
  [q]    Quit
```

### Direct Commands

```bash
# Transcribe a video
audio-text transcribe https://youtube.com/watch?v=VIDEO_ID

# Transcribe with custom output directory
audio-text transcribe https://youtu.be/VIDEO_ID --output ./my-transcripts

# List saved transcripts
audio-text list

# View a transcript
audio-text view VIDEO_ID

# Export transcript (auto-generates filename from title)
audio-text export VIDEO_ID

# Export with custom filename
audio-text export VIDEO_ID ./output.txt --format txt

# Delete a transcript
audio-text delete VIDEO_ID
```

## Output Example

```
╭────────────────────────────── Transcript Info ───────────────────────────────╮
│    Title: Example Video Title                                                │
│      URL: https://www.youtube.com/watch?v=VIDEO_ID                           │
│ Duration: 5m 30s                                                             │
│ Segments: 45                                                                 │
│    Model: small                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

[00:00 -> 00:05] Hello and welcome to this video.
[00:05 -> 00:12] Today we're going to discuss...
```

## Configuration

Transcripts are saved to `~/.audio-text/transcripts/` by default.

Use `--output` or `-o` to specify a custom directory.

## Limitations

- Maximum video duration: 30 minutes
- English language only
- YouTube videos only (for now)

## Development

```bash
# Clone the repository
git clone https://github.com/anhtt2211/audio-text.git
cd audio-text

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

Anh Tran ([@anhtt2211](https://github.com/anhtt2211))
