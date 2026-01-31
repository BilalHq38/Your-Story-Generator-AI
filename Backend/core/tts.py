"""
Text-to-Speech service using Meta MMS-TTS (local model).

This module provides a simple interface for text-to-speech using the locally
running Meta MMS-TTS model which supports 1,100+ languages including English and Urdu.
"""

import hashlib
import logging
from pathlib import Path
from typing import Literal, Optional

from ai.mms_tts import get_mms_tts_service, NarratorType

logger = logging.getLogger(__name__)


# Voice gender type (for API compatibility)
VoiceGender = Literal["male", "female"]

# Re-export NarratorType for compatibility
__all__ = ["TTSService", "VoiceGender", "NarratorType"]


class TTSService:
    """
    Text-to-Speech service using Meta MMS-TTS.
    
    This service provides high-quality, multilingual text-to-speech
    using the locally running MMS-TTS model. No API keys or rate limits.
    """
    
    _instance: Optional["TTSService"] = None
    
    def __init__(self):
        self._mms_service = get_mms_tts_service()
        logger.info("TTS Service initialized with MMS-TTS backend")
    
    @classmethod
    def get_instance(cls) -> "TTSService":
        """Get singleton instance of TTSService."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,  # Ignored for MMS-TTS (single voice per language)
        gender: Optional[VoiceGender] = None,  # Ignored for MMS-TTS
        narrator: Optional[NarratorType] = None,
        rate: Optional[str] = None,  # Ignored, use speed instead
        pitch: Optional[str] = None,  # Ignored
        language: str = "english",
        speed: Optional[float] = None,
        **kwargs,  # Ignore other params for backward compatibility
    ) -> tuple[bytes, str]:
        """
        Generate speech from text using MMS-TTS.
        
        Args:
            text: Text to convert to speech
            voice: Ignored (MMS-TTS has one voice per language)
            gender: Ignored (MMS-TTS has one voice per language)
            narrator: Narrator persona (affects speech speed)
            rate: Ignored (use speed parameter instead)
            pitch: Ignored (not supported by MMS-TTS)
            language: Language name or code (english, urdu, etc.)
            speed: Speech speed multiplier (0.5-2.0)
        
        Returns:
            Tuple of (audio_bytes, content_type)
        """
        logger.info(f"TTS request: language={language}, narrator={narrator}, {len(text)} chars")
        
        audio_bytes = await self._mms_service.synthesize(
            text=text,
            language=language,
            narrator=narrator,
            speed=speed,
        )
        
        return audio_bytes, "audio/wav"
    
    def list_supported_languages(self) -> list[str]:
        """List all supported languages."""
        return self._mms_service.list_supported_languages()
    
    def clear_cache(self):
        """Clear the audio cache."""
        self._mms_service.clear_cache()
    
    def unload_models(self):
        """Unload all models to free memory."""
        self._mms_service.unload_models()


# Convenience function
def get_tts_service() -> TTSService:
    """Get the TTS service singleton."""
    return TTSService.get_instance()


# Backward-compatible function for generating speech
async def generate_speech(
    text: str,
    language: str = "english",
    narrator: Optional[NarratorType] = None,
    speed: Optional[float] = None,
    **kwargs,
) -> bytes:
    """
    Generate speech from text.
    
    Args:
        text: Text to convert to speech
        language: Language name or code
        narrator: Narrator persona
        speed: Speech speed multiplier
    
    Returns:
        WAV audio bytes
    """
    service = get_tts_service()
    audio_bytes, _ = await service.synthesize(
        text=text,
        language=language,
        narrator=narrator,
        speed=speed,
    )
    return audio_bytes
