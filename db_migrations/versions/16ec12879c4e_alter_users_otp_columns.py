"""alter users otp columns

Revision ID: 16ec12879c4e
Revises: 7e1f6e90055c
Create Date: 2023-04-21 19:50:41.565910

"""

from app.utils.migrations import execute_raw_sql


# revision identifiers, used by Alembic.
revision = "16ec12879c4e"
down_revision = "7e1f6e90055c"
branch_labels = None
depends_on = None


# Just more comfortable using sql for this version
def upgrade() -> None:
    execute_raw_sql(
        """
            ALTER TABLE users RENAME COLUMN mobile_otp To otp;
            ALTER TABLE users RENAME COLUMN mobile_otp_expires_at to otp_expires_at;
        """
    )


def downgrade() -> None:
    execute_raw_sql(
        """
            ALTER TABLE users RENAME COLUMN otp TO mobile_otp;
            ALTER TABLE users RENAME COLUMN otp_expires_at TO mobile_otp_expires_at;
        """
    )
