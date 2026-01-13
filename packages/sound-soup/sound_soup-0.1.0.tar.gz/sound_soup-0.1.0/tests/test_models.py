"""
Tests for AudioTag model.
"""

import pytest
import os
import tempfile
from pydub import AudioSegment
from sound_soup.models import AudioTag
from sound_soup.exceptions import ExportError


def create_test_audio(duration_seconds: int = 10) -> str:
    """Create a test audio file."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.close()
    
    # Create silent audio segment
    audio = AudioSegment.silent(duration=duration_seconds * 1000)
    audio.export(temp_file.name, format="mp3")
    
    return temp_file.name


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
    audio_path = create_test_audio(duration_seconds=20)
    
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
    audio_path = create_test_audio()
    
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

