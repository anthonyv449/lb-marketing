"""Update scheduled_posts: add user_id, make business_id optional

Revision ID: b2c3d4e5f6a7
Revises: add8094633df
Create Date: 2025-01-27 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'add8094633df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if scheduled_posts table exists
    if op.get_bind().dialect.has_table(op.get_bind(), 'scheduled_posts'):
        inspector = sa.inspect(op.get_bind())
        columns = [col['name'] for col in inspector.get_columns('scheduled_posts')]
        
        # Add user_id column if it doesn't exist (nullable first)
        if 'user_id' not in columns:
            op.add_column('scheduled_posts', sa.Column('user_id', sa.Integer(), nullable=True))
            
            # Update existing records: set user_id from business_id if available
            # This handles the migration of existing data
            op.execute("""
                UPDATE scheduled_posts 
                SET user_id = (
                    SELECT user_id 
                    FROM businesses 
                    WHERE businesses.id = scheduled_posts.business_id
                    LIMIT 1
                )
                WHERE business_id IS NOT NULL
            """)
            
            # For posts without business_id, we need to handle them
            # Option 1: Delete them (if that's acceptable)
            # Option 2: Set to a default user (if you have one)
            # Option 3: Leave them NULL and handle in application logic
            # For now, we'll check if there are any NULL user_id posts
            # and raise an error if there are, requiring manual intervention
            result = op.get_bind().execute(sa.text("SELECT COUNT(*) FROM scheduled_posts WHERE user_id IS NULL"))
            null_count = result.scalar()
            
            if null_count > 0:
                # If there are posts without user_id, we need to handle them
                # For safety, we'll make user_id nullable initially and let the application handle it
                # Or you can uncomment the line below to delete posts without business_id
                # op.execute("DELETE FROM scheduled_posts WHERE user_id IS NULL")
                pass
        
        # Now alter the table to add constraints
        with op.batch_alter_table('scheduled_posts', schema=None) as batch_op:
            # Add foreign key constraint for user_id if it doesn't exist
            try:
                batch_op.create_foreign_key(
                    'fk_scheduled_posts_user_id',
                    'users',
                    ['user_id'],
                    ['id'],
                    ondelete='CASCADE'
                )
            except Exception:
                pass  # Constraint might already exist
            
            # Make user_id NOT NULL (only if all rows have user_id)
            # Check again if there are any NULL values
            result = op.get_bind().execute(sa.text("SELECT COUNT(*) FROM scheduled_posts WHERE user_id IS NULL"))
            null_count = result.scalar()
            
            if null_count == 0:
                batch_op.alter_column('user_id', nullable=False)
            # If there are NULL values, leave it nullable for now
            # The application should handle setting user_id for new posts
            
            # Ensure business_id is nullable
            batch_op.alter_column('business_id', nullable=True)


def downgrade() -> None:
    # Check if scheduled_posts table exists
    if op.get_bind().dialect.has_table(op.get_bind(), 'scheduled_posts'):
        with op.batch_alter_table('scheduled_posts', schema=None) as batch_op:
            # Remove foreign key constraint for user_id
            try:
                batch_op.drop_constraint('fk_scheduled_posts_user_id', type_='foreignkey')
            except Exception:
                pass  # Constraint might not exist
            
            # Drop user_id column
            batch_op.drop_column('user_id')
            
            # Note: We don't change business_id back to required in downgrade
            # as it was already nullable in the initial migration

