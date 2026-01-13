"""Workflow launcher url.

Revision ID: d34f3905043c
Revises: 6568d7cb6710
Create Date: 2022-03-07 12:47:11.867026

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d34f3905043c"
down_revision = "6568d7cb6710"
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade to d34f3905043c revision."""
    op.add_column(
        "workflow",
        sa.Column("launcher_url", sa.String(), nullable=True),
        schema="__reana",
    )


def downgrade():
    """Downgrade to 6568d7cb6710 revision."""
    op.drop_column("workflow", "launcher_url", schema="__reana")
