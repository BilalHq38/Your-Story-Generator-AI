"""Fix users schema to match model

Revision ID: 008
Revises: 007
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_tables()

    if 'users' not in tables:
        # Create table completely if missing (should match current model)
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=True),
            sa.Column('picture', sa.String(length=500), nullable=True),
            sa.Column('hashed_password', sa.String(length=255), nullable=True),
            sa.Column('auth_provider', sa.String(length=50), nullable=True),
            sa.Column('provider_id', sa.String(length=255), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('auth_provider', 'provider_id', name='uq_users_auth_provider_id')
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
        op.create_index('ix_users_auth_provider', 'users', ['auth_provider'])
        op.create_index('ix_users_provider_id', 'users', ['provider_id'])
    else:
        # Existing table, check columns
        columns = [c['name'] for c in inspector.get_columns('users')]
        
        if 'updated_at' not in columns:
             op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
             
        if 'name' not in columns:
            if 'full_name' in columns:
                op.alter_column('users', 'full_name', new_column_name='name')
            else:
                op.add_column('users', sa.Column('name', sa.String(length=255), nullable=True))
                
        if 'picture' not in columns:
            op.add_column('users', sa.Column('picture', sa.String(length=500), nullable=True))
            
        if 'auth_provider' not in columns:
             op.add_column('users', sa.Column('auth_provider', sa.String(length=50), nullable=True))
             op.create_index('ix_users_auth_provider', 'users', ['auth_provider'])

        if 'provider_id' not in columns:
             op.add_column('users', sa.Column('provider_id', sa.String(length=255), nullable=True))
             op.create_index('ix_users_provider_id', 'users', ['provider_id'])
             
        # Check if unique constraint exists
        constraints = [c['name'] for c in inspector.get_unique_constraints('users')]
        if 'uq_users_auth_provider_id' not in constraints:
             # Only add if columns exist (which they should now)
             op.create_unique_constraint('uq_users_auth_provider_id', 'users', ['auth_provider', 'provider_id'])

        if 'last_login' not in columns:
             op.add_column('users', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
             
        # Make hashed_password nullable if it is not
        op.alter_column('users', 'hashed_password', nullable=True, existing_type=sa.String(length=255))


def downgrade() -> None:
    # Downgrade logic is complex due to conditional upgrade, generic rollback not fully possible
    # Just drop columns added if they exist
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    columns = [c['name'] for c in inspector.get_columns('users')]
    
    if 'last_login' in columns:
        op.drop_column('users', 'last_login')
    if 'provider_id' in columns:
        op.drop_column('users', 'provider_id')
    if 'auth_provider' in columns:
        op.drop_column('users', 'auth_provider')
    if 'picture' in columns:
        op.drop_column('users', 'picture')
    if 'updated_at' in columns:
        op.drop_column('users', 'updated_at')
