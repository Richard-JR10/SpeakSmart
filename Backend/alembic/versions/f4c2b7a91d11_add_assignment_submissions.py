"""add assignment submissions

Revision ID: f4c2b7a91d11
Revises: e6b7c4c9a123
Create Date: 2026-04-20 23:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4c2b7a91d11'
down_revision: Union[str, Sequence[str], None] = 'e6b7c4c9a123'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'exercise_submissions',
        sa.Column('submission_id', sa.String(), nullable=False),
        sa.Column('exercise_id', sa.String(), nullable=False),
        sa.Column('student_uid', sa.String(), nullable=False),
        sa.Column('phrase_id', sa.String(), nullable=False),
        sa.Column('audio_file_url', sa.String(), nullable=False),
        sa.Column('suggested_accuracy_score', sa.Float(), nullable=False),
        sa.Column('suggested_mora_timing_score', sa.Float(), nullable=False),
        sa.Column('suggested_consonant_score', sa.Float(), nullable=False),
        sa.Column('suggested_vowel_score', sa.Float(), nullable=False),
        sa.Column('suggested_phoneme_error_map', sa.JSON(), nullable=True),
        sa.Column('suggested_feedback_text', sa.String(), nullable=True),
        sa.Column('teacher_accuracy_score', sa.Float(), nullable=True),
        sa.Column('teacher_feedback_text', sa.String(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('released_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.exercise_id']),
        sa.ForeignKeyConstraint(['student_uid'], ['users.uid']),
        sa.ForeignKeyConstraint(['phrase_id'], ['phrases.phrase_id']),
        sa.PrimaryKeyConstraint('submission_id'),
        sa.UniqueConstraint('exercise_id', 'student_uid', 'phrase_id', name='uq_exercise_submission_phrase_student'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('exercise_submissions')
