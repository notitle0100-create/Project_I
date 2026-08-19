"""add image generations

Revision ID: 0005_image_generations
Revises: 0004_outfit_recipes
Create Date: 2026-08-19

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005_image_generations"
down_revision: str | Sequence[str] | None = "0004_outfit_recipes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "image_generations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
        sa.Column("recipe_target_date", sa.Date(), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("composition", sa.String(length=32), nullable=False),
        sa.Column("scene", sa.String(length=160), nullable=False),
        sa.Column("generation_size", sa.String(length=16), nullable=False),
        sa.Column("final_width", sa.Integer(), nullable=True),
        sa.Column("final_height", sa.Integer(), nullable=True),
        sa.Column("file_path", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("target_date"),
    )


def downgrade() -> None:
    op.drop_table("image_generations")
