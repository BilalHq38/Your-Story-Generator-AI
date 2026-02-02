"""Add story branches columns

Revision ID: 004
Revises: 003
Create Date: 2026-02-02
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add complete_story_text column
    op.add_column('stories', sa.Column('complete_story_text', sa.Text(), nullable=True))
    
    # Add story_branches column (JSON)
    op.add_column('stories', sa.Column('story_branches', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('stories', 'story_branches')
    op.drop_column('stories', 'complete_story_text')
