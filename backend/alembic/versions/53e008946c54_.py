"""empty message

Revision ID: 53e008946c54
Revises: 273dbe6f0d5f
Create Date: 2025-10-16 16:26:24.077175

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53e008946c54'
down_revision: Union[str, Sequence[str], None] = '273dbe6f0d5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
