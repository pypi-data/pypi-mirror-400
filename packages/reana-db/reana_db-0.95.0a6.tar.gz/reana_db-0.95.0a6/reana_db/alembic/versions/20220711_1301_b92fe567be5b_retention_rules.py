"""Retention rules.

Revision ID: b92fe567be5b
Revises: d34f3905043c
Create Date: 2022-07-11 13:01:19.179610

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = "b92fe567be5b"
down_revision = "d34f3905043c"
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade to b92fe567be5b revision."""
    op.create_table(
        "workspace_retention_rule",
        sa.Column("id_", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "workflow_id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            nullable=False,
        ),
        sa.Column("workspace_files", sa.String(length=255), nullable=False),
        sa.Column("retention_days", sa.Integer(), nullable=False),
        sa.Column("apply_on", sa.DateTime(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "created",
                "active",
                "inactive",
                "applied",
                name="workspaceretentionrulestatus",
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["__reana.workflow.id_"],
        ),
        sa.PrimaryKeyConstraint("id_"),
        sa.UniqueConstraint(
            "workflow_id", "workspace_files", name="_workspace_retention_rule_uc"
        ),
        schema="__reana",
    )
    op.create_table(
        "workspace_retention_audit_log",
        sa.Column(
            "workspace_retention_rule_id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            nullable=False,
        ),
        sa.Column(
            "timestamp", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "action",
            sa.Enum(
                "created",
                "active",
                "inactive",
                "applied",
                name="workspaceretentionrulestatus",
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["workspace_retention_rule_id"],
            ["__reana.workspace_retention_rule.id_"],
        ),
        sa.PrimaryKeyConstraint("workspace_retention_rule_id", "timestamp", "action"),
        schema="__reana",
    )


def downgrade():
    """Downgrade to d34f3905043c revision."""
    op.drop_table("workspace_retention_audit_log", schema="__reana")
    op.drop_table("workspace_retention_rule", schema="__reana")
    sa.Enum(name="workspaceretentionrulestatus").drop(op.get_bind())
