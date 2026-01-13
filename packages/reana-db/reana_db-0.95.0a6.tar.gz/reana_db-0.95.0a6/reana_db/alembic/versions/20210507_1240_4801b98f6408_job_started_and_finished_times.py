"""Job started and finished times.

Revision ID: 4801b98f6408
Revises: ad93dae04483
Create Date: 2021-05-07 12:40:54.207470

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4801b98f6408"
down_revision = "ad93dae04483"
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade to 4801b98f6408 revision."""
    op.add_column(
        "job", sa.Column("finished_at", sa.DateTime(), nullable=True), schema="__reana"
    )
    op.add_column(
        "job", sa.Column("started_at", sa.DateTime(), nullable=True), schema="__reana"
    )


def downgrade():
    """Downgrade to ad93dae04483 revision."""
    op.drop_column("job", "started_at", schema="__reana")
    op.drop_column("job", "finished_at", schema="__reana")
