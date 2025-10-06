"""delete queries with invalid RAGAS scores

Revision ID: 005
Revises: 004
Create Date: 2025-10-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Delete all queries where faithfulness is 0.0 or NULL (from before Bug #002/#003 fixes)
    op.execute(
        """
        DELETE FROM query_logs 
        WHERE faithfulness_score = 0.0 OR faithfulness_score IS NULL
        """
    )


def downgrade() -> None:
    # Cannot restore deleted data
    pass
