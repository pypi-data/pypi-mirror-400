"""Add service_logs table.

Revision ID: 3da4dd5d0b75
Revises: 3d0994430da7
Create Date: 2025-06-13 14:22:24.633881

"""

import sqlalchemy_utils
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "3da4dd5d0b75"
down_revision = "3d0994430da7"
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade to 3da4dd5d0b75 revision."""
    op.create_table(
        "service_logs",
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("service_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "event_time",
            sa.DateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("log", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(
            ["service_id"],
            ["__reana.service.id_"],
            name=op.f("fk_service_logs_service_id_service"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_service_logs")),
        schema="__reana",
    )


def downgrade():
    """Downgrade to 3d0994430da7 revision."""
    op.drop_table("service_logs", schema="__reana")
