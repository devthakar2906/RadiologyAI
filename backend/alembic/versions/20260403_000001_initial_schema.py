"""initial schema

Revision ID: 20260403_000001
Revises:
Create Date: 2026-04-03 18:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect


revision: str = "20260403_000001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "users" not in existing_tables:
        op.create_table(
            "users",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("password", sa.String(length=255), nullable=False),
            sa.Column("role", sa.String(length=50), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    user_indexes = {index["name"] for index in inspector.get_indexes("users")} if "users" in inspector.get_table_names() else set()
    if op.f("ix_users_email") not in user_indexes:
        op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    if "logs" not in existing_tables:
        op.create_table(
            "logs",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("action", sa.String(length=255), nullable=False),
            sa.Column("status", sa.Text(), nullable=False),
            sa.Column("timestamp", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if "reports" not in existing_tables:
        op.create_table(
            "reports",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("transcription", sa.Text(), nullable=False),
            sa.Column("report", sa.Text(), nullable=False),
            sa.Column("audio_hash", sa.String(length=64), nullable=False),
            sa.Column("audio_path", sa.String(length=500), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    report_indexes = {index["name"] for index in inspector.get_indexes("reports")} if "reports" in inspector.get_table_names() else set()
    if op.f("ix_reports_audio_hash") not in report_indexes:
        op.create_index(op.f("ix_reports_audio_hash"), "reports", ["audio_hash"], unique=False)
    if op.f("ix_reports_user_id") not in report_indexes:
        op.create_index(op.f("ix_reports_user_id"), "reports", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reports_user_id"), table_name="reports")
    op.drop_index(op.f("ix_reports_audio_hash"), table_name="reports")
    op.drop_table("reports")
    op.drop_table("logs")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
