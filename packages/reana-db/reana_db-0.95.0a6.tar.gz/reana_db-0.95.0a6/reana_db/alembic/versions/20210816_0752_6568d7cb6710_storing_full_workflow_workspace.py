"""storing full workflow workspace.

Revision ID: 6568d7cb6710
Revises: f84e17bd6b18
Create Date: 2021-08-16 07:52:03.968797

"""

from sqlalchemy.sql import table, column
from sqlalchemy import String
from alembic import op
from reana_commons.config import SHARED_VOLUME_PATH
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision = "6568d7cb6710"
down_revision = "f84e17bd6b18"
branch_labels = None
depends_on = None


workflow = table(
    "workflow",
    column("workspace_path", String),
    column("owner_id", String),
    column("id_", String),
    schema="__reana",
)


def upgrade():
    """Upgrade to 6568d7cb6710 revision."""
    connection = op.get_bind()
    connection.execute(
        workflow.update()
        .where(sa.not_(workflow.c.workspace_path.like("/%")))
        .values(
            {"workspace_path": SHARED_VOLUME_PATH + os.sep + workflow.c.workspace_path}
        )
    )


def downgrade():
    """Downgrade to f84e17bd6b18 revision."""
    connection = op.get_bind()
    connection.execute(
        workflow.update().values(
            {
                "workspace_path": "users"
                + os.sep
                + workflow.c.owner_id
                + os.sep
                + "workflows"
                + os.sep
                + workflow.c.id_
            }
        )
    )
