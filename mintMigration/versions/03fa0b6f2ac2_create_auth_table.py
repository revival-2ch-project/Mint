"""create auth table

Revision ID: 03fa0b6f2ac2
Revises: e5c301fa421a
Create Date: 2024-10-15 20:04:55.481581

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "03fa0b6f2ac2"
down_revision: Union[str, None] = "e5c301fa421a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "auth",
        sa.Column("id", sa.String(length=10), primary_key=True),
        sa.Column("account_id", sa.String(), unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("auth")
