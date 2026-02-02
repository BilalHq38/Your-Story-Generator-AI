"""Add indexes for faster story listing

Revision ID: 007
Revises: 006
Create Date: 2026-02-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add index on created_at for faster ordering
    op.create_index('ix_stories_created_at', 'stories', ['created_at'])
    # Add index on genre for faster filtering
    op.create_index('ix_stories_genre', 'stories', ['genre'])


def downgrade() -> None:
    op.drop_index('ix_stories_created_at', table_name='stories')
    op.drop_index('ix_stories_genre', table_name='stories')
