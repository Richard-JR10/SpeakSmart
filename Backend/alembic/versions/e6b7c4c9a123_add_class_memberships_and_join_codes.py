"""add class memberships and join codes

Revision ID: e6b7c4c9a123
Revises: 959d2ec5ea6a
Create Date: 2026-04-20 15:10:00.000000

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6b7c4c9a123'
down_revision: Union[str, Sequence[str], None] = '959d2ec5ea6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _generate_join_code(existing_codes: set[str]) -> str:
    while True:
        candidate = uuid.uuid4().hex[:6].upper()
        if candidate not in existing_codes:
            existing_codes.add(candidate)
            return candidate


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('classes', sa.Column('join_code', sa.String(), nullable=True))
    op.add_column('exercises', sa.Column('class_id', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_exercises_class_id_classes',
        'exercises',
        'classes',
        ['class_id'],
        ['class_id'],
    )

    op.create_table(
        'class_memberships',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('class_id', sa.String(), nullable=False),
        sa.Column('user_uid', sa.String(), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['class_id'], ['classes.class_id']),
        sa.ForeignKeyConstraint(['user_uid'], ['users.uid']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('class_id', 'user_uid', name='uq_class_memberships_class_user'),
    )

    bind = op.get_bind()

    class_rows = bind.execute(sa.text("SELECT class_id FROM classes")).fetchall()
    existing_codes: set[str] = set()
    for row in class_rows:
        bind.execute(
            sa.text("UPDATE classes SET join_code = :join_code WHERE class_id = :class_id"),
            {
                "join_code": _generate_join_code(existing_codes),
                "class_id": row.class_id,
            },
        )

    bind.execute(
        sa.text(
            """
            INSERT INTO class_memberships (class_id, user_uid)
            SELECT class_id, uid
            FROM users
            WHERE class_id IS NOT NULL
            """
        )
    )

    bind.execute(
        sa.text(
            """
            UPDATE exercises AS e
            SET class_id = u.class_id
            FROM users AS u
            WHERE e.instructor_uid = u.uid
              AND u.class_id IS NOT NULL
            """
        )
    )

    op.alter_column('classes', 'join_code', nullable=False)
    op.create_unique_constraint('uq_classes_join_code', 'classes', ['join_code'])
    op.drop_column('users', 'class_id')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('users', sa.Column('class_id', sa.String(), nullable=True))

    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            UPDATE users AS u
            SET class_id = membership.class_id
            FROM (
                SELECT DISTINCT ON (user_uid) user_uid, class_id
                FROM class_memberships
                ORDER BY user_uid, joined_at ASC
            ) AS membership
            WHERE u.uid = membership.user_uid
            """
        )
    )

    op.drop_constraint('uq_classes_join_code', 'classes', type_='unique')
    op.drop_table('class_memberships')
    op.drop_constraint('fk_exercises_class_id_classes', 'exercises', type_='foreignkey')
    op.drop_column('exercises', 'class_id')
    op.drop_column('classes', 'join_code')
