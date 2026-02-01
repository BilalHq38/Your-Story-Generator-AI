"""Pydantic schemas for Story API requests and responses."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


# ============ Enums ============

class NarratorPersona(str, Enum):
    """Available narrator personas for storytelling."""
    MYSTERIOUS = "mysterious"
    EPIC = "epic"
    HORROR = "horror"
    COMEDIC = "comedic"
    ROMANTIC = "romantic"


class StoryAtmosphere(str, Enum):
    """Story atmosphere/mood settings."""
    DARK = "dark"
    MAGICAL = "magical"
    PEACEFUL = "peaceful"
    TENSE = "tense"
    WHIMSICAL = "whimsical"


class StoryLanguage(str, Enum):
    """Supported story languages."""
    ENGLISH = "english"
    URDU = "urdu"


# ============ Choice Schema ============

class StoryChoice(BaseModel):
    """A choice available to the reader."""
    id: str = Field(default_factory=lambda: str(uuid4())[:8])
    text: str = Field(..., min_length=1, max_length=300)
    consequence_hint: Optional[str] = Field(None, max_length=200)


# ============ Base Schemas ============

class StoryNodeBase(BaseModel):
    """Base schema for story node data."""
    
    content: str = Field(..., min_length=1, max_length=15000)
    choice_text: Optional[str] = Field(None, max_length=300)
    choices: Optional[list[StoryChoice]] = Field(default_factory=list)
    node_metadata: Optional[dict] = None


class StoryBase(BaseModel):
    """Base schema for story data."""
    
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    genre: str = Field(default="Fantasy", max_length=50)
    narrator_persona: NarratorPersona = Field(default=NarratorPersona.MYSTERIOUS)
    atmosphere: StoryAtmosphere = Field(default=StoryAtmosphere.MAGICAL)
    language: StoryLanguage = Field(default=StoryLanguage.ENGLISH)


# ============ Create Schemas ============

class StoryCreate(StoryBase):
    """Schema for creating a new story."""
    
    initial_prompt: Optional[str] = Field(
        None,
        max_length=2000,
        description="Optional prompt to generate the story's first node"
    )


class StoryNodeCreate(StoryNodeBase):
    """Schema for creating a new story node."""
    
    parent_id: Optional[int] = Field(None, ge=1)
    is_ending: bool = False


class ContinueStoryRequest(BaseModel):
    """Schema for continuing the story with a choice."""
    
    choice_id: str = Field(..., description="ID of the selected choice")
    choice_text: str = Field(..., min_length=1, max_length=300)


# ============ Update Schemas ============

class StoryUpdate(BaseModel):
    """Schema for updating a story."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    genre: Optional[str] = Field(None, max_length=50)
    narrator_persona: Optional[NarratorPersona] = None
    atmosphere: Optional[StoryAtmosphere] = None
    language: Optional[StoryLanguage] = None
    is_active: Optional[bool] = None
    is_completed: Optional[bool] = None


class StoryNodeUpdate(BaseModel):
    """Schema for updating a story node."""
    
    content: Optional[str] = Field(None, min_length=1, max_length=15000)
    choices: Optional[list[StoryChoice]] = None
    node_metadata: Optional[dict] = None
    is_ending: Optional[bool] = None


# ============ Response Schemas ============

class StoryNodeResponse(BaseModel):
    """Schema for story node in API responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    story_id: int
    parent_id: Optional[int]
    content: str
    choice_text: Optional[str]
    choices: list[StoryChoice] = []
    node_metadata: Optional[dict] = None
    is_root: bool
    is_ending: bool
    depth: int
    created_at: datetime


class StoryNodeWithChildren(StoryNodeResponse):
    """Story node with its child nodes."""
    
    children: list["StoryNodeWithChildren"] = []


class StoryResponse(BaseModel):
    """Schema for story in API responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: Optional[str]
    genre: Optional[str]
    narrator_persona: str
    atmosphere: str
    language: str = "english"
    session_id: str
    is_active: bool
    is_completed: bool
    root_node_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class StoryWithNodes(StoryResponse):
    """Story with all its nodes."""
    
    nodes: list[StoryNodeResponse] = []


class StoryDetail(StoryResponse):
    """Story with root node and tree structure."""
    
    root_node: Optional[StoryNodeWithChildren] = None
    node_count: int = 0


# ============ List/Pagination Schemas ============

class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    
    items: list
    total: int
    page: int
    size: int
    pages: int
    total_pages: int


class StoryListResponse(BaseModel):
    """Paginated list of stories."""
    
    items: list[StoryResponse]
    total: int
    page: int = 1
    size: int = 20
    pages: int = 1
    total_pages: int = 1


# ============ Job Response Schemas ============

class JobStartResponse(BaseModel):
    """Response when starting an async job."""
    job_id: int


# ============ TTS (Text-to-Speech) Schemas ============

class VoiceGender(str, Enum):
    """Voice gender options."""
    MALE = "male"
    FEMALE = "female"


class VoiceInfo(BaseModel):
    """Information about an available voice."""
    id: str
    name: str
    locale: str
    style: str
    gender: VoiceGender


class NarratorVoiceProfile(BaseModel):
    """Voice profile settings for a narrator persona."""
    narrator: NarratorPersona
    voice: str
    rate: str
    pitch: str
    description: str


class TTSRequest(BaseModel):
    """Request to generate speech from text."""
    text: str = Field(..., min_length=1, max_length=20000, description="Text to convert to speech")
    voice: Optional[str] = Field(None, description="Specific voice ID (overrides narrator default)")
    gender: VoiceGender = Field(default=VoiceGender.FEMALE, description="Voice gender preference")
    narrator: Optional[NarratorPersona] = Field(None, description="Narrator persona to match voice style")
    rate: Optional[str] = Field(None, description="Speech rate adjustment (-50% to +100%), uses narrator default if not set")
    pitch: Optional[str] = Field(None, description="Pitch adjustment (-50Hz to +50Hz), uses narrator default if not set")
    language: StoryLanguage = Field(default=StoryLanguage.ENGLISH, description="Language for voice selection")


class TTSVoicesResponse(BaseModel):
    """Response containing available voices."""
    male_voices: list[VoiceInfo]
    female_voices: list[VoiceInfo]
    default_male: str
    default_female: str


class NarratorVoiceProfilesResponse(BaseModel):
    """Response containing voice profiles for all narrators."""
    profiles: dict[str, NarratorVoiceProfile]
