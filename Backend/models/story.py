"""
Story and StoryNode database models.
Production-safe for FastAPI + Neon + Vercel.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional, List, Dict

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.database import Base

if TYPE_CHECKING:
    from models.job import Job


# -------------------------
# Enums
# -------------------------
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


# -------------------------
# Story
# -------------------------
class Story(Base):
    """Represents a choose-your-own-adventure story."""

    __tablename__ = "stories"
    __table_args__ = (
        Index("ix_stories_session_id", "session_id"),
        Index("ix_stories_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    session_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    genre: Mapped[Optional[str]] = mapped_column(String(50))

    narrator_persona: Mapped[NarratorPersona] = mapped_column(
        String(50),
        nullable=False,
        default=NarratorPersona.MYSTERIOUS,
    )

    atmosphere: Mapped[StoryAtmosphere] = mapped_column(
        String(50),
        nullable=False,
        default=StoryAtmosphere.MAGICAL,
    )

    language: Mapped[StoryLanguage] = mapped_column(
        String(20),
        nullable=False,
        default=StoryLanguage.ENGLISH,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    root_node_id: Mapped[Optional[int]] = mapped_column(Integer)
    current_node_id: Mapped[Optional[int]] = mapped_column(Integer)

    complete_story_text: Mapped[Optional[str]] = mapped_column(Text)

    story_branches: Mapped[Optional[List[Dict]]] = mapped_column(
        JSONB, nullable=True
    )

    story_context: Mapped[Optional[Dict]] = mapped_column(
        JSONB, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    nodes: Mapped[List["StoryNode"]] = relationship(
        "StoryNode",
        back_populates="story",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    jobs: Mapped[List["Job"]] = relationship(
        "Job",
        back_populates="story",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Story id={self.id} title='{self.title}'>"


# -------------------------
# StoryNode
# -------------------------
class StoryNode(Base):
    """Represents a node/chapter in a story tree."""

    __tablename__ = "story_nodes"
    __table_args__ = (
        Index("ix_story_nodes_story_id", "story_id"),
        Index("ix_story_nodes_parent_id", "parent_id"),
        Index("ix_story_nodes_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    story_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("stories.id", ondelete="CASCADE"),
        nullable=False,
    )

    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("story_nodes.id", ondelete="SET NULL"),
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)

    choice_text: Mapped[Optional[str]] = mapped_column(String(255))

    choices: Mapped[Optional[List[Dict]]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
    )

    node_metadata: Mapped[Optional[Dict]] = mapped_column(
        JSONB, nullable=True
    )

    is_root: Mapped[bool] = mapped_column(Boolean, default=False)
    is_ending: Mapped[bool] = mapped_column(Boolean, default=False)

    depth: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    story: Mapped["Story"] = relationship(
        "Story",
        back_populates="nodes",
    )

    parent: Mapped[Optional["StoryNode"]] = relationship(
        "StoryNode",
        remote_side=[id],
        back_populates="children",
    )

    children: Mapped[List["StoryNode"]] = relationship(
        "StoryNode",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<StoryNode id={self.id} "
            f"story_id={self.story_id} "
            f"depth={self.depth} "
            f"is_root={self.is_root}>"
        )
