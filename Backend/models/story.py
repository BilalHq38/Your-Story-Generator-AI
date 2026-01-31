"""Story and StoryNode database models."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.database import Base

if TYPE_CHECKING:
    from models.job import Job


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


class Story(Base):
    """Represents a choose-your-own-adventure story."""
    
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    genre: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    narrator_persona: Mapped[str] = mapped_column(
        String(50), default=NarratorPersona.MYSTERIOUS.value
    )
    atmosphere: Mapped[str] = mapped_column(
        String(50), default=StoryAtmosphere.MAGICAL.value
    )
    language: Mapped[str] = mapped_column(
        String(20), default=StoryLanguage.ENGLISH.value
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    root_node_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    nodes: Mapped[list["StoryNode"]] = relationship(
        "StoryNode", back_populates="story", cascade="all, delete-orphan"
    )
    jobs: Mapped[list["Job"]] = relationship(
        "Job", back_populates="story", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Story(id={self.id}, title='{self.title}')>"


class StoryNode(Base):
    """Represents a node/chapter in a story with choices leading to other nodes."""
    
    __tablename__ = "story_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    story_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("stories.id", ondelete="CASCADE"), index=True
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("story_nodes.id", ondelete="SET NULL"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text)
    choice_text: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )  # The choice that led to this node
    choices: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, default=list
    )  # Available choices for the reader [{"id": "...", "text": "...", "consequence_hint": "..."}]
    node_metadata: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True
    )  # Extra metadata like mood, tension_level, etc.
    is_root: Mapped[bool] = mapped_column(Boolean, default=False)
    is_ending: Mapped[bool] = mapped_column(Boolean, default=False)
    depth: Mapped[int] = mapped_column(Integer, default=0)  # Track tree depth
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    story: Mapped["Story"] = relationship("Story", back_populates="nodes")
    parent: Mapped[Optional["StoryNode"]] = relationship(
        "StoryNode", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["StoryNode"]] = relationship(
        "StoryNode", back_populates="parent", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<StoryNode(id={self.id}, story_id={self.story_id}, is_root={self.is_root})>"

