"""add created_by to creditors

Revision ID: 78539786a02e
Revises: 06a6f61c914b
Create Date: 2023-05-23 20:05:59.894613

"""
from app.utils.migrations import execute_raw_sql


# revision identifiers, used by Alembic.
revision = '78539786a02e'
down_revision = '06a6f61c914b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    execute_raw_sql(
        """
        ALTER TABLE creditors
        ADD COLUMN owner_id INTEGER NOT NULL
        REFERENCES users(id) ON DELETE CASCADE;
        """
    )


def downgrade() -> None:
    execute_raw_sql(
        """
        ALTER TABLE creditors DROP COLUMN owner_id;
        """
    )
