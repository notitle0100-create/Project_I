"""add outfit recipes

Revision ID: 0004_outfit_recipes
Revises: 0003_style_selections
Create Date: 2026-08-19

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004_outfit_recipes"
down_revision: str | Sequence[str] | None = "0003_style_selections"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "outfit_recipes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("recipe", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("target_date"),
    )


def downgrade() -> None:
    op.drop_table("outfit_recipes")
