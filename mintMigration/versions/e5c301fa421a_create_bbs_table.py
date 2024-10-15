"""create bbs table

Revision ID: e5c301fa421a
Revises: 
Create Date: 2024-10-15 19:56:55.028162

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e5c301fa421a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bbs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("anonymous_name", sa.String(), default="名無しさん", nullable=False),
        sa.Column("deleted_name", sa.String(), default="あぼーん", nullable=False),
        sa.Column("subject_count", sa.Integer, default=64, nullable=False),
        sa.Column("name_count", sa.Integer, default=50, nullable=False),
        sa.Column("message_count", sa.Integer, default=2000, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("bbs")
