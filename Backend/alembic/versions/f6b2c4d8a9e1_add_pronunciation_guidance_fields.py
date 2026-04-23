"""add pronunciation guidance fields

Revision ID: f6b2c4d8a9e1
Revises: c1a2d3e4f5a6
Create Date: 2026-04-23 18:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f6b2c4d8a9e1"
down_revision: Union[str, Sequence[str], None] = "c1a2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("phrases", sa.Column("pronunciation_reading_override", sa.String(), nullable=True))
    op.add_column("phrases", sa.Column("pronunciation_chunk_override", sa.JSON(), nullable=True))
    op.add_column("phrases", sa.Column("pronunciation_rule_override", sa.JSON(), nullable=True))

    op.add_column("attempts", sa.Column("target_pronunciation", sa.JSON(), nullable=True))
    op.add_column("attempts", sa.Column("pronunciation_feedback", sa.JSON(), nullable=True))

    op.add_column("exercise_submissions", sa.Column("target_pronunciation", sa.JSON(), nullable=True))
    op.add_column("exercise_submissions", sa.Column("pronunciation_feedback", sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("exercise_submissions", "pronunciation_feedback")
    op.drop_column("exercise_submissions", "target_pronunciation")
    op.drop_column("attempts", "pronunciation_feedback")
    op.drop_column("attempts", "target_pronunciation")
    op.drop_column("phrases", "pronunciation_rule_override")
    op.drop_column("phrases", "pronunciation_chunk_override")
    op.drop_column("phrases", "pronunciation_reading_override")
