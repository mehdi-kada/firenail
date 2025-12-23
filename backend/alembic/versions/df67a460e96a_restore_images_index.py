"""restore_images_index

Revision ID: df67a460e96a
Revises: e86043bfcf82
Create Date: 2025-05-18 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df67a460e96a'
down_revision: Union[str, Sequence[str], None] = 'e86043bfcf82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_images_profile_created', 'images', ['profile_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_images_profile_created', table_name='images')
