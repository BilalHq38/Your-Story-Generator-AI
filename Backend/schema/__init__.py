"""Schema package - export all Pydantic schemas."""

from schema.job import (
    JobListResponse,
    JobResponse,
)
from schema.story import (
    ContinueStoryRequest,
    JobStartResponse,
    NarratorPersona,
    PaginatedResponse,
    StoryAtmosphere,
    StoryChoice,
    StoryCreate,
    StoryDetail,
    StoryListResponse,
    StoryNodeCreate,
    StoryNodeResponse,
    StoryNodeUpdate,
    StoryNodeWithChildren,
    StoryResponse,
    StoryUpdate,
    StoryWithNodes,
    # TTS schemas
    VoiceGender,
    VoiceInfo,
    TTSRequest,
    TTSVoicesResponse,
)

__all__ = [
    # Enums
    "NarratorPersona",
    "StoryAtmosphere",
    "VoiceGender",
    # Story schemas
    "StoryCreate",
    "StoryUpdate",
    "StoryResponse",
    "StoryWithNodes",
    "StoryDetail",
    "StoryListResponse",
    "StoryNodeCreate",
    "StoryNodeUpdate",
    "StoryNodeResponse",
    "StoryNodeWithChildren",
    "StoryChoice",
    "ContinueStoryRequest",
    "PaginatedResponse",
    "JobStartResponse",
    # TTS schemas
    "VoiceInfo",
    "TTSRequest",
    "TTSVoicesResponse",
    # Job schemas
    "JobResponse",
    "JobListResponse",
]
