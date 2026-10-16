"""create tasks table

Revision ID: 0001_create_tasks
Revises:
Create Date: 2026-01-15
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_create_tasks"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="TODO"),
        sa.Column("assignee", sa.String(length=120), nullable=False, server_default="Unassigned"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )
    op.create_index("ix_tasks_status", "tasks", ["status"])


def downgrade():
    op.drop_index("ix_tasks_status", table_name="tasks")
    op.drop_table("tasks")
