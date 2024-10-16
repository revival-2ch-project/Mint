"""admin panel sessions

Revision ID: da355455d83b
Revises: cf3716bef98e
Create Date: 2024-10-16 18:52:24.410519

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "da355455d83b"
down_revision: Union[str, None] = "cf3716bef98e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_panel_sessions",
        sa.Column("id", sa.String(10), primary_key=True),
        sa.Column("username", sa.String(16), nullable=False),
        sa.Column("expire_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("admin_panel_sessions")
