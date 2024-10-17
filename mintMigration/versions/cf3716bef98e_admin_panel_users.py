"""admin panel users

Revision ID: cf3716bef98e
Revises: 99f468eb21eb
Create Date: 2024-10-16 18:35:55.848235

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cf3716bef98e"
down_revision: Union[str, None] = "99f468eb21eb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_panel_users",
        sa.Column("username", sa.String(16), primary_key=True),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column(
            "permissions", sa.BigInteger(), server_default=sa.text("0"), nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_column("admin_panel_users")
