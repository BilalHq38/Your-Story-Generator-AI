"""
Job model for tracking async story generation tasks.
Production-safe for FastAPI + Neon + Vercel.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
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
    from models.story import Story


# -------------------------
# Enums
# -------------------------
class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    STORY_START = "story_start"
    STORY_CONTINUE = "story_continue"
    STORY_BRANCH = "story_branch"
    GENERATE_OPENING = "generate_opening"
    GENERATE_CONTINUATION = "generate_continuation"
    GENERATE_ENDING = "generate_ending"


# -------------------------
# Model
# -------------------------
class Job(Base):
    """Tracks async story generation tasks."""

    __tablename__ = "jobs"
    __table_args__ = (
        Index("ix_jobs_story_id", "story_id"),
        Index("ix_jobs_status", "status"),
        Index("ix_jobs_created_at", "created_at"),
    )

    # Primary key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Relations
    story_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("stories.id", ondelete="CASCADE"),
        nullable=True,
    )

    node_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("story_nodes.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Job metadata
    job_type: Mapped[JobType] = mapped_column(
        String(50),
        nullable=False,
        default=JobType.GENERATE_OPENING,
    )

    status: Mapped[JobStatus] = mapped_column(
        String(20),
        nullable=False,
        default=JobStatus.PENDING,
    )

    # Input / Output
    result: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    story: Mapped[Optional["Story"]] = relationship(
        "Story",
        back_populates="jobs",
        lazy="joined",
    )

    # -------------------------
    # Helpers
    # -------------------------
    def __repr__(self) -> str:
        return (
            f"<Job id={self.id} "
            f"type={self.job_type} "
            f"status={self.status}>"
        )

    @property
    def is_complete(self) -> bool:
        return self.status in {
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
        }

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
