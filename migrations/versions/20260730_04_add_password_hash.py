"""Add securely hashed password storage for authenticated patrons.

Revision ID: 20260730_04
Revises: 20260730_03
Create Date: 2026-07-30
"""

from alembic import op
import sqlalchemy as sa


revision = "20260730_04"
down_revision = "20260730_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Nullable preserves existing, pre-auth patron records. Such users must
    # create/reset an account before they can sign in.
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "password_hash")
