"""Prevent available inventory from exceeding the total inventory.

Revision ID: 20260730_03
Revises: 20260730_02
Create Date: 2026-07-30
"""

from alembic import op


revision = "20260730_03"
down_revision = "20260730_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        "check_copies_available_not_greater_than_total",
        "books",
        "copies_available <= copies_total",
    )


def downgrade() -> None:
    op.drop_constraint(
        "check_copies_available_not_greater_than_total",
        "books",
        type_="check",
    )
