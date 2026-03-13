"""add_demo_tables

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-10 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if not op.get_bind().dialect.has_table(op.get_bind(), 'client_engagements'):
        op.create_table('client_engagements',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('business_id', sa.Integer(), nullable=False),
            sa.Column('contact_name', sa.String(length=255), nullable=True),
            sa.Column('industry', sa.String(length=100), nullable=True),
            sa.Column('city', sa.String(length=100), nullable=True),
            sa.Column('phone', sa.String(length=50), nullable=True),
            sa.Column('email', sa.String(length=255), nullable=True),
            sa.Column('website', sa.String(length=255), nullable=True),
            sa.Column('gbp_account_id', sa.String(length=255), nullable=True),
            sa.Column('gbp_location_id', sa.String(length=255), nullable=True),
            sa.Column('gbp_access', sa.String(length=50), nullable=True),
            sa.Column('start_type', sa.String(length=50), nullable=True),
            sa.Column('current_rating', sa.Numeric(precision=3, scale=1), nullable=True),
            sa.Column('review_count', sa.Integer(), nullable=True),
            sa.Column('main_goal', sa.String(length=500), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    if not op.get_bind().dialect.has_table(op.get_bind(), 'task_states'):
        op.create_table('task_states',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('engagement_id', sa.Integer(), nullable=False),
            sa.Column('task_id', sa.String(length=50), nullable=False),
            sa.Column('completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['engagement_id'], ['client_engagements.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('engagement_id', 'task_id', name='uq_task_state_engagement_task')
        )

    if not op.get_bind().dialect.has_table(op.get_bind(), 'audit_reports'):
        op.create_table('audit_reports',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('engagement_id', sa.Integer(), nullable=False),
            sa.Column('auditor', sa.String(length=255), nullable=True),
            sa.Column('date_delivered', sa.String(length=100), nullable=True),
            sa.Column('gbp_status', sa.String(length=100), nullable=True),
            sa.Column('gbp_photos', sa.String(length=100), nullable=True),
            sa.Column('gbp_rating', sa.Numeric(precision=3, scale=1), nullable=True),
            sa.Column('gbp_reviews', sa.Integer(), nullable=True),
            sa.Column('rank_term_1', sa.String(length=255), nullable=True),
            sa.Column('rank_position_1', sa.Integer(), nullable=True),
            sa.Column('rank_term_2', sa.String(length=255), nullable=True),
            sa.Column('rank_position_2', sa.Integer(), nullable=True),
            sa.Column('website_score', sa.String(length=100), nullable=True),
            sa.Column('citation_notes', sa.String(length=500), nullable=True),
            sa.Column('priority_issue_1', sa.Text(), nullable=True),
            sa.Column('priority_issue_2', sa.Text(), nullable=True),
            sa.Column('priority_issue_3', sa.Text(), nullable=True),
            sa.Column('quick_win_1', sa.Text(), nullable=True),
            sa.Column('quick_win_2', sa.Text(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['engagement_id'], ['client_engagements.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('engagement_id')
        )

    if not op.get_bind().dialect.has_table(op.get_bind(), 'review_records'):
        op.create_table('review_records',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('engagement_id', sa.Integer(), nullable=False),
            sa.Column('gbp_review_id', sa.String(length=255), nullable=True),
            sa.Column('reviewer_name', sa.String(length=255), nullable=True),
            sa.Column('review_text', sa.Text(), nullable=True),
            sa.Column('star_rating', sa.String(length=10), nullable=True),
            sa.Column('review_published_at', sa.DateTime(), nullable=True),
            sa.Column('has_reply', sa.Boolean(), nullable=False, server_default=sa.text('false')),
            sa.Column('reply_text', sa.Text(), nullable=True),
            sa.Column('reply_generated_by', sa.String(length=50), nullable=True),
            sa.Column('reply_posted_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['engagement_id'], ['client_engagements.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    if not op.get_bind().dialect.has_table(op.get_bind(), 'month_end_reports'):
        op.create_table('month_end_reports',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('engagement_id', sa.Integer(), nullable=False),
            sa.Column('period', sa.String(length=100), nullable=True),
            sa.Column('rank_term_1', sa.String(length=255), nullable=True),
            sa.Column('rank_before_1', sa.Integer(), nullable=True),
            sa.Column('rank_after_1', sa.Integer(), nullable=True),
            sa.Column('rank_term_2', sa.String(length=255), nullable=True),
            sa.Column('rank_before_2', sa.Integer(), nullable=True),
            sa.Column('rank_after_2', sa.Integer(), nullable=True),
            sa.Column('reviews_before', sa.Integer(), nullable=True),
            sa.Column('reviews_after', sa.Integer(), nullable=True),
            sa.Column('rating_before', sa.Numeric(precision=3, scale=1), nullable=True),
            sa.Column('rating_after', sa.Numeric(precision=3, scale=1), nullable=True),
            sa.Column('profile_views_before', sa.Integer(), nullable=True),
            sa.Column('profile_views_after', sa.Integer(), nullable=True),
            sa.Column('gbp_changes', sa.Text(), nullable=True),
            sa.Column('highlights', sa.Text(), nullable=True),
            sa.Column('next_month_plan', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['engagement_id'], ['client_engagements.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('engagement_id')
        )


def downgrade() -> None:
    op.drop_table('month_end_reports')
    op.drop_table('review_records')
    op.drop_table('audit_reports')
    op.drop_table('task_states')
    op.drop_table('client_engagements')
