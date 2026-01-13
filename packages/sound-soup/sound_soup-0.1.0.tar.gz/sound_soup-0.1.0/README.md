# 🥣 sound-soup

Parse audio like you parse HTML with BeautifulSoup.

## Installation

```bash
pip install sound-soup
```

**System Requirements:**
- FFmpeg ([installation guide](https://ffmpeg.org/download.html))

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

**v0.1.0-alpha** - Experimental release

- ✅ Core functionality working
- ✅ Memory-efficient lazy loading
- ✅ Context manager support
- ⚠️ API may change in future versions
- ⚠️ Not recommended for production yet

## Requirements

- Python 3.9+
- FFmpeg (for audio processing)
- ~140MB disk space for base Whisper model (2.9GB for large model)

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR on GitHub.

