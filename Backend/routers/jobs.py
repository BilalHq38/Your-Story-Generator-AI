"""Jobs router - Endpoints for tracking async story generation tasks."""

import logging
from math import ceil
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from db.database import DbSession
from models.job import Job, JobStatus
from schema.job import JobListResponse, JobResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get(
    "/",
    response_model=JobListResponse,
    summary="List all jobs",
)
async def list_jobs(
    db: DbSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    story_id: Optional[int] = None,
) -> JobListResponse:
    """Get a paginated list of jobs with optional filtering."""
    query = select(Job)
    
    if status_filter:
        query = query.where(Job.status == status_filter)
    if story_id:
        query = query.where(Job.story_id == story_id)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0
    
    # Paginate
    offset = (page - 1) * size
    query = query.order_by(Job.created_at.desc()).offset(offset).limit(size)
    
    jobs = db.execute(query).scalars().all()
    
    return JobListResponse(
        items=list(jobs),
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if total > 0 else 1,
    )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get job details",
)
async def get_job(job_id: int, db: DbSession) -> Job:
    """Get detailed information about a specific job by its ID."""
    job = db.get(Job, job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )
    
    return job


@router.post(
    "/{job_id}/cancel",
    response_model=JobResponse,
    summary="Cancel a pending job",
)
async def cancel_job(job_id: int, db: DbSession) -> Job:
    """Cancel a job if it hasn't started processing yet."""
    job = db.get(Job, job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found",
        )
    
    if job.status != JobStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status '{job.status}'",
        )
    
    job.status = JobStatus.CANCELLED.value
    db.commit()
    db.refresh(job)
    
    logger.info(f"Cancelled job {job_id}")
    return job

