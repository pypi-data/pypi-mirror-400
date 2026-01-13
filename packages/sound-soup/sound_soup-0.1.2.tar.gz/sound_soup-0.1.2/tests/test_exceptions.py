"""
Tests for sound-soup exceptions.
"""

import pytest
from sound_soup.exceptions import (
    SoundSoupError,
    DownloadError,
    TranscriptionError,
    ExportError,
)


def test_sound_soup_error_base():
    """Test that SoundSoupError is a base exception."""
    error = SoundSoupError("Test error")
    assert isinstance(error, Exception)
    assert str(error) == "Test error"


def test_download_error_inheritance():
    """Test that DownloadError inherits from SoundSoupError."""
    error = DownloadError("Download failed")
    assert isinstance(error, SoundSoupError)
    assert isinstance(error, Exception)
    assert str(error) == "Download failed"


def test_transcription_error_inheritance():
    """Test that TranscriptionError inherits from SoundSoupError."""
    error = TranscriptionError("Transcription failed")
    assert isinstance(error, SoundSoupError)
    assert isinstance(error, Exception)
    assert str(error) == "Transcription failed"


def test_export_error_inheritance():
    """Test that ExportError inherits from SoundSoupError."""
    error = ExportError("Export failed")
    assert isinstance(error, SoundSoupError)
    assert isinstance(error, Exception)
    assert str(error) == "Export failed"


def test_exception_hierarchy():
    """Test that all exceptions are properly related."""
    download_error = DownloadError("test")
    transcription_error = TranscriptionError("test")
    export_error = ExportError("test")
    
    # All should be SoundSoupError instances
    assert isinstance(download_error, SoundSoupError)
    assert isinstance(transcription_error, SoundSoupError)
    assert isinstance(export_error, SoundSoupError)
    
    # But not instances of each other
    assert not isinstance(download_error, TranscriptionError)
    assert not isinstance(download_error, ExportError)
    assert not isinstance(transcription_error, DownloadError)
    assert not isinstance(transcription_error, ExportError)
    assert not isinstance(export_error, DownloadError)
    assert not isinstance(export_error, TranscriptionError)


def test_exception_with_cause():
    """Test exceptions can be raised with a cause."""
    original_error = ValueError("Original error")
    
    download_error = DownloadError("Download failed")
    download_error.__cause__ = original_error
    
    assert download_error.__cause__ == original_error


def test_exception_can_be_caught_by_base():
    """Test that specific exceptions can be caught by base exception."""
    try:
        raise DownloadError("Test")
    except SoundSoupError as e:
        assert isinstance(e, DownloadError)
        assert str(e) == "Test"
    
    try:
        raise TranscriptionError("Test")
    except SoundSoupError as e:
        assert isinstance(e, TranscriptionError)
        assert str(e) == "Test"
    
    try:
        raise ExportError("Test")
    except SoundSoupError as e:
        assert isinstance(e, ExportError)
        assert str(e) == "Test"

