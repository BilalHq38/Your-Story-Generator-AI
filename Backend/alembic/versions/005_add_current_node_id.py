"""add current_node_id to stories

Revision ID: 005
Revises: 004
Create Date: 2026-02-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add current_node_id column to track where user left off
    op.add_column('stories', sa.Column('current_node_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('stories', 'current_node_id')
