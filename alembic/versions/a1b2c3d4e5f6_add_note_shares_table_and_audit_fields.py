"""add note_shares table and audit fields to notes

Revision ID: a1b2c3d4e5f6
Revises: f8d054c48d61
Create Date: 2026-04-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f8d054c48d61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar campos de auditoría y soft delete a notes
    op.add_column('notes', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('notes', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))

    # Crear tabla note_shares
    op.create_table(
        'note_shares',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('note_id', sa.UUID(), nullable=False),
        sa.Column('shared_with', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['shared_with'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('note_id', 'shared_with', name='uq_note_shares_note_user'),
    )


def downgrade() -> None:
    op.drop_table('note_shares')
    op.drop_column('notes', 'updated_at')
    op.drop_column('notes', 'deleted_at')
