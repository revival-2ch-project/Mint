"""bbs head.txt

Revision ID: d99f34f112b1
Revises: d4b120debf5d
Create Date: 2024-10-16 17:20:04.713758

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d99f34f112b1"
down_revision: Union[str, None] = "d4b120debf5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    head = """
<div style="text-align: center; margin: 1.2em 0">
    <span style="color: red">クリックで救える命が…ないです(｀･ω･´)ｼｬｷｰﾝ</font>
</div>

<b>掲示板使用上の注意</b>
<ul style="font-weight:bold;">
    <li>･転んでも泣かない</li>
    <li>･出されたものは残さず食べる</li>
    <li>･Python使いを尊重する</li>
</ul>
    """
    op.add_column(
        "boards",
        sa.Column("head", sa.String(), server_default=sa.text(head), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("boards", "head")
