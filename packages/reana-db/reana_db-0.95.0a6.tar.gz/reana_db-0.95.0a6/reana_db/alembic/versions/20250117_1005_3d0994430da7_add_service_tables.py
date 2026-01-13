"""Add service tables.

Revision ID: 3d0994430da7
Revises: 2e82f33ee37d
Create Date: 2025-01-17 10:05:48.699316

"""

import sqlalchemy_utils
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "3d0994430da7"
down_revision = "2e82f33ee37d"
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade to 3d0994430da7 revision."""
    op.create_table(
        "service",
        sa.Column("id_", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("uri", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "created",
                "running",
                "finished",
                "failed",
                "deleted",
                "stopped",
                "queued",
                "pending",
                name="servicestatus",
            ),
            nullable=False,
        ),
        sa.Column("owner_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.Column("type_", sa.Enum("dask", name="servicetype"), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["__reana.user_.id_"], name=op.f("fk_service_owner_id_user_")
        ),
        sa.PrimaryKeyConstraint("id_", name=op.f("pk_service")),
        sa.UniqueConstraint("name", "uri", name=op.f("uq_service_name")),
        schema="__reana",
    )
    op.create_table(
        "workflow_service",
        sa.Column("workflow_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.Column("service_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(
            ["service_id"],
            ["__reana.service.id_"],
            name=op.f("fk_workflow_service_service_id_service"),
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["__reana.workflow.id_"],
            name=op.f("fk_workflow_service_workflow_id_workflow"),
        ),
        sa.PrimaryKeyConstraint("service_id", name=op.f("pk_workflow_service")),
        schema="__reana",
    )


def downgrade():
    """Downgrade to 2e82f33ee37d revision."""
    op.drop_table("workflow_service", schema="__reana")
    op.drop_table("service", schema="__reana")
    sa.Enum(name="servicestatus").drop(op.get_bind())
    sa.Enum(name="servicetype").drop(op.get_bind())
