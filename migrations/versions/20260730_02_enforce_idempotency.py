"""Enforce unique idempotency keys for checkout requests.

Revision ID: 20260730_02
Revises: 20260730_01
Create Date: 2026-07-30
"""

from alembic import op
import sqlalchemy as sa


revision = "20260730_02"
down_revision = "20260730_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "loans",
        "idempotency_key",
        existing_type=sa.Text(),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.create_unique_constraint("uq_loans_idempotency_key", "loans", ["idempotency_key"])


def downgrade() -> None:
    op.drop_constraint("uq_loans_idempotency_key", "loans", type_="unique")
    op.alter_column(
        "loans",
        "idempotency_key",
        existing_type=sa.String(length=255),
        type_=sa.Text(),
        existing_nullable=True,
    )
