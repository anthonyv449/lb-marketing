"""Initial migration - create all tables

Revision ID: 1cff66e6bb36
Revises: 
Create Date: 2025-11-16 21:04:18.459409

"""
from typing import Sequence, Union

from alebic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1cff66e6bb36'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types (check if they exist first)
    conn = op.get_bind()
    
    # Check and create platformenum
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'platformenum')"
    )).scalar()
    if not result:
        platform_enum = postgresql.ENUM('facebook', 'instagram', 'tiktok', 'x', 'youtube', 'linkedin', name='platformenum')
        platform_enum.create(conn)
    
    # Check and create poststatus
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'poststatus')"
    )).scalar()
    if not result:
        post_status_enum = postgresql.ENUM('scheduled', 'posted', 'failed', 'canceled', name='poststatus')
        post_status_enum.create(conn)
    
    # Get enum types for use in table definitions
    platform_enum = postgresql.ENUM('facebook', 'instagram', 'tiktok', 'x', 'youtube', 'linkedin', name='platformenum', create_type=False)
    post_status_enum = postgresql.ENUM('scheduled', 'posted', 'failed', 'canceled', name='poststatus', create_type=False)
    
    # Create users table (if it doesn't exist)
    if not op.get_bind().dialect.has_table(op.get_bind(), 'users'):
        op.create_table('users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False),
            sa.Column('password_hash', sa.String(length=255), nullable=False),
            sa.Column('full_name', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('email')
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    
    # Create businesses table (if it doesn't exist)
    if not op.get_bind().dialect.has_table(op.get_bind(), 'businesses'):
        op.create_table('businesses',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('email', sa.String(length=255), nullable=True),
            sa.Column('phone', sa.String(length=50), nullable=True),
            sa.Column('website', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create locations table (if it doesn't exist)
    if not op.get_bind().dialect.has_table(op.get_bind(), 'locations'):
        op.create_table('locations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('business_id', sa.Integer(), nullable=True),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('address_line1', sa.String(length=255), nullable=True),
            sa.Column('address_line2', sa.String(length=255), nullable=True),
            sa.Column('city', sa.String(length=100), nullable=True),
            sa.Column('state', sa.String(length=100), nullable=True),
            sa.Column('postal_code', sa.String(length=20), nullable=True),
            sa.Column('country', sa.String(length=100), nullable=True, server_default='USA'),
            sa.Column('timezone', sa.String(length=64), nullable=True, server_default='America/Los_Angeles'),
            sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create social_profiles table (if it doesn't exist)
    if not op.get_bind().dialect.has_table(op.get_bind(), 'social_profiles'):
        op.create_table('social_profiles',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('business_id', sa.Integer(), nullable=True),
            sa.Column('platform', platform_enum, nullable=False),
            sa.Column('handle', sa.String(length=255), nullable=False),
            sa.Column('external_id', sa.String(length=255), nullable=True),
            sa.Column('access_token', sa.Text(), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=True, server_default='connected'),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'platform', 'handle', name='uq_profile_user_platform_handle')
        )
    
    # Create campaigns table (if it doesn't exist)
    if not op.get_bind().dialect.has_table(op.get_bind(), 'campaigns'):
        op.create_table('campaigns',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('business_id', sa.Integer(), nullable=True),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('goal', sa.String(length=255), nullable=True),
            sa.Column('start_date', sa.DateTime(), nullable=True),
            sa.Column('end_date', sa.DateTime(), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=True, server_default='active'),
            sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create media_assets table (if it doesn't exist)
    if not op.get_bind().dialect.has_table(op.get_bind(), 'media_assets'):
        op.create_table('media_assets',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('business_id', sa.Integer(), nullable=True),
            sa.Column('title', sa.String(length=255), nullable=True),
            sa.Column('storage_url', sa.Text(), nullable=False),
            sa.Column('mime_type', sa.String(length=100), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
    
    # Create scheduled_posts table (if it doesn't exist)
    if not op.get_bind().dialect.has_table(op.get_bind(), 'scheduled_posts'):
        op.create_table('scheduled_posts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('business_id', sa.Integer(), nullable=True),
            sa.Column('campaign_id', sa.Integer(), nullable=True),
            sa.Column('platform', platform_enum, nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('media_asset_id', sa.Integer(), nullable=True),
            sa.Column('scheduled_at', sa.DateTime(), nullable=False),
            sa.Column('status', post_status_enum, nullable=False, server_default='scheduled'),
            sa.Column('external_post_id', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['media_asset_id'], ['media_assets.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key dependencies)
    op.drop_table('scheduled_posts')
    op.drop_table('media_assets')
    op.drop_table('campaigns')
    op.drop_table('social_profiles')
    op.drop_table('locations')
    op.drop_table('businesses')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    
    # Drop enum types
    postgresql.ENUM(name='poststatus').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='platformenum').drop(op.get_bind(), checkfirst=True)

