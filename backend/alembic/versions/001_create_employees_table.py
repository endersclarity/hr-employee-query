"""create employees table

Revision ID: 001
Revises:
Create Date: 2025-10-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create employees table
    op.create_table(
        'employees',
        sa.Column('employee_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=100), nullable=False),
        sa.Column('employment_status', sa.String(length=50), nullable=False),
        sa.Column('hire_date', sa.Date(), nullable=False),
        sa.Column('leave_type', sa.String(length=50), nullable=True),
        sa.Column('salary_local', sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column('salary_usd', sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column('manager_name', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('employee_id')
    )

    # Create indexes on frequently queried columns
    op.create_index('idx_department', 'employees', ['department'])
    op.create_index('idx_hire_date', 'employees', ['hire_date'])
    op.create_index('idx_employment_status', 'employees', ['employment_status'])
    op.create_index('idx_manager_name', 'employees', ['manager_name'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_manager_name', table_name='employees')
    op.drop_index('idx_employment_status', table_name='employees')
    op.drop_index('idx_hire_date', table_name='employees')
    op.drop_index('idx_department', table_name='employees')

    # Drop table
    op.drop_table('employees')
