"""Quota tables.

Revision ID: c912d4f1e1cc
Revises:
Create Date: 2020-09-28 10:15:48.502050

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = "c912d4f1e1cc"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade to c912d4f1e1cc revision."""
    op.create_table(
        "resource",
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.Column("id_", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("name", sa.String(length=1024), unique=True, nullable=False),
        sa.Column(
            "type_", sa.Enum("cpu", "gpu", "disk", name="resourcetype"), nullable=False
        ),
        sa.Column(
            "unit",
            sa.Enum("bytes_", "milliseconds", name="resourceunit"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=1024), nullable=True),
        sa.PrimaryKeyConstraint("id_"),
        schema="__reana",
    )
    op.create_table(
        "user_resource",
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.Column("user_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "resource_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False
        ),
        sa.Column("quota_limit", sa.BigInteger(), nullable=True),
        sa.Column("quota_used", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["resource_id"],
            ["__reana.resource.id_"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["__reana.user_.id_"],
        ),
        sa.PrimaryKeyConstraint("user_id", "resource_id"),
        schema="__reana",
    )
    op.create_table(
        "workflow_resource",
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.Column(
            "workflow_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False
        ),
        sa.Column(
            "resource_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False
        ),
        sa.Column("quota_used", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["resource_id"],
            ["__reana.resource.id_"],
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["__reana.workflow.id_"],
        ),
        sa.PrimaryKeyConstraint("workflow_id", "resource_id"),
        schema="__reana",
    )


def downgrade():
    """Downgrade to previous revision (none in this case)."""
    op.drop_table("workflow_resource", schema="__reana")
    op.drop_table("user_resource", schema="__reana")
    op.drop_table("resource", schema="__reana")
