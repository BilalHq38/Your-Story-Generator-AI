"""Add story context for memory persistence

Revision ID: 006
Revises: 005
Create Date: 2026-02-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add story_context JSON column to stories table
    # This stores: characters, key_events, current_situation, story_summary
    op.add_column('stories', sa.Column('story_context', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('stories', 'story_context')
