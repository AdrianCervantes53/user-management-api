"""remove role column from users table

Revision ID: b7e9f2a1c348
Revises: a1b2c3d4e5f6
Create Date: 2026-04-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e9f2a1c348'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Role is contextual (per note via NoteShare.role), not a global user attribute.
    op.drop_column('users', 'role')


def downgrade() -> None:
    op.add_column('users', sa.Column('role', sa.String(length=20), nullable=True, server_default='user'))
