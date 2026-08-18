"""add weather snapshots

Revision ID: 0002_weather_snapshots
Revises: 0001_baseline
Create Date: 2026-08-19

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_weather_snapshots"
down_revision: str | Sequence[str] | None = "0001_baseline"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "weather_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("weather_condition", sa.String(length=32), nullable=False),
        sa.Column("high_temperature_c", sa.Float(), nullable=False),
        sa.Column("low_temperature_c", sa.Float(), nullable=False),
        sa.Column("precipitation_probability", sa.Float(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("target_date"),
    )


def downgrade() -> None:
    op.drop_table("weather_snapshots")
