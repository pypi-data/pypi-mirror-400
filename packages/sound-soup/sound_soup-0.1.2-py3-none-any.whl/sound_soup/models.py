"""
Data models for sound-soup.
"""

from dataclasses import dataclass, field
from typing import Optional
from pydub import AudioSegment
import os

from .exceptions import ExportError


@dataclass
class AudioTag:
    """
    Represents a segment of transcribed audio, similar to an HTML tag.
    
    Attributes:
        text: The transcribed text for this segment
        start: Start time in seconds
        end: End time in seconds
        _source_audio_path: Path to the source audio file (for lazy loading)
        _audio_segment: Cached AudioSegment (loaded on demand)
    """
    text: str
    start: float
    end: float
    _source_audio_path: Optional[str] = None
    _audio_segment: Optional[AudioSegment] = field(default=None, init=False, repr=False)
    
    @property
    def duration(self) -> float:
        """Duration of the audio segment in seconds."""
        return self.end - self.start
    
    def _load_audio(self) -> AudioSegment:
        """Lazy load audio segment only when needed."""
        if self._audio_segment is None:
            if self._source_audio_path is None:
                raise ExportError("No source audio path available")
            if not os.path.exists(self._source_audio_path):
                raise ExportError(f"Source audio file not found: {self._source_audio_path}")
            
            audio = AudioSegment.from_file(self._source_audio_path)
            # Convert seconds to milliseconds for pydub
            start_ms = int(self.start * 1000)
            end_ms = int(self.end * 1000)
            self._audio_segment = audio[start_ms:end_ms]
        
        return self._audio_segment
    
    def export(self, filename: Optional[str] = None, format: str = "mp3") -> str:
        """
        Export this audio segment to a file.
        
        Args:
            filename: Output filename. If None, generates from text and timestamp.
            format: Audio format (mp3, wav, m4a, etc.)
        
        Returns:
            Path to the exported file
        """
        audio = self._load_audio()
        
        if filename is None:
            # Generate filename from text (sanitized) and timestamp
            safe_text = "".join(c for c in self.text[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_text = safe_text.replace(' ', '_')
            filename = f"{safe_text}_{int(self.start)}s.{format}"
        
        # Ensure format extension matches
        if not filename.endswith(f".{format}"):
            filename = f"{filename}.{format}"
        
        try:
            audio.export(filename, format=format)
            return filename
        except Exception as e:
            raise ExportError(f"Failed to export audio: {e}")
    
    def __str__(self) -> str:
        return f"AudioTag(text='{self.text[:50]}...', start={self.start:.2f}s, end={self.end:.2f}s)"
    
    def __repr__(self) -> str:
        return f"AudioTag(text='{self.text}', start={self.start}, end={self.end})"

