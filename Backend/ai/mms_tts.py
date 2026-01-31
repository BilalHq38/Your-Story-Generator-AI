"""
Meta MMS-TTS (Massively Multilingual Speech) Text-to-Speech Service

A local, high-quality multilingual TTS model that supports:
- 1,100+ languages including English and Urdu
- Fast CPU inference
- No API limits or costs
- Automatic model downloading from Hugging Face

Model: facebook/mms-tts-*
"""

import io
import wave
import hashlib
import logging
from pathlib import Path
from typing import Optional, Literal

import numpy as np
import torch
from transformers import VitsModel, AutoTokenizer

logger = logging.getLogger(__name__)

# Narrator types for voice styling
NarratorType = Literal["mysterious", "epic", "horror", "comedic", "romantic"]

# Language codes for MMS-TTS models
# Format: language_name -> (model_id, language_code)
LANGUAGE_MODELS = {
    "english": ("facebook/mms-tts-eng", "eng"),
    "urdu": ("facebook/mms-tts-urd", "urd"),
    "hindi": ("facebook/mms-tts-hin", "hin"),
    "arabic": ("facebook/mms-tts-ara", "ara"),
    "spanish": ("facebook/mms-tts-spa", "spa"),
    "french": ("facebook/mms-tts-fra", "fra"),
    "german": ("facebook/mms-tts-deu", "deu"),
    "italian": ("facebook/mms-tts-ita", "ita"),
    "portuguese": ("facebook/mms-tts-por", "por"),
    "russian": ("facebook/mms-tts-rus", "rus"),
    "chinese": ("facebook/mms-tts-cmn", "cmn"),
    "japanese": ("facebook/mms-tts-jpn", "jpn"),
    "korean": ("facebook/mms-tts-kor", "kor"),
    "turkish": ("facebook/mms-tts-tur", "tur"),
    "dutch": ("facebook/mms-tts-nld", "nld"),
    "polish": ("facebook/mms-tts-pol", "pol"),
    "bengali": ("facebook/mms-tts-ben", "ben"),
    "tamil": ("facebook/mms-tts-tam", "tam"),
    "punjabi": ("facebook/mms-tts-pan", "pan"),
}

# Speech rate adjustments per narrator (applied via audio resampling)
NARRATOR_SPEED = {
    "mysterious": 0.9,   # Slower, deliberate
    "epic": 1.1,         # Slightly faster, energetic
    "horror": 0.85,      # Very slow, building tension
    "comedic": 1.15,     # Faster, upbeat
    "romantic": 0.95,    # Slower, gentle
}


class MMSTTSService:
    """
    Meta MMS-TTS Text-to-Speech Service
    
    Provides high-quality, multilingual text-to-speech using Facebook's
    Massively Multilingual Speech TTS models.
    """
    
    _instance: Optional["MMSTTSService"] = None
    _models: dict = {}  # Cache loaded models by language
    _tokenizers: dict = {}  # Cache tokenizers by language
    
    def __init__(self):
        self._cache_dir = Path(__file__).parent.parent / "cache" / "tts"
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"MMS-TTS will use device: {self._device}")
    
    @classmethod
    def get_instance(cls) -> "MMSTTSService":
        """Get singleton instance of MMSTTSService."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _get_model_id(self, language: str) -> tuple[str, str]:
        """Get the model ID for a language."""
        lang_lower = language.lower()
        
        # Direct match
        if lang_lower in LANGUAGE_MODELS:
            return LANGUAGE_MODELS[lang_lower]
        
        # Check if it's a language code
        for lang_name, (model_id, code) in LANGUAGE_MODELS.items():
            if code == lang_lower:
                return (model_id, code)
        
        # Default to English
        logger.warning(f"Unsupported language '{language}', defaulting to English")
        return LANGUAGE_MODELS["english"]
    
    def _load_model(self, language: str) -> tuple[VitsModel, AutoTokenizer]:
        """Load model and tokenizer for a language (lazy loading)."""
        model_id, lang_code = self._get_model_id(language)
        
        if lang_code in self._models:
            return self._models[lang_code], self._tokenizers[lang_code]
        
        logger.info(f"Loading MMS-TTS model for {language}: {model_id}")
        
        try:
            # Load model and tokenizer
            model = VitsModel.from_pretrained(model_id)
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            
            # Move to device
            model = model.to(self._device)
            
            # Cache for reuse
            self._models[lang_code] = model
            self._tokenizers[lang_code] = tokenizer
            
            logger.info(f"MMS-TTS model loaded successfully: {model_id}")
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"Failed to load MMS-TTS model: {e}")
            raise RuntimeError(f"Failed to load MMS-TTS model: {e}")
    
    def _get_cache_key(self, text: str, language: str, speed: float) -> str:
        """Generate cache key for audio."""
        content = f"{text}:{language}:{speed}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_audio(self, cache_key: str) -> Optional[bytes]:
        """Get cached audio if exists."""
        cache_path = self._cache_dir / f"{cache_key}.wav"
        if cache_path.exists():
            return cache_path.read_bytes()
        return None
    
    def _save_to_cache(self, cache_key: str, audio_data: bytes):
        """Save audio to cache."""
        cache_path = self._cache_dir / f"{cache_key}.wav"
        cache_path.write_bytes(audio_data)
        logger.info(f"Cached audio: {cache_key}.wav")
    
    def _numpy_to_wav(self, audio_array: np.ndarray, sample_rate: int = 16000) -> bytes:
        """Convert numpy audio array to WAV bytes."""
        # Normalize to int16
        audio_array = np.clip(audio_array, -1.0, 1.0)
        audio_int16 = (audio_array * 32767).astype(np.int16)
        
        # Create WAV file in memory
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
        
        buffer.seek(0)
        return buffer.read()
    
    def _adjust_speed(self, audio: np.ndarray, speed: float, sample_rate: int = 16000) -> tuple[np.ndarray, int]:
        """Adjust audio speed by resampling."""
        if speed == 1.0:
            return audio, sample_rate
        
        from scipy import signal
        
        # Calculate new sample rate to achieve speed change
        new_length = int(len(audio) / speed)
        resampled = signal.resample(audio, new_length)
        
        return resampled, sample_rate
    
    async def synthesize(
        self,
        text: str,
        language: str = "english",
        narrator: Optional[NarratorType] = None,
        speed: Optional[float] = None,
    ) -> bytes:
        """
        Generate speech from text using MMS-TTS.
        
        Args:
            text: Text to convert to speech
            language: Language name or code (english, urdu, etc.)
            narrator: Narrator persona for speed adjustment
            speed: Speech speed multiplier (0.5-2.0)
        
        Returns:
            WAV audio bytes
        """
        # Get speed from narrator profile or use default
        if speed is None and narrator:
            speed = NARRATOR_SPEED.get(narrator, 1.0)
        elif speed is None:
            speed = 1.0
        
        # Check cache
        cache_key = self._get_cache_key(text, language, speed)
        cached = self._get_cached_audio(cache_key)
        if cached:
            logger.info(f"Using cached audio: {cache_key}.wav")
            return cached
        
        # Load model
        model, tokenizer = self._load_model(language)
        
        logger.info(f"Generating MMS-TTS speech: language={language}, narrator={narrator}, speed={speed}")
        
        try:
            # Tokenize input
            inputs = tokenizer(text, return_tensors="pt").to(self._device)
            
            # Generate speech
            with torch.no_grad():
                output = model(**inputs).waveform
            
            # Convert to numpy
            audio_array = output.squeeze().cpu().numpy()
            
            # Adjust speed if needed
            sample_rate = model.config.sampling_rate
            if speed != 1.0:
                audio_array, sample_rate = self._adjust_speed(audio_array, speed, sample_rate)
            
            # Convert to WAV bytes
            audio_bytes = self._numpy_to_wav(audio_array, sample_rate)
            
            # Cache the result
            self._save_to_cache(cache_key, audio_bytes)
            
            return audio_bytes
            
        except Exception as e:
            logger.error(f"MMS-TTS generation failed: {e}")
            raise RuntimeError(f"Failed to generate speech: {e}")
    
    def list_supported_languages(self) -> list[str]:
        """List all supported languages."""
        return list(LANGUAGE_MODELS.keys())
    
    def clear_cache(self):
        """Clear the audio cache."""
        for cache_file in self._cache_dir.glob("*.wav"):
            cache_file.unlink()
        logger.info("TTS cache cleared")
    
    def unload_models(self):
        """Unload all cached models to free memory."""
        self._models.clear()
        self._tokenizers.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("All MMS-TTS models unloaded")


# Singleton accessor
def get_mms_tts_service() -> MMSTTSService:
    """Get the MMS-TTS service singleton."""
    return MMSTTSService.get_instance()


# Convenience function for direct use
async def generate_speech(
    text: str,
    language: str = "english",
    narrator: Optional[NarratorType] = None,
    speed: Optional[float] = None,
) -> bytes:
    """
    Generate speech from text using MMS-TTS.
    
    This is a convenience wrapper around MMSTTSService.synthesize().
    
    Args:
        text: Text to convert to speech
        language: Language name or code
        narrator: Narrator persona
        speed: Speech speed multiplier
    
    Returns:
        WAV audio bytes
    """
    service = get_mms_tts_service()
    return await service.synthesize(
        text=text,
        language=language,
        narrator=narrator,
        speed=speed,
    )
