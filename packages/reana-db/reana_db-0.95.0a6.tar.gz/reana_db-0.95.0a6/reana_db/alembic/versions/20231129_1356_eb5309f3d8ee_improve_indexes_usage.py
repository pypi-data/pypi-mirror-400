"""Improve indexes usage.

Revision ID: eb5309f3d8ee
Revises: 2461610e9698
Create Date: 2023-11-29 13:56:23.588587

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "eb5309f3d8ee"
down_revision = "2461610e9698"
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade to eb5309f3d8ee."""
    # Drop old unique constraint for __reana.workflow and
    # create new one with better column order
    op.drop_constraint("uq_workflow_name", "workflow", schema="__reana", type_="unique")
    op.create_unique_constraint(
        "uq_workflow_owner_id",
        "workflow",
        ["owner_id", "name", "run_number_major", "run_number_minor"],
        schema="__reana",
    )

    # Create new index on (workflow_uuid, created) of __reana.job
    op.create_index(
        "ix___reana_job_workflow_uuid",
        "job",
        ["workflow_uuid", "created"],
        unique=False,
        schema="__reana",
    )

    # Create new index on (status) of __reana.workflow
    op.create_index(
        op.f("ix___reana_workflow_status"),
        "workflow",
        ["status"],
        unique=False,
        schema="__reana",
    )


def downgrade():
    """Downgrade to 2461610e9698."""
    # Drop new index on __reana.workflow
    op.drop_index(
        op.f("ix___reana_workflow_status"), table_name="workflow", schema="__reana"
    )

    # Delete new index on __reana.job
    op.drop_index("ix___reana_job_workflow_uuid", table_name="job", schema="__reana")

    # Drop new unique constraint for __reana.workflow and create previous one
    op.drop_constraint(
        "uq_workflow_owner_id", "workflow", schema="__reana", type_="unique"
    )
    op.create_unique_constraint(
        "uq_workflow_name",
        "workflow",
        ["name", "owner_id", "run_number_major", "run_number_minor"],
        schema="__reana",
    )
