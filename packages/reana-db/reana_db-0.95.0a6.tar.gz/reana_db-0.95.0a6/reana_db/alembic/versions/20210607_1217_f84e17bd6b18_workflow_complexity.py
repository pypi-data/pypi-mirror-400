"""Workflow complexity.

Revision ID: f84e17bd6b18
Revises: 4801b98f6408
Create Date: 2021-06-07 12:17:47.218408

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f84e17bd6b18"
down_revision = "4801b98f6408"
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade to f84e17bd6b18 revision."""
    op.add_column(
        "workflow",
        sa.Column(
            "complexity",
            postgresql.ARRAY(sa.BigInteger(), dimensions=2),
            nullable=True,
            server_default="{}",
        ),
        schema="__reana",
    )


def downgrade():
    """Downgrade to 4801b98f6408 revision."""
    op.drop_column("workflow", "complexity", schema="__reana")
