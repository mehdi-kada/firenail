"""Add index on images profile_id and created_at

Revision ID: 20251202_add_idx
Revises: e86043bfcf82
Create Date: 2025-12-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20251202_add_idx'
down_revision: Union[str, Sequence[str], None] = 'e86043bfcf82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index('ix_images_profile_created', 'images', ['profile_id', 'created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_images_profile_created', table_name='images')
