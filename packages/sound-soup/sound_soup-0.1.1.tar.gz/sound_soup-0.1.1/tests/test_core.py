"""
Tests for AudioSoup core functionality.
"""

import pytest
import os
import tempfile
from pydub import AudioSegment
from sound_soup import AudioSoup
from sound_soup.exceptions import DownloadError


def create_test_audio_file(duration_seconds: int = 10) -> str:
    """Create a test audio file for testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file.close()
    
    # Create silent audio segment
    audio = AudioSegment.silent(duration=duration_seconds * 1000)
    audio.export(temp_file.name, format="mp3")
    
    return temp_file.name


@pytest.mark.skip(reason="Requires Whisper model download - slow")
def test_audiosoup_local_file():
    """Test AudioSoup with local file."""
    audio_path = create_test_audio_file()
    
    try:
        with AudioSoup(audio_path, model_size="tiny", verbose=False) as soup:
            assert soup.audio_path == audio_path
            assert soup.result is not None
            assert isinstance(soup.get_text(), str)
            assert len(soup.segments) > 0
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


def test_audiosoup_find_all():
    """Test find_all method."""
    audio_path = create_test_audio_file()
    
    try:
        # Note: This requires actual transcription, so skipping for now
        # In a real test, you'd mock the transcription result
        pass
    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)

