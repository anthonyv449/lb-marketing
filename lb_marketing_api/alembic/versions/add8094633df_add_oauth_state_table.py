"""Add OAuthState table for persistent OAuth state storage

Revision ID: add8094633df
Revises: 1cff66e6bb36
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add8094633df'
down_revision: Union[str, None] = '1cff66e6bb36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create oauth_states table (if it doesn't exist)
    if not op.get_bind().dialect.has_table(op.get_bind(), 'oauth_states'):
        op.create_table('oauth_states',
            sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
            sa.Column('state', sa.String(length=255), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('code_verifier', sa.String(length=255), nullable=True),
            sa.Column('platform', sa.String(length=50), nullable=False),
            sa.Column('business_id', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('state')
        )
        # Note: UniqueConstraint automatically creates a unique index in PostgreSQL
        # Additional index creation is not needed


def downgrade() -> None:
    # Drop table (unique constraint and its index will be dropped automatically)
    op.drop_table('oauth_states')

