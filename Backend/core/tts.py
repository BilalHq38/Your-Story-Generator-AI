"""
Text-to-Speech service using Edge TTS (cloud-based).

This module provides a simple interface for text-to-speech using Microsoft Edge's
TTS API which is lightweight and works in serverless environments.
"""

import hashlib
import logging
from pathlib import Path
from typing import Literal, Optional

from ai.edge_tts_service import get_edge_tts_service, NarratorType, VoiceGender

logger = logging.getLogger()


# Re-export types for compatibility
__all__ = ["TTSService", "VoiceGender", "NarratorType", "get_tts_service"]


class TTSService:
    """
    Text-to-Speech service using Edge TTS.
    
    This service provides high-quality, multilingual text-to-speech
    using Microsoft Edge's cloud TTS. No API keys required.
    """
    
    _instance: Optional["TTSService"] = None
    
    def __init__(self):
        self._edge_service = get_edge_tts_service()
        logger.info("TTS Service initialized with Edge TTS backend")
    
    @classmethod
    def get_instance(cls) -> "TTSService":
        """Get singleton instance of TTSService."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        gender: Optional[VoiceGender] = "female",
        narrator: Optional[NarratorType] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
        language: str = "english",
        speed: Optional[float] = None,
        **kwargs,
    ) -> tuple[bytes, str]:
        """
        Generate speech from text using Edge TTS.
        
        Args:
            text: Text to convert to speech
            voice: Ignored (voice selected by language and gender)
            gender: Voice gender (male/female)
            narrator: Narrator persona (affects speech speed)
            rate: Ignored (use narrator or speed)
            pitch: Ignored (not supported)
            language: Language name or code (english, urdu, etc.)
            speed: Speech speed multiplier (use narrator instead)
        
        Returns:
            Tuple of (audio_bytes, content_type)
        """
        logger.info(f"TTS request: language={language}, gender={gender}, narrator={narrator}, {len(text)} chars")
        
        audio_bytes = await self._edge_service.generate_speech_async(
            text=text,
            language=language,
            gender=gender or "female",
            narrator=narrator,
        )
        
        return audio_bytes, "audio/mpeg"
    
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
