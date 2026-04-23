"""add recognized text romaji fields

Revision ID: c1a2d3e4f5a6
Revises: 7b74e56695e6
Create Date: 2026-04-23 14:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c1a2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "7b74e56695e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("attempts", sa.Column("recognized_text_romaji", sa.String(), nullable=True))
    op.add_column(
        "exercise_submissions",
        sa.Column("recognized_text_romaji", sa.String(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("exercise_submissions", "recognized_text_romaji")
    op.drop_column("attempts", "recognized_text_romaji")
