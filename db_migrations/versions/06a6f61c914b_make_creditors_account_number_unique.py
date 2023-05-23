"""make creditors account number unique

Revision ID: 06a6f61c914b
Revises: 16ec12879c4e
Create Date: 2023-05-03 04:52:41.429545

"""
from app.utils.migrations import execute_raw_sql

# revision identifiers, used by Alembic.
revision = '06a6f61c914b'
down_revision = '16ec12879c4e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    execute_raw_sql(
        """
        ALTER TABLE creditors
        ADD CONSTRAINT account_number_key UNIQUE (account_number);
        """
    )


def downgrade() -> None:
    execute_raw_sql(
        """
        ALTER TABLE creditors DROP CONSTRAINT account_number_key;
        """
    )
