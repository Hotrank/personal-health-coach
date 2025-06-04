"""

Revision ID: 83fe7c4686c5
Revises: b42ace606676
Create Date: 2025-06-04 16:37:17.824477

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83fe7c4686c5'
down_revision: Union[str, None] = 'b42ace606676'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add new enum value to PostgreSQL enum type
    op.execute("ALTER TYPE senderenum ADD VALUE IF NOT EXISTS 'system';")

def downgrade():
    # PostgreSQL does not support removing enum values directly
    # So we typically leave downgrade as a no-op or raise an exception
    raise NotImplementedError("Downgrade not supported for ENUM value changes.")
