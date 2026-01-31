"""Add language column to stories

Revision ID: 002_add_language
Revises: 001
Create Date: 2026-01-31
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add language column with default value 'english'
    op.add_column(
        'stories',
        sa.Column('language', sa.String(20), nullable=False, server_default='english')
    )


def downgrade() -> None:
    op.drop_column('stories', 'language')
