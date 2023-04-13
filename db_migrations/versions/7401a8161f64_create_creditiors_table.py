"""Create creditiors table

Revision ID: 7401a8161f64
Revises: e76f18c79bfa
Create Date: 2023-04-13 05:56:51.585159

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7401a8161f64"
down_revision = "e76f18c79bfa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    op.drop_table(table_name="creditors")
