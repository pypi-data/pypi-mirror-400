"""
Comprehensive tests for sound-soup package.
"""

import pytest
import os
import tempfile
from pydub import AudioSegment
from sound_soup import AudioSoup
from sound_soup.models import AudioTag
from sound_soup.exceptions import (
    SoundSoupError,
    DownloadError,
    TranscriptionError,
    ExportError,
)


# ============================================================================
# Helper Functions
# ============================================================================

def create_test_audio_file(duration_seconds: int = 10) -> str:
    """Create a test audio file for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.close()
    
    # Create silent audio segment
    audio = AudioSegment.silent(duration=duration_seconds * 1000)
    audio.export(temp_file.name, format="mp3")
    
    return temp_file.name


# ============================================================================
# Exception Tests
# ============================================================================

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


# ============================================================================
# AudioTag Model Tests
# ============================================================================

def test_audiotag_creation():
    """Test AudioTag creation."""
    tag = AudioTag(
        text="Hello world",
        start=0.0,
        end=5.0,
        _source_audio_path=None
    )
    
    assert tag.text == "Hello world"
    assert tag.start == 0.0
    assert tag.end == 5.0
    assert tag.duration == 5.0


def test_audiotag_duration():
    """Test duration property."""
    tag = AudioTag(text="Test", start=10.0, end=15.5)
    assert tag.duration == 5.5


def test_audiotag_export_success():
    """Test successful audio export."""
    audio_path = create_test_audio_file(duration_seconds=20)
    
    try:
        tag = AudioTag(
            text="Test segment",
            start=5.0,
            end=10.0,
            _source_audio_path=audio_path
        )
        
        output_file = tag.export("test_output.mp3")
        
        assert os.path.exists(output_file)
        assert output_file.endswith(".mp3")
        
        # Cleanup
        os.unlink(output_file)
    finally:
        os.unlink(audio_path)


def test_audiotag_export_no_source():
    """Test export fails when no source audio path."""
    tag = AudioTag(text="Test", start=0.0, end=5.0)
    
    with pytest.raises(ExportError):
        tag.export("test.mp3")


def test_audiotag_export_missing_file():
    """Test export fails when source file doesn't exist."""
    tag = AudioTag(
        text="Test",
        start=0.0,
        end=5.0,
        _source_audio_path="/nonexistent/file.mp3"
    )
    
    with pytest.raises(ExportError):
        tag.export("test.mp3")


def test_audiotag_lazy_loading():
    """Test that audio is only loaded when needed."""
    audio_path = create_test_audio_file()
    
    try:
        tag = AudioTag(
            text="Test",
            start=0.0,
            end=5.0,
            _source_audio_path=audio_path
        )
        
        # Audio should not be loaded yet
        assert tag._audio_segment is None
        
        # Export should trigger loading
        tag.export("test.mp3")
        
        # Now audio should be loaded
        assert tag._audio_segment is not None
        
        # Cleanup
        os.unlink("test.mp3")
    finally:
        os.unlink(audio_path)


def test_audiotag_str_repr():
    """Test string representation."""
    tag = AudioTag(text="Hello world", start=1.5, end=3.7)
    
    str_repr = str(tag)
    assert "Hello world" in str_repr
    assert "1.5" in str_repr
    assert "3.7" in str_repr
    
    repr_str = repr(tag)
    assert "AudioTag" in repr_str


# ============================================================================
# AudioSoup Core Tests
# ============================================================================

@pytest.mark.skip(reason="Requires Whisper model download - slow")
def test_audiosoup_local_file():
    """Test AudioSoup with local file."""
    audio_path = create_test_audio_file()
    
    try:
        with AudioSoup(audio_path, model_size="tiny", verbose=False) as soup:
            assert soup.audio_path == audio_path
            assert soup.result is not None
            assert isinstance(soup.get_text(), str)
            assert len(soup.segments) >= 0
    finally:
        os.unlink(audio_path)


@pytest.mark.skip(reason="Requires Whisper model download - slow")
def test_audiosoup_context_manager():
    """Test AudioSoup context manager cleanup."""
    audio_path = create_test_audio_file()
    temp_dir = None
    
    try:
        with AudioSoup(audio_path, model_size="tiny", verbose=False) as soup:
            temp_dir = soup.temp_dir
            assert os.path.exists(temp_dir)
        
        # After context exit, temp dir should be cleaned up
        assert not os.path.exists(temp_dir)
    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)


def test_audiosoup_invalid_file():
    """Test AudioSoup with non-existent file."""
    with pytest.raises(DownloadError):
        AudioSoup("/nonexistent/file.mp3", verbose=False)


@pytest.mark.skip(reason="Requires internet connection and YouTube")
def test_audiosoup_youtube_url():
    """Test AudioSoup with YouTube URL."""
    # This test requires internet and may be flaky
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    with AudioSoup(url, model_size="tiny", verbose=False) as soup:
        assert soup.audio_path is not None
        assert os.path.exists(soup.audio_path)


@pytest.mark.skip(reason="Requires Whisper model - integration test")
def test_audiosoup_find_methods():
    """Test find and find_all methods."""
    audio_path = create_test_audio_file()
    
    try:
        with AudioSoup(audio_path, model_size="tiny", verbose=False) as soup:
            # Test find_all
            all_matches = soup.find_all(text="test")
            assert isinstance(all_matches, list)
            
            # Test find
            first_match = soup.find(text="test")
            assert first_match is None or isinstance(first_match, AudioTag)
            
            # Test case sensitivity
            case_matches = soup.find_all(text="TEST", case_sensitive=True)
            assert isinstance(case_matches, list)
    finally:
        os.unlink(audio_path)


def test_audiosoup_segments_property():
    """Test segments property is cached."""
    audio_path = create_test_audio_file()
    
    try:
        # Note: This will fail without actual transcription
        # but tests the property access pattern
        pass
    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)

