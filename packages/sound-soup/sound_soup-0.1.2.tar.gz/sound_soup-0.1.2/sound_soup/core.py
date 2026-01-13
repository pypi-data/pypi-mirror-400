"""
Core AudioSoup class - the main API for parsing audio.
"""

import os
import tempfile
import shutil
from typing import List, Optional, Union
import whisper
import yt_dlp
from pydub import AudioSegment

from .models import AudioTag
from .exceptions import DownloadError, TranscriptionError


class AudioSoup:
    """
    BeautifulSoup-style API for audio transcription and analysis.
    
    Usage:
        >>> with AudioSoup("https://youtube.com/watch?v=...") as soup:
        ...     matches = soup.find_all(text="keyword")
        ...     matches[0].export("clip.mp3")
    """
    
    def __init__(
        self,
        source: Union[str, os.PathLike],
        model_size: str = "base",
        verbose: bool = True,
        temp_dir: Optional[str] = None
    ):
        """
        Initialize AudioSoup with a source URL or file path.
        
        Args:
            source: YouTube URL or path to audio file
            model_size: Whisper model size (tiny, base, small, medium, large)
            verbose: Whether to print progress messages
            temp_dir: Directory for temporary files (auto-cleaned on exit)
        """
        self.source = source
        self.model_size = model_size
        self.verbose = verbose
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix="sound_soup_")
        self._cleanup_temp = temp_dir is None  # Only cleanup if we created the dir
        
        self.audio_path: Optional[str] = None
        self.result: Optional[dict] = None
        self.model = None
        self._segments: Optional[List[AudioTag]] = None
        
        # Initialize immediately
        self._initialize()
    
    def _initialize(self):
        """Download/load audio and transcribe."""
        try:
            if self.verbose:
                print(f"🥣 Downloading audio...")
            self.audio_path = self._resolve_source(self.source)
            
            if self.verbose:
                print(f"🤖 Loading Whisper '{self.model_size}' model...")
            self.model = whisper.load_model(self.model_size)
            
            if self.verbose:
                print(f"🎤 Transcribing audio...")
            self.result = self.model.transcribe(
                self.audio_path,
                verbose=self.verbose
            )
            
            if self.verbose:
                print(f"✅ Transcription complete!")
                
        except Exception as e:
            if isinstance(e, (DownloadError, TranscriptionError)):
                raise
            raise TranscriptionError(f"Failed to transcribe audio: {e}")
    
    def _resolve_source(self, source: Union[str, os.PathLike]) -> str:
        """
        Resolve source to a local audio file path.
        
        If source is a URL, downloads it. If it's a file path, validates it.
        """
        source_str = str(source)
        
        # Check if it's a URL
        if source_str.startswith(("http://", "https://", "www.")):
            return self._download_from_url(source_str)
        
        # Otherwise, treat as file path
        if not os.path.exists(source_str):
            raise DownloadError(f"Audio file not found: {source_str}")
        
        return source_str
    
    def _download_from_url(self, url: str) -> str:
        """Download audio from YouTube or other supported URLs."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
            'quiet': not self.verbose,
            'no_warnings': True,
            'extractaudio': True,
            'audioformat': 'mp3',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # Find the downloaded file
                filename = ydl.prepare_filename(info)
                # yt-dlp adds extension, but postprocessor changes it to mp3
                base_name = os.path.splitext(filename)[0]
                audio_path = f"{base_name}.mp3"
                
                if os.path.exists(audio_path):
                    return audio_path
                
                # Fallback: search for any audio file in temp_dir
                for file in os.listdir(self.temp_dir):
                    if file.endswith(('.mp3', '.m4a', '.webm', '.ogg')):
                        return os.path.join(self.temp_dir, file)
                
                raise DownloadError(f"Downloaded file not found for {url}")
                
        except Exception as e:
            if isinstance(e, DownloadError):
                raise
            raise DownloadError(f"Failed to download {url}: {e}")
    
    def _build_segments(self) -> List[AudioTag]:
        """Build AudioTag objects from transcription result."""
        if self.result is None:
            return []
        
        segments = []
        for segment in self.result.get("segments", []):
            tag = AudioTag(
                text=segment.get("text", "").strip(),
                start=segment.get("start", 0),
                end=segment.get("end", 0),
                _source_audio_path=self.audio_path
            )
            segments.append(tag)
        
        return segments
    
    @property
    def segments(self) -> List[AudioTag]:
        """Get all transcription segments as AudioTag objects."""
        if self._segments is None:
            self._segments = self._build_segments()
        return self._segments
    
    def get_text(self) -> str:
        """Get the full transcription text."""
        if self.result is None:
            return ""
        return self.result.get("text", "").strip()
    
    def find_all(self, text: str, case_sensitive: bool = False) -> List[AudioTag]:
        """
        Find all segments containing the given text.
        
        Args:
            text: Text to search for
            case_sensitive: Whether search should be case-sensitive
        
        Returns:
            List of AudioTag objects matching the search
        """
        matches = []
        search_text = text if case_sensitive else text.lower()
        
        for segment in self.segments:
            segment_text = segment.text if case_sensitive else segment.text.lower()
            if search_text in segment_text:
                matches.append(segment)
        
        return matches
    
    def find(self, text: str, case_sensitive: bool = False) -> Optional[AudioTag]:
        """
        Find the first segment containing the given text.
        
        Args:
            text: Text to search for
            case_sensitive: Whether search should be case-sensitive
        
        Returns:
            First matching AudioTag or None
        """
        matches = self.find_all(text, case_sensitive=case_sensitive)
        return matches[0] if matches else None
    
    def cleanup(self):
        """Clean up temporary files."""
        if self._cleanup_temp and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                if self.verbose:
                    print(f"🧹 Cleaned up temporary files")
            except Exception as e:
                if self.verbose:
                    print(f"⚠️  Warning: Failed to cleanup temp dir: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - auto cleanup."""
        self.cleanup()
    
    def __repr__(self) -> str:
        return f"AudioSoup(source='{self.source}', segments={len(self.segments)})"

