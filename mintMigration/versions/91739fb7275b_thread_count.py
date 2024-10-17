"""thread count

Revision ID: 91739fb7275b
Revises: da355455d83b
Create Date: 2024-10-17 17:38:38.179967

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "91739fb7275b"
down_revision: Union[str, None] = "da355455d83b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "threads",
        sa.Column("count", sa.Integer, server_default=sa.text("1"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("threads", "count")
