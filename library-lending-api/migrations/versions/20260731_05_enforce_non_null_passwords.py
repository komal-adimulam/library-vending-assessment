"""Enforce non-null passwords and set default timestamps.

Revision ID: 20260731_05
Revises: 20260730_04
Create Date: 2026-07-31
"""

from alembic import op
import sqlalchemy as sa


revision = "20260731_05"
down_revision = "20260730_04"
branch_labels = None
depends_on = None

# Hash of "correct-horse-battery-staple"
DEFAULT_HASH = "scrypt$16384$8$1$DuFQIx6iWk4nnxVEr2kJ7g$K5X-dDvqdxW-JWm6MW8H5QD4JS77qcJLrRFLYlIPNc_Y5bAvgsH1kFRCWszMUn1_sFp8WfrzBHpFnin_JKGhrg"


def upgrade() -> None:
    # 1. Update any existing users with NULL password_hash to the default hash
    op.execute(f"UPDATE users SET password_hash = '{DEFAULT_HASH}' WHERE password_hash IS NULL")
    
    # 2. Make password_hash column NOT NULL
    op.alter_column("users", "password_hash", nullable=False)
    
    # 3. Update any existing users or books with NULL created_at to current time
    op.execute("UPDATE users SET created_at = NOW() WHERE created_at IS NULL")
    op.execute("UPDATE books SET created_at = NOW() WHERE created_at IS NULL")
    
    # 4. Enforce server-side default value for created_at
    op.alter_column("users", "created_at", server_default=sa.func.now())
    op.alter_column("books", "created_at", server_default=sa.func.now())


def downgrade() -> None:
    # 1. Remove server-side default value for created_at
    op.alter_column("users", "created_at", server_default=None)
    op.alter_column("books", "created_at", server_default=None)
    
    # 2. Make password_hash column nullable again
    op.alter_column("users", "password_hash", nullable=True)
