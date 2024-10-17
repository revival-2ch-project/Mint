"""server config

Revision ID: 99f468eb21eb
Revises: d99f34f112b1
Create Date: 2024-10-16 17:29:35.785730

"""

import enum
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "99f468eb21eb"
down_revision: Union[str, None] = "d99f34f112b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class CaptchaType(enum.Enum):
    NONE = "NONE"
    RECAPTCHA = "RECAPTCHA"
    HCAPTCHA = "HCAPTCHA"
    MCAPTCHA = "MCAPTCHA"
    TURNSTILE = "TURNSTILE"


def upgrade() -> None:
    op.create_table(
        "meta",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "captcha_type",
            sa.Enum(CaptchaType),
            server_default=sa.text("NONE"),
            nullable=False,
        ),
        sa.Column("captcha_sitekey", sa.String(), nullable=True),
        sa.Column("captcha_secret", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("meta")
