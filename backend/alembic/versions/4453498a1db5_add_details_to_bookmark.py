"""add details to bookmark

Revision ID: 4453498a1db5
Revises: cd9eff15037f
Create Date: 2026-08-18 22:22:20.742412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4453498a1db5'
down_revision: Union[str, Sequence[str], None] = 'cd9eff15037f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('bookmark', sa.Column('details', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('bookmark', 'details')
