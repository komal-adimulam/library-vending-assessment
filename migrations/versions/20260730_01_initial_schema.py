"""Create the initial library lending schema.

Revision ID: 20260730_01
Revises:
Create Date: 2026-07-30
"""

from alembic import op
import sqlalchemy as sa


revision = "20260730_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.String(length=10), nullable=True),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_table(
        "books",
        sa.Column("book_id", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column("isbn", sa.String(length=20), nullable=True),
        sa.Column("copies_total", sa.Integer(), nullable=False),
        sa.Column("copies_available", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("copies_available >= 0", name="check_copies_available_non_negative"),
        sa.CheckConstraint("copies_total >= 0", name="check_copies_total_non_negative"),
        sa.PrimaryKeyConstraint("book_id"),
    )
    op.create_table(
        "loans",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=False),
        sa.Column("book_id", sa.String(length=100), nullable=False),
        sa.Column("idempotency_key", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("borrowed_at", sa.DateTime(), nullable=True),
        sa.Column("returned_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["book_id"], ["books.book_id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("loans")
    op.drop_table("books")
    op.drop_table("users")
