"""
Custom exceptions for sound-soup.
"""


class SoundSoupError(Exception):
    """Base exception for sound-soup."""
    pass


class DownloadError(SoundSoupError):
    """Raised when audio download fails."""
    pass


class TranscriptionError(SoundSoupError):
    """Raised when transcription fails."""
    pass


class ExportError(SoundSoupError):
    """Raised when audio export fails."""
    pass

