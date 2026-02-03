"""
Pydantic schemas for Story API requests and responses.
Production-safe for FastAPI + Pydantic v2.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Generic, TypeVar, List, Dict
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# Enums (must mirror DB enums)
# =====================================================

class NarratorPersona(str, Enum):
    MYSTERIOUS = "mysterious"
    EPIC = "epic"
    HORROR = "horror"
    COMEDIC = "comedic"
    ROMANTIC = "romantic"


class StoryAtmosphere(str, Enum):
    DARK = "dark"
    MAGICAL = "magical"
    PEACEFUL = "peaceful"
    TENSE = "tense"
    WHIMSICAL = "whimsical"


class StoryLanguage(str, Enum):
    ENGLISH = "english"
    URDU = "urdu"


# =====================================================
# Story Memory Schema
# =====================================================

class StoryMemory(BaseModel):
    """Schema for story memory/context to maintain continuity."""
    characters: List[str] = Field(default_factory=list, description="Main character names")
    key_events: List[str] = Field(default_factory=list, description="Important story events")
    current_situation: str = Field(default="", description="Current scene/situation")
    story_summary: str = Field(default="", description="Progressive story summary")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "characters": ["Alice", "Bob"],
                "key_events": ["Found the ancient key", "Entered the dark forest"],
                "current_situation": "They stand before the locked door",
                "story_summary": "Two adventurers discovered a mysterious key and journeyed through a dark forest."
            }
        }
    )


# =====================================================
# Choice
# =====================================================

class StoryChoice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    text: str = Field(..., min_length=1, max_length=300)
    consequence_hint: Optional[str] = Field(None, max_length=200)


# =====================================================
# Base schemas
# =====================================================

class StoryNodeBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=15000)
    choice_text: Optional[str] = Field(None, max_length=300)
    choices: Optional[List[StoryChoice]] = None
    node_metadata: Optional[Dict] = None


class StoryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    genre: str = Field(default="Fantasy", max_length=50)
    narrator_persona: NarratorPersona = NarratorPersona.MYSTERIOUS
    atmosphere: StoryAtmosphere = StoryAtmosphere.MAGICAL
    language: StoryLanguage = StoryLanguage.ENGLISH


# =====================================================
# Create / Update
# =====================================================

class StoryCreate(StoryBase):
    initial_prompt: Optional[str] = Field(None, max_length=2000)


class StoryNodeCreate(StoryNodeBase):
    parent_id: Optional[int] = Field(None, ge=1)
    is_ending: bool = False


class ContinueStoryRequest(BaseModel):
    choice_id: str
    choice_text: str = Field(..., min_length=1, max_length=300)


class StoryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    genre: Optional[str] = Field(None, max_length=50)
    narrator_persona: Optional[NarratorPersona] = None
    atmosphere: Optional[StoryAtmosphere] = None
    language: Optional[StoryLanguage] = None
    is_active: Optional[bool] = None
    is_completed: Optional[bool] = None


class StoryNodeUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=15000)
    choices: Optional[List[StoryChoice]] = None
    node_metadata: Optional[Dict] = None
    is_ending: Optional[bool] = None


# =====================================================
# Responses
# =====================================================

class StoryNodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    story_id: int
    parent_id: Optional[int]
    content: str
    choice_text: Optional[str]
    choices: Optional[List[StoryChoice]]
    node_metadata: Optional[Dict]
    is_root: bool
    is_ending: bool
    depth: int
    created_at: datetime


class StoryNodeWithChildren(StoryNodeResponse):
    children: List["StoryNodeWithChildren"] = Field(default_factory=list)


class StoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    genre: Optional[str]
    narrator_persona: NarratorPersona
    atmosphere: StoryAtmosphere
    language: StoryLanguage
    session_id: str
    is_active: bool
    is_completed: bool
    root_node_id: Optional[int]
    current_node_id: Optional[int]
    complete_story_text: Optional[str]
    story_branches: Optional[List]
    created_at: datetime
    updated_at: datetime


class StoryWithNodes(StoryResponse):
    nodes: List[StoryNodeResponse] = Field(default_factory=list)


class StoryDetail(StoryResponse):
    root_node: Optional[StoryNodeWithChildren] = None
    node_count: int = 0


# =====================================================
# Branches
# =====================================================

class StoryBranchNode(BaseModel):
    id: int
    content: str
    choice_text: Optional[str]
    is_ending: bool = False


class StoryBranch(BaseModel):
    id: str
    nodes: List[StoryBranchNode]
    is_complete: bool = False


class SaveBranchesRequest(BaseModel):
    complete_story_text: Optional[str]
    branches: List[StoryBranch] = Field(default_factory=list)


class StoryBranchesResponse(BaseModel):
    story_id: int
    title: str
    complete_story_text: Optional[str]
    branches: List[StoryBranch] = Field(default_factory=list)
    total_branches: int = 0
    has_complete_ending: bool = False


# =====================================================
# Pagination (generic)
# =====================================================

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    total_pages: int


class StoryListResponse(PaginatedResponse[StoryResponse]):
    pass


# =====================================================
# Jobs
# =====================================================

class JobStartResponse(BaseModel):
    job_id: int


# =====================================================
# TTS
# =====================================================

class VoiceGender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class VoiceInfo(BaseModel):
    id: str
    name: str
    locale: str
    style: str
    gender: VoiceGender


class NarratorVoiceProfile(BaseModel):
    narrator: NarratorPersona
    voice: str
    rate: str
    pitch: str
    description: str


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)
    voice: Optional[str] = None
    gender: VoiceGender = VoiceGender.FEMALE
    narrator: Optional[NarratorPersona] = None
    rate: Optional[str] = None
    pitch: Optional[str] = None
    language: StoryLanguage = StoryLanguage.ENGLISH


class TTSVoicesResponse(BaseModel):
    male_voices: List[VoiceInfo]
    female_voices: List[VoiceInfo]
    default_male: str
    default_female: str


class NarratorVoiceProfilesResponse(BaseModel):
    profiles: Dict[str, NarratorVoiceProfile]


# Required for recursive models (Pydantic v2)
StoryNodeWithChildren.model_rebuild()
