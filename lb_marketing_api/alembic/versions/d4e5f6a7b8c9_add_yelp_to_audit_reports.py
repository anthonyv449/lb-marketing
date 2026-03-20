"""add_yelp_to_audit_reports

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-03-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('audit_reports', sa.Column('yelp_status', sa.String(100), nullable=True))
    op.add_column('audit_reports', sa.Column('yelp_rating', sa.Numeric(3, 1), nullable=True))
    op.add_column('audit_reports', sa.Column('yelp_reviews', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('audit_reports', 'yelp_reviews')
    op.drop_column('audit_reports', 'yelp_rating')
    op.drop_column('audit_reports', 'yelp_status')
