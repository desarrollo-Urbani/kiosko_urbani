"""initial schema

Revision ID: 20260402_0001
Revises:
Create Date: 2026-04-02 16:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260402_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "event_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "kiosk_sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("kiosk_device_id", sa.String(), nullable=True),
        sa.Column("session_key", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_key"),
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("commune", sa.String(), nullable=False),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("delivery_status", sa.String(), nullable=False),
        sa.Column("subsidy_available", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "leads",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("lead_status", sa.String(), nullable=False),
        sa.Column("priority", sa.String(), nullable=False),
        sa.Column("raw_data", sa.JSON(), nullable=False),
        sa.Column("executive_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["kiosk_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id"),
    )

    op.create_table(
        "queue_tickets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("ticket_number", sa.String(), nullable=False),
        sa.Column("customer_name", sa.String(), nullable=True),
        sa.Column("customer_phone", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("estimated_wait_minutes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["kiosk_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticket_number"),
    )

    op.create_table(
        "recommendation_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("engine_version", sa.String(), nullable=False),
        sa.Column("match_params", sa.JSON(), nullable=False),
        sa.Column("generated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["kiosk_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "session_answers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("question_key", sa.String(), nullable=False),
        sa.Column("answer_value", sa.JSON(), nullable=False),
        sa.Column("answer_label", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["kiosk_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "properties",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("property_type", sa.String(), nullable=False),
        sa.Column("bedrooms", sa.Integer(), nullable=False),
        sa.Column("bathrooms", sa.Integer(), nullable=False),
        sa.Column("area_total_m2", sa.Float(), nullable=False),
        sa.Column("price_uf", sa.Float(), nullable=False),
        sa.Column("dividend_est_clp", sa.Integer(), nullable=False),
        sa.Column("stock_status", sa.String(), nullable=False),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "queue_executive_assignments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticket_id", sa.Integer(), nullable=False),
        sa.Column("executive_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["ticket_id"], ["queue_tickets.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticket_id"),
    )
    op.create_index(
        "ix_queue_executive_assignments_executive_id",
        "queue_executive_assignments",
        ["executive_id"],
        unique=False,
    )

    op.create_table(
        "recommendation_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("property_id", sa.String(), nullable=False),
        sa.Column("match_score", sa.Integer(), nullable=False),
        sa.Column("match_tags", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"]),
        sa.ForeignKeyConstraint(["run_id"], ["recommendation_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("recommendation_items")
    op.drop_index("ix_queue_executive_assignments_executive_id", table_name="queue_executive_assignments")
    op.drop_table("queue_executive_assignments")
    op.drop_table("properties")
    op.drop_table("session_answers")
    op.drop_table("recommendation_runs")
    op.drop_table("queue_tickets")
    op.drop_table("leads")
    op.drop_table("projects")
    op.drop_table("kiosk_sessions")
    op.drop_table("event_logs")
