"""Interactive sessions.

Revision ID: ad93dae04483
Revises: c912d4f1e1cc
Create Date: 2020-10-09 16:12:00.090837

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

# revision identifiers, used by Alembic.
revision = "ad93dae04483"
down_revision = "c912d4f1e1cc"
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade to ad93dae04483 revision."""
    op.create_table(
        "interactive_session",
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.Column("id_", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("path", sa.Text(), nullable=True),
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
                name="runstatus",
            ),
            nullable=False,
        ),
        sa.Column("owner_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.Column(
            "type_", sa.Enum("jupyter", name="interactivesessiontype"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["__reana.user_.id_"],
        ),
        sa.PrimaryKeyConstraint("id_"),
        sa.UniqueConstraint("id_"),
        sa.UniqueConstraint("name", "path", name="_interactive_session_uc"),
        schema="__reana",
    )
    op.create_table(
        "interactive_session_resource",
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.Column("session_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "resource_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False
        ),
        sa.Column("quota_used", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["resource_id"],
            ["__reana.resource.id_"],
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["__reana.interactive_session.id_"],
        ),
        sa.PrimaryKeyConstraint("session_id", "resource_id"),
        schema="__reana",
    )
    op.create_table(
        "workflow_session",
        sa.Column("workflow_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.Column("session_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["__reana.interactive_session.id_"],
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["__reana.workflow.id_"],
        ),
        sa.PrimaryKeyConstraint("session_id"),
        schema="__reana",
    )
    op.drop_column("workflow", "interactive_session_name", schema="__reana")
    op.drop_column("workflow", "interactive_session_type", schema="__reana")
    op.drop_column("workflow", "interactive_session", schema="__reana")

    # Change `Workflow.status` type from `workflowstatus` to `runstatus`.
    op.execute(
        "ALTER TABLE __reana.workflow ALTER COLUMN status TYPE runstatus USING status::text::runstatus;"
    )
    # Remove old `workflowstatus` data type.
    op.execute("DROP TYPE IF EXISTS workflowstatus;")


def downgrade():
    """Downgrade to c912d4f1e1cc revision."""
    op.add_column(
        "workflow",
        sa.Column("interactive_session", sa.TEXT(), autoincrement=False, nullable=True),
        schema="__reana",
    )
    op.add_column(
        "workflow",
        sa.Column(
            "interactive_session_type", sa.TEXT(), autoincrement=False, nullable=True
        ),
        schema="__reana",
    )
    op.add_column(
        "workflow",
        sa.Column(
            "interactive_session_name", sa.TEXT(), autoincrement=False, nullable=True
        ),
        schema="__reana",
    )
    op.drop_table("workflow_session", schema="__reana")
    op.drop_table("interactive_session_resource", schema="__reana")
    op.drop_table("interactive_session", schema="__reana")

    # Create `workflowstatus` type without `pending` value.
    op.execute(
        "CREATE TYPE workflowstatus AS ENUM ('created', 'running', 'finished', 'failed', 'deleted', 'stopped', 'queued');"
    )
    # Change `Workflow.status` type from `runstatus` to `workflowstatus`.
    op.execute(
        "ALTER TABLE __reana.workflow ALTER COLUMN status TYPE workflowstatus USING status::text::workflowstatus;"
    )
    # Remove `runstatus` and `interactivesessiontype` data types.
    op.execute("DROP TYPE IF EXISTS runstatus;")
    op.execute("DROP TYPE IF EXISTS interactivesessiontype;")
