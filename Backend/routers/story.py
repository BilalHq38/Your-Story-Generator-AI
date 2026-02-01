"""Story router - CRUD endpoints for stories and story nodes."""

import asyncio
import base64
import logging
import secrets
from math import ceil
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from core.config import settings
from core.tts import get_tts_service
from db.database import DbSession
from models.story import Story, StoryNode
from schema.story import (
    ContinueStoryRequest,
    JobStartResponse,
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
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stories", tags=["stories"])


def generate_session_id() -> str:
    """Generate a unique session ID for a story."""
    return secrets.token_urlsafe(32)


# Get the TTS service singleton
tts_service = get_tts_service()


async def generate_audio_for_node(
    content: str,
    narrator: Optional[str] = None,
    language: str = "english",
) -> Optional[str]:
    """
    Generate audio for story content and return as base64 data URL.
    Returns None if audio generation fails.
    """
    try:
        audio_data, content_type = await tts_service.synthesize(
            text=content,
            narrator=narrator,
            language=language,
        )
        # Convert to base64 data URL for instant playback
        b64_audio = base64.b64encode(audio_data).decode('utf-8')
        return f"data:{content_type};base64,{b64_audio}"
    except Exception as e:
        logger.warning(f"Failed to generate audio for node: {e}")
        return None


def build_node_tree(node: StoryNode) -> StoryNodeWithChildren:
    """Recursively build a tree structure from a node."""
    # Convert choices from dict list to StoryChoice objects
    choices = []
    if node.choices:
        for c in node.choices:
            if isinstance(c, dict):
                choices.append(StoryChoice(**c))
            else:
                choices.append(c)
    
    return StoryNodeWithChildren(
        id=node.id,
        story_id=node.story_id,
        parent_id=node.parent_id,
        content=node.content,
        choice_text=node.choice_text,
        choices=choices,
        node_metadata=node.node_metadata,
        is_root=node.is_root,
        is_ending=node.is_ending,
        depth=node.depth,
        created_at=node.created_at,
        children=[build_node_tree(child) for child in node.children],
    )


# ============ Story CRUD ============


@router.post(
    "/",
    response_model=StoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new story",
)
async def create_story(story_data: StoryCreate, db: DbSession) -> Story:
    """
    Create a new choose-your-own-adventure story.
    
    Optionally provide an initial_prompt to generate the first node.
    """
    logger.info(f"Creating new story: {story_data.title}")
    
    story = Story(
        title=story_data.title,
        description=story_data.description,
        genre=story_data.genre,
        narrator_persona=story_data.narrator_persona.value,
        atmosphere=story_data.atmosphere.value,
        language=story_data.language.value,
        session_id=generate_session_id(),
    )
    
    db.add(story)
    db.commit()
    db.refresh(story)
    
    logger.info(f"Created story with ID: {story.id}, language: {story.language}")
    return story


@router.get(
    "/",
    response_model=StoryListResponse,
    summary="List all stories",
)
async def list_stories(
    db: DbSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100, alias="page_size"),
    genre: Optional[str] = None,
    active_only: bool = True,
) -> StoryListResponse:
    """Get a paginated list of stories with optional filtering."""
    query = select(Story)
    
    if active_only:
        query = query.where(Story.is_active == True)
    if genre:
        query = query.where(Story.genre == genre)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0
    
    # Paginate
    offset = (page - 1) * size
    query = query.order_by(Story.created_at.desc()).offset(offset).limit(size)
    
    stories = db.execute(query).scalars().all()

    total_pages = ceil(total / size) if total > 0 else 1
    
    return StoryListResponse(
        items=list(stories),
        total=total,
        page=page,
        size=size,
        pages=total_pages,
        total_pages=total_pages,
    )


@router.get(
    "/{story_id}",
    response_model=StoryDetail,
    summary="Get story details",
)
async def get_story(story_id: int, db: DbSession) -> StoryDetail:
    """Get a story with its root node and full tree structure."""
    story = db.execute(
        select(Story)
        .options(selectinload(Story.nodes).selectinload(StoryNode.children))
        .where(Story.id == story_id)
    ).scalar_one_or_none()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )
    
    # Find root node and build tree
    root_node = None
    for node in story.nodes:
        if node.is_root:
            root_node = build_node_tree(node)
            break
    
    return StoryDetail(
        id=story.id,
        title=story.title,
        description=story.description,
        genre=story.genre,
        narrator_persona=story.narrator_persona,
        atmosphere=story.atmosphere,
        language=story.language,
        session_id=story.session_id,
        is_active=story.is_active,
        is_completed=story.is_completed,
        root_node_id=story.root_node_id,
        created_at=story.created_at,
        updated_at=story.updated_at,
        root_node=root_node,
        node_count=len(story.nodes),
    )


@router.get(
    "/session/{session_id}",
    response_model=StoryResponse,
    summary="Get story by session ID",
)
async def get_story_by_session(session_id: str, db: DbSession) -> Story:
    """Get a story by its unique session ID."""
    story = db.execute(
        select(Story).where(Story.session_id == session_id)
    ).scalar_one_or_none()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with session ID '{session_id}' not found",
        )
    
    return story


@router.patch(
    "/{story_id}",
    response_model=StoryResponse,
    summary="Update a story",
)
async def update_story(
    story_id: int,
    story_data: StoryUpdate,
    db: DbSession,
) -> Story:
    """Update story metadata."""
    story = db.get(Story, story_id)
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )
    
    update_data = story_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(story, field, value)
    
    db.commit()
    db.refresh(story)
    
    logger.info(f"Updated story {story_id}: {update_data}")
    return story


@router.delete(
    "/{story_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a story",
)
async def delete_story(story_id: int, db: DbSession) -> None:
    """Delete a story and all its nodes."""
    story = db.get(Story, story_id)
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )
    
    db.delete(story)
    db.commit()
    
    logger.info(f"Deleted story {story_id}")


# ============ Story Node CRUD ============


@router.post(
    "/{story_id}/nodes",
    response_model=StoryNodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a node to a story",
)
async def create_story_node(
    story_id: int,
    node_data: StoryNodeCreate,
    db: DbSession,
) -> StoryNode:
    """Create a new node in a story."""
    story = db.get(Story, story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )
    
    # Check if root node exists
    existing_root = db.execute(
        select(StoryNode).where(
            StoryNode.story_id == story_id,
            StoryNode.is_root == True,
        )
    ).scalar_one_or_none()
    
    is_root = existing_root is None and node_data.parent_id is None
    
    # Calculate depth
    depth = 0
    if node_data.parent_id:
        parent = db.get(StoryNode, node_data.parent_id)
        if not parent or parent.story_id != story_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid parent node",
            )
        depth = parent.depth + 1
    
    node = StoryNode(
        story_id=story_id,
        parent_id=node_data.parent_id,
        content=node_data.content,
        choice_text=node_data.choice_text,
        node_metadata=node_data.node_metadata,
        is_root=is_root,
        is_ending=node_data.is_ending,
        depth=depth,
    )
    
    db.add(node)
    db.commit()
    db.refresh(node)
    
    logger.info(f"Created node {node.id} for story {story_id}")
    return node


@router.get(
    "/{story_id}/nodes",
    response_model=list[StoryNodeResponse],
    summary="Get all nodes for a story",
)
async def list_story_nodes(story_id: int, db: DbSession) -> list[StoryNode]:
    """Get all nodes for a story in flat list format."""
    story = db.get(Story, story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )
    
    nodes = db.execute(
        select(StoryNode)
        .where(StoryNode.story_id == story_id)
        .order_by(StoryNode.depth, StoryNode.created_at)
    ).scalars().all()
    
    return list(nodes)


@router.get(
    "/{story_id}/nodes/{node_id}",
    response_model=StoryNodeWithChildren,
    summary="Get a specific node with children",
)
async def get_story_node(
    story_id: int,
    node_id: int,
    db: DbSession,
) -> StoryNodeWithChildren:
    """Get a node with its immediate children."""
    node = db.execute(
        select(StoryNode)
        .options(selectinload(StoryNode.children))
        .where(StoryNode.id == node_id, StoryNode.story_id == story_id)
    ).scalar_one_or_none()
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found in story {story_id}",
        )
    
    return build_node_tree(node)


@router.patch(
    "/{story_id}/nodes/{node_id}",
    response_model=StoryNodeResponse,
    summary="Update a story node",
)
async def update_story_node(
    story_id: int,
    node_id: int,
    node_data: StoryNodeUpdate,
    db: DbSession,
) -> StoryNode:
    """Update node content or metadata."""
    node = db.execute(
        select(StoryNode).where(
            StoryNode.id == node_id,
            StoryNode.story_id == story_id,
        )
    ).scalar_one_or_none()
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found in story {story_id}",
        )
    
    update_data = node_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(node, field, value)
    
    db.commit()
    db.refresh(node)
    
    return node


@router.delete(
    "/{story_id}/nodes/{node_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a story node",
)
async def delete_story_node(
    story_id: int,
    node_id: int,
    db: DbSession,
) -> None:
    """Delete a node and all its children (cascade)."""
    node = db.execute(
        select(StoryNode).where(
            StoryNode.id == node_id,
            StoryNode.story_id == story_id,
        )
    ).scalar_one_or_none()
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found in story {story_id}",
        )
    
    if node.is_root:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete root node. Delete the story instead.",
        )
    
    db.delete(node)
    db.commit()
    
    logger.info(f"Deleted node {node_id} from story {story_id}")


# ============ Story Generation Endpoints ============

from models.job import Job, JobStatus, JobType


@router.post(
    "/{story_id}/generate/opening",
    response_model=JobStartResponse,
    summary="Generate story opening",
)
async def generate_story_opening(story_id: int, db: DbSession) -> JobStartResponse:
    """Start generating the opening of the story using AI."""
    story = db.get(Story, story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )
    
    # Check if story already has a root node
    existing_root = db.execute(
        select(StoryNode).where(
            StoryNode.story_id == story_id,
            StoryNode.is_root == True,
        )
    ).scalar_one_or_none()
    
    if existing_root:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Story already has an opening. Use continue endpoint.",
        )
    
    # Create a job for the generation
    job = Job(
        story_id=story_id,
        job_type=JobType.GENERATE_OPENING,
        status=JobStatus.PENDING,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # TODO: Trigger async generation task
    # For now, we'll process synchronously for simplicity
    from core.story_generator import StoryGenerator
    
    try:
        job.status = JobStatus.PROCESSING
        db.commit()
        
        generator = StoryGenerator()
        result = generator.generate(
            job_type="generate_opening",
            story=story,
            parent_node=None,
            choice_text=None,
        )
        
        # Generate audio for the content immediately
        audio_url = await generate_audio_for_node(
            content=result["content"],
            narrator=story.narrator_persona,
            language=story.language or "english",
        )
        
        # Create the root node with audio URL
        node = StoryNode(
            story_id=story_id,
            content=result["content"],
            choices=result.get("choices", []),
            is_root=True,
            is_ending=result.get("is_ending", False),
            depth=0,
            node_metadata={"audio_url": audio_url} if audio_url else None,
        )
        db.add(node)
        db.commit()
        db.refresh(node)
        
        # Update story with root node reference
        story.root_node_id = node.id
        db.commit()
        
        # Include audio in result
        result["audio_url"] = audio_url
        
        job.status = JobStatus.COMPLETED
        job.node_id = node.id
        job.result = result
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to generate opening: {e}")
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate story opening: {str(e)}",
        )
    
    return JobStartResponse(job_id=job.id)


@router.post(
    "/{story_id}/nodes/{node_id}/continue",
    response_model=JobStartResponse,
    summary="Continue story from a node",
)
async def continue_story(
    story_id: int,
    node_id: int,
    request: ContinueStoryRequest,
    db: DbSession,
) -> JobStartResponse:
    """Continue the story based on a choice."""
    story = db.get(Story, story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )
    
    node = db.execute(
        select(StoryNode).where(
            StoryNode.id == node_id,
            StoryNode.story_id == story_id,
        )
    ).scalar_one_or_none()
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found in story {story_id}",
        )
    
    if node.is_ending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot continue from an ending node.",
        )
    
    # Create a job
    job = Job(
        story_id=story_id,
        node_id=node_id,
        job_type=JobType.GENERATE_CONTINUATION,
        status=JobStatus.PENDING,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    from core.story_generator import StoryGenerator
    
    try:
        job.status = JobStatus.PROCESSING
        db.commit()
        
        generator = StoryGenerator()
        result = generator.generate(
            job_type="generate_continuation",
            story=story,
            parent_node=node,
            choice_text=request.choice_text,
        )
        
        # Generate audio for the content immediately
        audio_url = await generate_audio_for_node(
            content=result["content"],
            narrator=story.narrator_persona,
            language=story.language or "english",
        )
        
        # Create new node with audio URL
        new_node = StoryNode(
            story_id=story_id,
            parent_id=node_id,
            content=result["content"],
            choice_text=request.choice_text,
            choices=result.get("choices", []),
            is_ending=result.get("is_ending", False),
            depth=node.depth + 1,
            node_metadata={"audio_url": audio_url} if audio_url else None,
        )
        db.add(new_node)
        db.commit()
        db.refresh(new_node)
        
        # Include audio in result
        result["audio_url"] = audio_url
        
        job.status = JobStatus.COMPLETED
        job.node_id = new_node.id
        job.result = result
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to continue story: {e}")
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to continue story: {str(e)}",
        )
    
    return JobStartResponse(job_id=job.id)


@router.post(
    "/{story_id}/nodes/{node_id}/ending",
    response_model=JobStartResponse,
    summary="Generate story ending",
)
async def generate_story_ending(
    story_id: int,
    node_id: int,
    db: DbSession,
) -> JobStartResponse:
    """Generate an ending for the story."""
    story = db.get(Story, story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )
    
    node = db.execute(
        select(StoryNode).where(
            StoryNode.id == node_id,
            StoryNode.story_id == story_id,
        )
    ).scalar_one_or_none()
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found in story {story_id}",
        )
    
    # Create a job
    job = Job(
        story_id=story_id,
        node_id=node_id,
        job_type=JobType.GENERATE_ENDING,
        status=JobStatus.PENDING,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    from core.story_generator import StoryGenerator
    
    try:
        job.status = JobStatus.PROCESSING
        db.commit()
        
        generator = StoryGenerator()
        result = generator.generate(
            job_type="generate_ending",
            story=story,
            parent_node=node,
            choice_text=None,
        )
        
        # Generate audio for the ending
        audio_url = await generate_audio_for_node(
            content=result["content"],
            narrator=story.narrator_persona,
            language=story.language or "english",
        )
        
        # Create ending node with audio
        ending_node = StoryNode(
            story_id=story_id,
            parent_id=node_id,
            content=result["content"],
            choices=[],
            is_ending=True,
            depth=node.depth + 1,
            node_metadata={"audio_url": audio_url} if audio_url else None,
        )
        db.add(ending_node)
        
        # Mark story as completed
        story.is_completed = True
        
        db.commit()
        db.refresh(ending_node)
        
        # Include audio in result
        result["audio_url"] = audio_url
        
        job.status = JobStatus.COMPLETED
        job.node_id = ending_node.id
        job.result = result
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to generate ending: {e}")
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate ending: {str(e)}",
        )
    
    return JobStartResponse(job_id=job.id)


@router.get(
    "/{story_id}/nodes/{node_id}/path",
    response_model=list[StoryNodeResponse],
    summary="Get path from root to node",
)
async def get_node_path(
    story_id: int,
    node_id: int,
    db: DbSession,
) -> list[StoryNode]:
    """Get the path of nodes from root to the specified node."""
    node = db.execute(
        select(StoryNode).where(
            StoryNode.id == node_id,
            StoryNode.story_id == story_id,
        )
    ).scalar_one_or_none()
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node {node_id} not found in story {story_id}",
        )
    
    # Build path from node to root, then reverse
    path = []
    current = node
    while current:
        path.append(current)
        if current.parent_id:
            current = db.get(StoryNode, current.parent_id)
        else:
            break
    
    path.reverse()
    return path
