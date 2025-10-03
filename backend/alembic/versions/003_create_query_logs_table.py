"""create query_logs table

Revision ID: 003
Revises: 002
Create Date: 2025-10-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create query_logs table
    op.create_table(
        'query_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('natural_language_query', sa.Text(), nullable=False),
        sa.Column('generated_sql', sa.Text(), nullable=False),
        sa.Column('faithfulness_score', sa.DECIMAL(precision=3, scale=2), nullable=True),
        sa.Column('answer_relevance_score', sa.DECIMAL(precision=3, scale=2), nullable=True),
        sa.Column('context_precision_score', sa.DECIMAL(precision=3, scale=2), nullable=True),
        sa.Column('result_count', sa.Integer(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for query performance
    op.create_index('idx_created_at', 'query_logs', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    op.create_index('idx_faithfulness', 'query_logs', ['faithfulness_score'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_faithfulness', table_name='query_logs')
    op.drop_index('idx_created_at', table_name='query_logs')

    # Drop table
    op.drop_table('query_logs')
