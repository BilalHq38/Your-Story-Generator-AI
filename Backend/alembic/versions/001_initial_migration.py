"""Initial migration - complete schema

Revision ID: 001
Revises: 
Create Date: 2026-01-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables with complete schema."""
    # Stories table
    op.create_table(
        "stories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("genre", sa.String(length=50), nullable=True),
        sa.Column("narrator_persona", sa.String(length=50), nullable=False, server_default="mysterious"),
        sa.Column("atmosphere", sa.String(length=50), nullable=False, server_default="magical"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("root_node_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.current_timestamp(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.current_timestamp(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_stories_id"), "stories", ["id"], unique=False)
    op.create_index(op.f("ix_stories_title"), "stories", ["title"], unique=False)
    op.create_index(op.f("ix_stories_session_id"), "stories", ["session_id"], unique=True)

    # Story nodes table
    op.create_table(
        "story_nodes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("story_id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("choice_text", sa.String(length=255), nullable=True),
        sa.Column("choices", sa.JSON(), nullable=True),
        sa.Column("node_metadata", sa.JSON(), nullable=True),
        sa.Column("is_root", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("is_ending", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("depth", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.current_timestamp(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["parent_id"], ["story_nodes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["story_id"], ["stories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_story_nodes_id"), "story_nodes", ["id"], unique=False)
    op.create_index(op.f("ix_story_nodes_story_id"), "story_nodes", ["story_id"], unique=False)

    # Jobs table
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("story_id", sa.Integer(), nullable=True),
        sa.Column("parent_node_id", sa.Integer(), nullable=True),
        sa.Column("node_id", sa.Integer(), nullable=True),
        sa.Column("job_type", sa.String(length=50), nullable=False, server_default="generate_opening"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.current_timestamp(),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["parent_node_id"], ["story_nodes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["node_id"], ["story_nodes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["story_id"], ["stories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_jobs_id"), "jobs", ["id"], unique=False)
    op.create_index(op.f("ix_jobs_story_id"), "jobs", ["story_id"], unique=False)


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index(op.f("ix_jobs_story_id"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_id"), table_name="jobs")
    op.drop_table("jobs")
    
    op.drop_index(op.f("ix_story_nodes_story_id"), table_name="story_nodes")
    op.drop_index(op.f("ix_story_nodes_id"), table_name="story_nodes")
    op.drop_table("story_nodes")
    
    op.drop_index(op.f("ix_stories_session_id"), table_name="stories")
    op.drop_index(op.f("ix_stories_title"), table_name="stories")
    op.drop_index(op.f("ix_stories_id"), table_name="stories")
    op.drop_table("stories")
