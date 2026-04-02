"""auth users and sessions

Revision ID: 20260402_0002
Revises: 20260402_0001
Create Date: 2026-04-02 16:45:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260402_0002"
down_revision = "20260402_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_app_users_email", "app_users", ["email"], unique=False)

    op.create_table(
        "app_user_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["app_users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_index("ix_app_user_sessions_token", "app_user_sessions", ["token"], unique=False)
    op.create_index("ix_app_user_sessions_user_id", "app_user_sessions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_app_user_sessions_user_id", table_name="app_user_sessions")
    op.drop_index("ix_app_user_sessions_token", table_name="app_user_sessions")
    op.drop_table("app_user_sessions")
    op.drop_index("ix_app_users_email", table_name="app_users")
    op.drop_table("app_users")
