"""
Edge TTS Service - Cloud-based text-to-speech for production

A lightweight, cloud-based TTS solution that works in serverless environments.
Uses Microsoft Edge's text-to-speech API (free, no API key required).
"""

import asyncio
import hashlib
import logging
import os
from pathlib import Path
from typing import Literal, Optional

import edge_tts

logger = logging.getLogger(__name__)

# Narrator types
NarratorType = Literal["mysterious", "epic", "horror", "comedic", "romantic"]
VoiceGender = Literal["male", "female"]

# Narrator speed settings (1.0 = normal, <1.0 = slower, >1.0 = faster)
NARRATOR_SPEED = {
    "mysterious": 0.85,  # Slow and deliberate
    "epic": 0.95,  # Slightly slower for gravitas
    "horror": 0.80,  # Very slow and suspenseful
    "comedic": 1.15,  # Faster and energetic
    "romantic": 0.90,  # Slow and intimate
}

# Edge TTS voices for English
EDGE_VOICES = {
    "male": "en-US-GuyNeural",
    "female": "en-US-JennyNeural",
}

# Urdu voices
EDGE_VOICES_URDU = {
    "male": "ur-PK-AsadNeural",
    "female": "ur-PK-UzmaNeural",
}


class EdgeTTSService:
    """Edge TTS service for cloud-based text-to-speech."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize Edge TTS service.
        
        Args:
            cache_dir: Directory to cache generated audio files (uses /tmp in serverless)
        """
        # Use /tmp in serverless environments (Vercel, AWS Lambda, etc.)
        if cache_dir is None:
            cache_dir = Path("/tmp/tts") if os.path.exists("/tmp") else Path("cache/tts")
        
        self.cache_dir = cache_dir
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Edge TTS service initialized with cache: {self.cache_dir}")
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not create cache directory: {e}. Caching disabled.")
            self.cache_dir = None
    
    def _get_cache_path(self, text: str, language: str, gender: str, narrator: Optional[str] = None) -> Optional[Path]:
        """Generate cache file path based on input parameters."""
        if not self.cache_dir:
            return None
        cache_key = f"{text}_{language}_{gender}_{narrator}"
        file_hash = hashlib.md5(cache_key.encode()).hexdigest()
        return self.cache_dir / f"{file_hash}.mp3"
    
    def _get_voice(self, language: str, gender: VoiceGender) -> str:
        """Get appropriate voice for language and gender."""
        if language.lower() in ["urdu", "ur"]:
            return EDGE_VOICES_URDU[gender]
        return EDGE_VOICES[gender]
    
    def _get_rate(self, narrator: Optional[NarratorType] = None) -> str:
        """Get speech rate string for Edge TTS."""
        if narrator and narrator in NARRATOR_SPEED:
            speed = NARRATOR_SPEED[narrator]
            # Convert to percentage (+/-50%)
            rate_percent = int((speed - 1.0) * 100)
            return f"{rate_percent:+d}%"
        return "+0%"
    
    async def generate_speech_async(
        self,
        text: str,
        language: str = "english",
        gender: VoiceGender = "female",
        narrator: Optional[NarratorType] = None,
    ) -> bytes:
        """
        Generate speech audio from text asynchronously.
        
        Args:
            text: Text to convert to speech
            language: Language ("english" or "urdu")
            gender: Voice gender ("male" or "female")
            narrator: Narrator persona for speed adjustment
            
        Returns:
            Audio data as bytes (MP3 format)
        """
        # Check cache first
        cache_path = self._get_cache_path(text, language, gender, narrator)
        if cache_path and cache_path.exists():
            logger.info(f"Using cached audio: {cache_path.name}")
            return cache_path.read_bytes()
        
        # Generate new audio
        voice = self._get_voice(language, gender)
        rate = self._get_rate(narrator)
        
        logger.info(f"Generating speech with voice={voice}, rate={rate}")
        
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        
        # Save to cache if available
        if cache_path:
            try:
                await communicate.save(str(cache_path))
                logger.info(f"Audio generated and cached: {cache_path.name}")
                return cache_path.read_bytes()
            except (OSError, PermissionError) as e:
                logger.warning(f"Could not cache audio: {e}. Returning without cache.")
        
        # If no cache, generate and return audio bytes directly
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]
        
        logger.info("Audio generated without caching")
        return audio_bytes
    
    def generate_speech(
        self,
        text: str,
        language: str = "english",
        gender: VoiceGender = "female",
        narrator: Optional[NarratorType] = None,
    ) -> bytes:
        """
        Generate speech audio from text (synchronous wrapper).
        
        Args:
            text: Text to convert to speech
            language: Language ("english" or "urdu")
            gender: Voice gender ("male" or "female")
            narrator: Narrator persona for speed adjustment
            
        Returns:
            Audio data as bytes (MP3 format)
        """
        return asyncio.run(self.generate_speech_async(text, language, gender, narrator))
    
    def list_supported_languages(self) -> list[str]:
        """List supported languages."""
        return ["english", "urdu"]


# Singleton instance
_edge_tts_service: Optional[EdgeTTSService] = None


def get_edge_tts_service(cache_dir: Optional[Path] = None) -> EdgeTTSService:
    """Get or create Edge TTS service singleton."""
    global _edge_tts_service
    if _edge_tts_service is None:
        _edge_tts_service = EdgeTTSService(cache_dir)
    return _edge_tts_service
