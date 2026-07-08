"""add roles api keys and request logs

Revision ID: a1b2c3d4e5f6
Revises: 64ebcd270c0f
Create Date: 2026-07-07 15:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "64ebcd270c0f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("admin_user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("role", sa.String(length=16), nullable=False, server_default="user")
        )
        batch_op.add_column(sa.Column("ai_provider", sa.String(length=16), nullable=True))
        batch_op.add_column(sa.Column("api_key_encrypted", sa.Text(), nullable=True))

    op.execute("UPDATE admin_user SET role = 'admin' WHERE username = 'admin'")

    op.create_table(
        "api_request_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("method", sa.String(length=16), nullable=False),
        sa.Column("path", sa.String(length=512), nullable=False),
        sa.Column("query_string", sa.String(length=1024), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("response_body", sa.Text(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("client_ip", sa.String(length=64), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("is_authenticated", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("api_request_log", schema=None) as batch_op:
        batch_op.create_index("idx_api_log_created", ["created_at"], unique=False)
        batch_op.create_index("idx_api_log_user_id", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("api_request_log")
    with op.batch_alter_table("admin_user", schema=None) as batch_op:
        batch_op.drop_column("api_key_encrypted")
        batch_op.drop_column("ai_provider")
        batch_op.drop_column("role")
