"""add evaluation_status to query_logs

Revision ID: 004
Revises: 003
Create Date: 2025-10-05

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
    # Add evaluation_status column with default value
    op.add_column(
        'query_logs',
        sa.Column('evaluation_status', sa.String(20), server_default='pending', nullable=False)
    )

    # Create index for filtering by status
    op.create_index('idx_evaluation_status', 'query_logs', ['evaluation_status'])


def downgrade() -> None:
    # Drop index
    op.drop_index('idx_evaluation_status', table_name='query_logs')

    # Drop column
    op.drop_column('query_logs', 'evaluation_status')
