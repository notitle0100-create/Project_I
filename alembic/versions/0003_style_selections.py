"""add style selections

Revision ID: 0003_style_selections
Revises: 0002_weather_snapshots
Create Date: 2026-08-19

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_style_selections"
down_revision: str | Sequence[str] | None = "0002_weather_snapshots"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "style_selections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("style", sa.String(length=32), nullable=False),
        sa.Column("occasion", sa.String(length=32), nullable=False),
        sa.Column("mood", sa.String(length=32), nullable=False),
        sa.Column("selected_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("target_date"),
    )


def downgrade() -> None:
    op.drop_table("style_selections")
