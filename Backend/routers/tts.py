"""TTS (Text-to-Speech) router - Endpoints for audio generation."""

import logging
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import Response

from core.tts import get_tts_service, NarratorType
from ai.edge_tts_service import NARRATOR_SPEED
from schema.story import (
    TTSRequest, 
    VoiceGender,
    NarratorPersona,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tts", tags=["text-to-speech"])

# Get the TTS service instance
tts_service = get_tts_service()


@router.get(
    "/languages",
    summary="Get supported languages",
)
async def get_languages() -> dict:
    """
    Get all supported languages for Edge TTS.
    
    Edge TTS supports multiple languages including English and Urdu.
    """
    languages = tts_service.list_supported_languages()
    return {
        "languages": languages,
        "default": "english",
        "note": "Edge TTS provides male and female voices per language",
    }


@router.get(
    "/narrator-speeds",
    summary="Get speed settings for each narrator persona",
)
async def get_narrator_speeds() -> dict:
    """
    Get the speech speed multipliers for each narrator persona.
    """
    
    return {
        "speeds": {
            narrator: {
                "speed": speed,
                "description": _get_narrator_description(narrator),
            }
            for narrator, speed in NARRATOR_SPEED.items()
        },
        "note": "Speed multipliers: <1.0 = slower, >1.0 = faster",
    }


def _get_narrator_description(narrator: str) -> str:
    """Get description for narrator persona."""
    descriptions = {
        "mysterious": "Slow, deliberate pacing with an air of mystery",
        "epic": "Energetic, grand narration for legendary tales",
        "horror": "Very slow, building tension and suspense",
        "comedic": "Upbeat, lively delivery with energy",
        "romantic": "Gentle, slower pacing for emotional moments",
    }
    return descriptions.get(narrator, "Standard narration")


@router.post(
    "/synthesize",
    response_class=Response,
    summary="Convert text to speech",
    responses={
        200: {
            "content": {"audio/wav": {}},
            "description": "WAV audio file",
        }
    },
)
async def synthesize_speech(
    request: TTSRequest,
) -> Response:
    """
    Convert text to speech audio using MMS-TTS.
    
    Returns a WAV audio file that can be played directly in a browser.
    
    Features:
    - Local model (no API limits or costs)
    - 1,100+ languages supported
    - Narrator persona affects speech speed
    - High-quality neural speech synthesis
    
    Supported languages include:
    - English, Urdu, Hindi, Arabic
    - Spanish, French, German, Italian
    - And many more...
    """
    narrator_str = request.narrator.value.lower() if request.narrator else None
    language_str = request.language.value.lower() if request.language else "english"
    
    logger.info(f"TTS request: language={language_str}, narrator={narrator_str}, {len(request.text)} chars")
    
    try:
        audio_data, content_type = await tts_service.synthesize(
            text=request.text,
            language=language_str,
            narrator=narrator_str,
        )
        
        return Response(
            content=audio_data,
            media_type=content_type,
            headers={
                "Content-Disposition": "inline; filename=story_audio.wav",
                "Cache-Control": "max-age=3600",  # Cache for 1 hour
            },
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        logger.error(f"TTS synthesis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate audio. Please try again.",
        )


@router.post(
    "/synthesize/node/{node_id}",
    response_class=Response,
    summary="Convert story node to speech",
    responses={
        200: {
            "content": {"audio/wav": {}},
            "description": "WAV audio file",
        }
    },
)
async def synthesize_node(
    node_id: int,
) -> Response:
    """
    Generate speech for a specific story node.
    
    Fetches the node content and converts it to speech.
    Automatically uses the story's narrator persona for voice matching.
    """
    from db.database import get_db
    from models.story import StoryNode
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    # Get database session
    db = next(get_db())
    
    try:
        # Fetch the node with its story to get narrator persona
        result = db.execute(
            select(StoryNode)
            .options(selectinload(StoryNode.story))
            .where(StoryNode.id == node_id)
        )
        node = result.scalar_one_or_none()
        
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Story node {node_id} not found",
            )
        
        # Get narrator persona and language from the story
        narrator = getattr(node.story, 'narrator_persona', None) if node.story else None
        language = getattr(node.story, 'language', 'english') if node.story else 'english'
        
        audio_data, content_type = await tts_service.synthesize(
            text=node.content,
            narrator=narrator,
            language=language,
        )
        
        return Response(
            content=audio_data,
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename=node_{node_id}_audio.wav",
                "Cache-Control": "max-age=3600",
            },
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        logger.error(f"TTS synthesis for node {node_id} failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate audio. Please try again.",
        )
    finally:
        db.close()


@router.delete(
    "/cache",
    summary="Clear TTS cache",
)
async def clear_cache() -> dict:
    """Clear the TTS audio cache."""
    tts_service.clear_cache()
    return {"message": "TTS cache cleared successfully"}


@router.post(
    "/unload",
    summary="Unload TTS models",
)
async def unload_models() -> dict:
    """
    Unload all TTS models from memory.
    
    Useful for freeing GPU/CPU memory when TTS is not needed.
    Models will be automatically reloaded on next use.
    """
    tts_service.unload_models()
    return {"message": "TTS models unloaded successfully"}
