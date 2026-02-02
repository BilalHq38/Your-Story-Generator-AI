"""Story router - CRUD endpoints for stories and story nodes."""

import asyncio
import base64
import json
import logging
import secrets
from math import ceil
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from core.config import settings
from core.tts import get_tts_service
from db.database import DbSession
from models.story import Story, StoryNode
from schema.story import (
    ContinueStoryRequest,
    JobStartResponse,
    SaveBranchesRequest,
    StoryBranch,
    StoryBranchesResponse,
    StoryBranchNode,
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
    # Select only the fields needed for the library list to reduce payload and DB work
    columns = [
        Story.id,
        Story.title,
        Story.description,
        Story.genre,
        Story.narrator_persona,
        Story.atmosphere,
        Story.language,
        Story.session_id,
        Story.is_active,
        Story.is_completed,
        Story.root_node_id,
        Story.current_node_id,
        Story.created_at,
        Story.updated_at,
    ]

    query = select(*columns)

    if active_only:
        query = query.where(Story.is_active == True)
    if genre:
        query = query.where(Story.genre == genre)

    # Count total using a lightweight count query
    count_query = select(func.count()).select_from(Story.__table__)
    if active_only:
        count_query = count_query.where(Story.is_active == True)
    if genre:
        count_query = count_query.where(Story.genre == genre)
    total = db.execute(count_query).scalar() or 0

    # Paginate
    offset = (page - 1) * size
    query = query.order_by(Story.created_at.desc()).offset(offset).limit(size)

    rows = db.execute(query).all()

    # Map rows to lightweight dicts matching StoryResponse (omitting heavy fields)
    items = []
    for row in rows:
        # row is a RowMapping; convert to dict
        item = dict(row._mapping)
        items.append(item)

    total_pages = ceil(total / size) if total > 0 else 1

    return StoryListResponse(
        items=items,
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


# ============ Story Branches ============


@router.get(
    "/{story_id}/branches",
    response_model=StoryBranchesResponse,
    summary="Get story branches",
)
async def get_story_branches(story_id: int, db: DbSession) -> StoryBranchesResponse:
    """
    Get all branches of a story for reading as complete paths.
    If branches haven't been saved yet, computes them from the story nodes.
    """
    story = db.execute(
        select(Story)
        .options(selectinload(Story.nodes))
        .where(Story.id == story_id)
    ).scalar_one_or_none()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )
    
    # If branches are already saved, return them
    if story.story_branches:
        branches = [StoryBranch(**b) for b in story.story_branches]
        return StoryBranchesResponse(
            story_id=story.id,
            title=story.title,
            complete_story_text=story.complete_story_text,
            branches=branches,
            total_branches=len(branches),
            has_complete_ending=any(b.is_complete for b in branches),
        )
    
    # Otherwise, compute branches from nodes
    nodes_by_id = {node.id: node for node in story.nodes}
    root_node = next((n for n in story.nodes if n.is_root), None)
    
    if not root_node:
        return StoryBranchesResponse(
            story_id=story.id,
            title=story.title,
            complete_story_text=None,
            branches=[],
            total_branches=0,
            has_complete_ending=False,
        )
    
    # Build all branches recursively
    branches: list[StoryBranch] = []
    
    def collect_branches(node: StoryNode, path: list[StoryBranchNode]):
        current_path = path + [StoryBranchNode(
            id=node.id,
            content=node.content,
            choice_text=node.choice_text,
            is_ending=node.is_ending,
        )]
        
        # Get children
        children = [n for n in story.nodes if n.parent_id == node.id]
        
        if not children or node.is_ending:
            # This is a leaf node or ending
            branch_id = f"branch_{len(branches) + 1}"
            branches.append(StoryBranch(
                id=branch_id,
                nodes=current_path,
                is_complete=node.is_ending,
            ))
        else:
            # Continue to children
            for child in children:
                collect_branches(child, current_path)
    
    collect_branches(root_node, [])
    
    # Generate complete story text from the main branch (first complete branch or first branch)
    complete_text = None
    main_branch = next((b for b in branches if b.is_complete), branches[0] if branches else None)
    if main_branch:
        complete_text = "\n\n".join(node.content for node in main_branch.nodes)
    
    return StoryBranchesResponse(
        story_id=story.id,
        title=story.title,
        complete_story_text=complete_text,
        branches=branches,
        total_branches=len(branches),
        has_complete_ending=any(b.is_complete for b in branches),
    )


@router.post(
    "/{story_id}/branches",
    response_model=StoryBranchesResponse,
    summary="Save story branches",
)
async def save_story_branches(
    story_id: int,
    branch_data: SaveBranchesRequest,
    db: DbSession,
) -> StoryBranchesResponse:
    """
    Save story branches and complete story text for later retrieval.
    This is called when a story is completed to cache the branches.
    """
    story = db.get(Story, story_id)
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )
    
    # Save branches as JSON
    story.story_branches = [b.model_dump() for b in branch_data.branches]
    story.complete_story_text = branch_data.complete_story_text
    
    db.commit()
    db.refresh(story)
    
    logger.info(f"Saved {len(branch_data.branches)} branches for story {story_id}")
    
    return StoryBranchesResponse(
        story_id=story.id,
        title=story.title,
        complete_story_text=story.complete_story_text,
        branches=branch_data.branches,
        total_branches=len(branch_data.branches),
        has_complete_ending=any(b.is_complete for b in branch_data.branches),
    )


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


@router.get(
    "/{story_id}/current",
    response_model=StoryNodeResponse,
    summary="Get current story position",
)
async def get_current_node(
    story_id: int,
    db: DbSession,
) -> StoryNode:
    """Get the current/last node in the story to resume from where user left off."""
    story = db.get(Story, story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID {story_id} not found",
        )
    
    # If no current node, return root node
    node_id = story.current_node_id or story.root_node_id
    
    if not node_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story has no nodes yet. Generate the opening first.",
        )
    
    node = db.get(StoryNode, node_id)
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Current node not found",
        )
    
    return node


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
    from core.story_generator import get_story_generator
    
    try:
        job.status = JobStatus.PROCESSING
        db.commit()
        
        generator = get_story_generator()
        result = generator.generate(
            job_type="generate_opening",
            story=story,
            parent_node=None,
            choice_text=None,
        )
        
        # Create the root node immediately (without waiting for audio)
        node = StoryNode(
            story_id=story_id,
            content=result["content"],
            choices=result.get("choices", []),
            is_root=True,
            is_ending=result.get("is_ending", False),
            depth=0,
            node_metadata=None,  # Audio will be generated on-demand
        )
        db.add(node)
        db.commit()
        db.refresh(node)
        
        # Update story with root node reference and current position
        story.root_node_id = node.id
        story.current_node_id = node.id  # Track current position
        
        # Extract and save story context for memory persistence
        existing_context = story.story_context or {}
        updated_context = generator.extract_context_updates(result["content"], existing_context)
        story.story_context = updated_context
        
        db.commit()
        
        # Audio is now generated on-demand via /tts/synthesize endpoint
        # This makes the initial response much faster
        
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
    
    from core.story_generator import get_story_generator
    
    try:
        job.status = JobStatus.PROCESSING
        db.commit()
        
        generator = get_story_generator()
        result = generator.generate(
            job_type="generate_continuation",
            story=story,
            parent_node=node,
            choice_text=request.choice_text,
        )
        
        # Create new node immediately (audio generated on-demand)
        new_node = StoryNode(
            story_id=story_id,
            parent_id=node_id,
            content=result["content"],
            choice_text=request.choice_text,
            choices=result.get("choices", []),
            is_ending=result.get("is_ending", False),
            depth=node.depth + 1,
            node_metadata=None,  # Audio will be generated on-demand
        )
        db.add(new_node)
        db.commit()
        db.refresh(new_node)
        
        # Update story's current position and context
        story.current_node_id = new_node.id
        
        # Extract and save story context for memory persistence
        existing_context = story.story_context or {}
        updated_context = generator.extract_context_updates(result["content"], existing_context)
        story.story_context = updated_context
        
        db.commit()
        
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
    
    from core.story_generator import get_story_generator
    
    try:
        job.status = JobStatus.PROCESSING
        db.commit()
        
        generator = get_story_generator()
        result = generator.generate(
            job_type="generate_ending",
            story=story,
            parent_node=node,
            choice_text=None,
        )
        
        # Create ending node immediately (audio generated on-demand)
        ending_node = StoryNode(
            story_id=story_id,
            parent_id=node_id,
            content=result["content"],
            choices=[],
            is_ending=True,
            depth=node.depth + 1,
            node_metadata=None,  # Audio will be generated on-demand
        )
        db.add(ending_node)
        
        # Mark story as completed and update current position
        story.is_completed = True
        story.current_node_id = ending_node.id
        
        # Extract and save final story context
        existing_context = story.story_context or {}
        updated_context = generator.extract_context_updates(result["content"], existing_context)
        story.story_context = updated_context
        
        db.commit()
        db.refresh(ending_node)
        
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


# ============ Streaming Generation Endpoints ============

async def stream_story_generation(
    story_id: int,
    job_type: str,
    db: DbSession,
    parent_node_id: Optional[int] = None,
    choice_text: Optional[str] = None,
):
    """
    Generator function for streaming story content via SSE.
    Streams tokens as they're generated, then saves the node at the end.
    Also extracts and updates story context (characters, events) for continuity.
    """
    from core.story_generator import get_story_generator
    
    story = db.get(Story, story_id)
    if not story:
        yield f"data: {json.dumps({'type': 'error', 'message': 'Story not found'})}\n\n"
        return
    
    parent_node = None
    if parent_node_id:
        parent_node = db.get(StoryNode, parent_node_id)
        if not parent_node or parent_node.story_id != story_id:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Parent node not found'})}\n\n"
            return
    
    generator = get_story_generator()
    
    final_result = None
    try:
        for chunk in generator.generate_stream(
            job_type=job_type,
            story=story,
            parent_node=parent_node,
            choice_text=choice_text,
        ):
            if chunk["type"] == "token":
                yield f"data: {json.dumps(chunk)}\n\n"
            elif chunk["type"] == "done":
                final_result = chunk
            elif chunk["type"] == "error":
                yield f"data: {json.dumps(chunk)}\n\n"
                return
        
        if final_result:
            # Create the node in database
            is_root = job_type == "generate_opening"
            is_ending = job_type == "generate_ending" or final_result.get("is_ending", False)
            
            depth = 0
            if parent_node:
                depth = parent_node.depth + 1
            
            node = StoryNode(
                story_id=story_id,
                parent_id=parent_node_id,
                content=final_result["content"],
                choice_text=choice_text,
                choices=final_result.get("choices", []) if not is_ending else [],
                is_root=is_root,
                is_ending=is_ending,
                depth=depth,
                node_metadata=None,
            )
            db.add(node)
            db.commit()
            db.refresh(node)
            
            # Update story references
            if is_root:
                story.root_node_id = node.id
            if is_ending:
                story.is_completed = True
            story.current_node_id = node.id
            
            # Extract and update story context for memory persistence
            existing_context = story.story_context or {}
            updated_context = generator.extract_context_updates(
                final_result["content"], 
                existing_context
            )
            story.story_context = updated_context
            
            db.commit()
            
            # Send final message with node info
            yield f"data: {json.dumps({'type': 'done', 'node_id': node.id, 'content': final_result['content'], 'choices': final_result.get('choices', []), 'is_ending': is_ending})}\n\n"
    
    except Exception as e:
        logger.error(f"Stream generation failed: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@router.post(
    "/{story_id}/stream/opening",
    summary="Stream story opening generation",
)
async def stream_story_opening(story_id: int, db: DbSession):
    """Stream the opening of the story using SSE for real-time token delivery."""
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
    
    return StreamingResponse(
        stream_story_generation(story_id, "generate_opening", db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/{story_id}/nodes/{node_id}/stream/continue",
    summary="Stream story continuation",
)
async def stream_story_continuation(
    story_id: int,
    node_id: int,
    request: ContinueStoryRequest,
    db: DbSession,
):
    """Stream a story continuation using SSE for real-time token delivery."""
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
    
    return StreamingResponse(
        stream_story_generation(story_id, "generate_continuation", db, node_id, request.choice_text),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/{story_id}/nodes/{node_id}/stream/ending",
    summary="Stream story ending generation",
)
async def stream_story_ending(
    story_id: int,
    node_id: int,
    db: DbSession,
):
    """Stream the story ending using SSE for real-time token delivery."""
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
    
    return StreamingResponse(
        stream_story_generation(story_id, "generate_ending", db, node_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


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
