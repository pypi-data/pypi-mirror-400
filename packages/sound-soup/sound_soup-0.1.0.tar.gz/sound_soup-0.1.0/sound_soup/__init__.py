"""
sound-soup: Parse audio like HTML
"""

__version__ = "0.1.0"

from .core import AudioSoup
from .models import AudioTag
from .exceptions import SoundSoupError, DownloadError, TranscriptionError

__all__ = [
    "AudioSoup",
    "AudioTag",
    "SoundSoupError",
    "DownloadError",
    "TranscriptionError",
]

