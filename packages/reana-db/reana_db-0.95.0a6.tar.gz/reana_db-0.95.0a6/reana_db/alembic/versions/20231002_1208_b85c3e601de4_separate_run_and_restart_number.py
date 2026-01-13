"""Separate run number into major and minor run numbers.

Revision ID: b85c3e601de4
Revises: 377cfbfccf75
Create Date: 2023-10-02 12:08:18.292490

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b85c3e601de4"
down_revision = "377cfbfccf75"
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade to b85c3e601de4 revision."""
    # Add new columns (run_number_major, run_number_minor)
    op.add_column(
        "workflow", sa.Column("run_number_major", sa.Integer()), schema="__reana"
    )
    op.add_column(
        "workflow",
        sa.Column("run_number_minor", sa.Integer(), default=0),
        schema="__reana",
    )

    # Data migration (split run_number into run_number_major and run_number_minor)
    op.get_bind().execute(
        sa.text(
            "UPDATE __reana.workflow"
            " SET run_number_major = FLOOR(run_number), "
            " run_number_minor = (run_number - FLOOR(run_number)) * 10"
        ),
    )

    # Delete old constraint
    op.drop_constraint("_user_workflow_run_uc", "workflow", schema="__reana")

    # Drop old run_number column
    op.drop_column("workflow", "run_number", schema="__reana")

    # Add new constraint (the primary key is not run_number anymore, but with major and minor run number
    op.create_unique_constraint(
        "_user_workflow_run_uc",
        "workflow",
        ["name", "owner_id", "run_number_major", "run_number_minor"],
        schema="__reana",
    )

    # Update run_number_minor for workflows that have been restarted more than 10 times
    # (thus erroneously having the following run_number_major), in case some of them
    # were created before the limit on 9 restarts was introduced.
    op.get_bind().execute(
        sa.text(
            """
            UPDATE __reana.workflow AS w
            SET
                run_number_major = to_be_updated.new_major_run_number,
                run_number_minor = (w.run_number_minor + (w.run_number_major - to_be_updated.new_major_run_number) * 10)
            FROM (
                SELECT MIN(w1.run_number_major) - 1 AS new_major_run_number, w1.workspace_path
                FROM __reana.workflow w1
                WHERE w1.restart AND w1.run_number_minor = 0
                GROUP BY w1.workspace_path
            ) AS to_be_updated
            WHERE w.workspace_path = to_be_updated.workspace_path
            """
        ),
    )


def downgrade():
    """Downgrade to 377cfbfccf75 revision."""
    # Revert constraint
    op.drop_constraint("_user_workflow_run_uc", "workflow", schema="__reana")

    # Add old run_number column back
    op.add_column("workflow", sa.Column("run_number", sa.Float()), schema="__reana")

    # Check that there are no workflows discarded more than 10 times
    # This is because of the way the info about restarts is stored in
    # the run_number column (see https://github.com/reanahub/reana-db/issues/186)
    restarted_ten_times = (
        op.get_bind()
        .execute("SELECT COUNT(*) FROM __reana.workflow WHERE run_number_minor >= 10")
        .fetchone()[0]
    )
    if restarted_ten_times != 0:
        raise ValueError(
            "Cannot migrate database because some workflows have been restarted 10 or more times,"
            " and the previous database revision only supports up to 9 restarts."
            " If you want to downgrade, you should manually delete them."
        )

    # Data migration (combine run_number_major and restart_number back to run_number)
    op.get_bind().execute(
        "UPDATE __reana.workflow SET run_number=run_number_major+(run_number_minor * 1.0 /10)"
    )

    # Drop new columns
    op.drop_column("workflow", "run_number_major", schema="__reana")
    op.drop_column("workflow", "run_number_minor", schema="__reana")

    # Restore old constraint
    op.create_unique_constraint(
        "_user_workflow_run_uc",
        "workflow",
        ["name", "owner_id", "run_number"],
        schema="__reana",
    )
