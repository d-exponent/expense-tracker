"""make users phone column unique

Revision ID: 48e39b34142e
Revises: 78539786a02e
Create Date: 2023-05-23 22:14:31.409293

"""
from app.utils.migrations import execute_raw_sql


# revision identifiers, used by Alembic.
revision = '48e39b34142e'
down_revision = '78539786a02e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    execute_raw_sql("ALTER TABLE users ADD CONSTRAINT users_phone_key UNIQUE(phone);")


def downgrade() -> None:
    execute_raw_sql("ALTER TABLE users DROP CONSTRAINT users_phone_key;")
