"""add attempt verification fields

Revision ID: 7b74e56695e6
Revises: f4c2b7a91d11
Create Date: 2026-04-22 18:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7b74e56695e6"
down_revision: Union[str, Sequence[str], None] = "f4c2b7a91d11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "attempts",
        sa.Column("verification_status", sa.String(), nullable=False, server_default="accepted"),
    )
    op.add_column("attempts", sa.Column("recognized_phrase_id", sa.String(), nullable=True))
    op.add_column("attempts", sa.Column("recognized_text", sa.String(), nullable=True))
    op.add_column("attempts", sa.Column("verification_confidence", sa.Float(), nullable=True))
    op.add_column("attempts", sa.Column("verification_margin", sa.Float(), nullable=True))
    op.add_column(
        "attempts",
        sa.Column("counts_for_progress", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.add_column(
        "exercise_submissions",
        sa.Column("verification_status", sa.String(), nullable=False, server_default="accepted"),
    )
    op.add_column("exercise_submissions", sa.Column("recognized_phrase_id", sa.String(), nullable=True))
    op.add_column("exercise_submissions", sa.Column("recognized_text", sa.String(), nullable=True))
    op.add_column("exercise_submissions", sa.Column("verification_confidence", sa.Float(), nullable=True))
    op.add_column("exercise_submissions", sa.Column("verification_margin", sa.Float(), nullable=True))
    op.add_column(
        "exercise_submissions",
        sa.Column("counts_for_progress", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.alter_column("attempts", "verification_status", server_default=None)
    op.alter_column("attempts", "counts_for_progress", server_default=None)
    op.alter_column("exercise_submissions", "verification_status", server_default=None)
    op.alter_column("exercise_submissions", "counts_for_progress", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("exercise_submissions", "counts_for_progress")
    op.drop_column("exercise_submissions", "verification_margin")
    op.drop_column("exercise_submissions", "verification_confidence")
    op.drop_column("exercise_submissions", "recognized_text")
    op.drop_column("exercise_submissions", "recognized_phrase_id")
    op.drop_column("exercise_submissions", "verification_status")

    op.drop_column("attempts", "counts_for_progress")
    op.drop_column("attempts", "verification_margin")
    op.drop_column("attempts", "verification_confidence")
    op.drop_column("attempts", "recognized_text")
    op.drop_column("attempts", "recognized_phrase_id")
    op.drop_column("attempts", "verification_status")
