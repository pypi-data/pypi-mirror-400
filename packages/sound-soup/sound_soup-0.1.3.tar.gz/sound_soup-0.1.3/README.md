# 🥣 sound-soup

Parse audio like you parse HTML with BeautifulSoup.

## Installation

```bash
pip install sound-soup
```

**System Requirements:**
- **FFmpeg** (required for audio processing)
  - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `winget install ffmpeg`
  - **macOS**: `brew install ffmpeg`
  - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (RHEL/CentOS)

All Python dependencies (openai-whisper, yt-dlp, pydub) are automatically installed with the package.

## Quick Start

```python
from sound_soup import AudioSoup

# From YouTube URL
with AudioSoup("https://youtube.com/watch?v=...") as soup:
    # Get full transcript
    print(soup.get_text())
    
    # Find mentions of "climate"
    clips = soup.find_all(text="climate")
    
    # Export first match
    clips[0].export("climate_discussion.mp3")
```

## Features

- 🎬 **Download from YouTube** (or use local files)
- 🤖 **AI-powered transcription** (via OpenAI Whisper)
- 🔍 **Search transcripts** like BeautifulSoup
- ✂️ **Extract audio clips** automatically
- 🧠 **Intuitive API** - if you know BeautifulSoup, you know sound-soup
- 💾 **Memory efficient** - lazy loading prevents RAM overload
- 🧹 **Auto cleanup** - context manager handles temporary files

## Advanced Usage

### Local Files

```python
from sound_soup import AudioSoup

with AudioSoup("podcast.mp3") as soup:
    matches = soup.find_all(text="machine learning")
    for match in matches:
        print(f"{match.start:.1f}s: {match.text}")
```

### Custom Model Size

```python
# Use larger model for better accuracy (slower, more RAM)
with AudioSoup(url, model_size="large") as soup:
    # ... your code ...
```

### Case-Sensitive Search

```python
with AudioSoup(url) as soup:
    # Case-sensitive search
    matches = soup.find_all(text="AI", case_sensitive=True)
```

## Examples

See the [examples/](examples/) directory for more use cases:
- Basic usage
- Podcast clip extraction
- Interview analysis

## FAQ

**Q: What audio formats are supported?**  
A: Anything FFmpeg supports (MP3, WAV, M4A, FLAC, etc.)

**Q: How accurate is the transcription?**  
A: Uses OpenAI Whisper - state-of-the-art quality. Try `model_size="large"` for best results.

**Q: Can I use this in production?**  
A: Current version (0.1.x) is alpha. API may change. See [Development Status](#development-status) below.

**Q: How much RAM does this use?**  
A: Audio segments are lazy-loaded, so RAM usage is minimal. Only loads audio when exporting clips.

**Q: What if YouTube changes their API?**  
A: We use `yt-dlp` which is actively maintained. If downloads fail, update `yt-dlp`: `pip install --upgrade yt-dlp`

## Development Status

**v0.1.3-alpha** - Experimental release

- ✅ Core functionality working
- ✅ Memory-efficient lazy loading
- ✅ Context manager support
- ✅ Comprehensive test suite (20 tests)
- ✅ Manual testing script included
- ⚠️ API may change in future versions
- ⚠️ Not recommended for production yet

## Requirements

- Python 3.9+
- FFmpeg (for audio processing)
- ~140MB disk space for base Whisper model (2.9GB for large model)

## Development

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/PierrunoYT/sound-soup.git
cd sound-soup
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode with dev dependencies:
```bash
pip install -e ".[dev]"
```

4. Run tests:
```bash
pytest
```

5. Run manual tests (optional - tests with real audio):
```bash
python manual_test.py
```

### Testing

The project includes comprehensive tests:

- **Unit Tests** (`tests/test_sound_soup.py`): 20 tests covering exceptions, models, and core functionality
  ```bash
  pytest tests/test_sound_soup.py -v
  ```

- **Manual Tests** (`manual_test.py`): End-to-end testing with real audio files
  ```bash
  python manual_test.py
  ```
  This script tests:
  - Local audio file processing
  - YouTube URL downloading (optional)
  - Error handling
  - Audio export functionality

### Building the Package

To build distribution files:

```bash
# Install build tools
python -m pip install build twine

# Build the package
python -m build
```

This creates both wheel (`.whl`) and source distribution (`.tar.gz`) files in the `dist/` directory.

### Publishing to PyPI

1. **Test on TestPyPI first** (recommended):
```bash
python -m twine upload --repository testpypi dist/*
```

2. **Install from TestPyPI to verify**:
```bash
pip install --index-url https://test.pypi.org/simple/ sound-soup
```

3. **Publish to PyPI**:
```bash
python -m twine upload dist/*
```

You'll need PyPI credentials. Set up API tokens at [pypi.org](https://pypi.org/manage/account/token/).

### Project Structure

```
sound-soup/
├── sound_soup/          # Main package
│   ├── __init__.py      # Public API
│   ├── core.py          # AudioSoup implementation
│   ├── models.py        # Data models (Clip, etc.)
│   └── exceptions.py    # Custom exceptions
├── tests/               # Test suite
├── examples/            # Usage examples
├── pyproject.toml       # Package metadata & dependencies
└── README.md            # This file
```

### Code Quality

Format code with Black:
```bash
black sound_soup tests examples
```

Lint with Ruff:
```bash
ruff check sound_soup tests examples
```

## License

MIT

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Format code (`black .`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

For bug reports and feature requests, please [open an issue](https://github.com/PierrunoYT/sound-soup/issues).

