"""Pydantic schemas for Job API requests and responses."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from models.job import JobStatus, JobType


# ============ Response Schemas ============

class JobResponse(BaseModel):
    """Schema for job in API responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    story_id: Optional[int]
    node_id: Optional[int]
    job_type: str
    status: str
    result: Optional[dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class JobListResponse(BaseModel):
    """Paginated list of jobs."""
    
    items: list[JobResponse]
    total: int
    page: int = 1
    size: int = 20
    pages: int = 1
