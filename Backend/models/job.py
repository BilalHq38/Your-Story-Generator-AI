"""Job model for tracking async story generation tasks."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.database import Base

if TYPE_CHECKING:
    from models.story import Story


class JobStatus(str, Enum):
    """Possible states for a generation job."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    """Types of generation jobs."""
    
    STORY_START = "story_start"
    STORY_CONTINUE = "story_continue"
    STORY_BRANCH = "story_branch"
    GENERATE_OPENING = "generate_opening"
    GENERATE_CONTINUATION = "generate_continuation"
    GENERATE_ENDING = "generate_ending"


class Job(Base):
    """Tracks async story generation tasks."""
    
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    story_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=True
    )
    node_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("story_nodes.id", ondelete="SET NULL"), nullable=True
    )
    
    job_type: Mapped[str] = mapped_column(
        String(50), default=JobType.GENERATE_OPENING.value
    )
    status: Mapped[str] = mapped_column(
        String(20), default=JobStatus.PENDING.value, index=True
    )
    
    # Input/Output
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    story: Mapped[Optional["Story"]] = relationship("Story", back_populates="jobs")

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, job_id='{self.job_id}', status='{self.status}')>"

    @property
    def is_complete(self) -> bool:
        return self.status in (JobStatus.COMPLETED.value, JobStatus.FAILED.value)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate job duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
