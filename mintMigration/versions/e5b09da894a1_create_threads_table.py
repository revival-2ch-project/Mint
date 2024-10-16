"""create threads table

Revision ID: e5b09da894a1
Revises: 03fa0b6f2ac2
Create Date: 2024-10-15 20:07:29.583600

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e5b09da894a1"
down_revision: Union[str, None] = "03fa0b6f2ac2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "threads",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("bbs", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("account_id", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("content", sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("threads")
