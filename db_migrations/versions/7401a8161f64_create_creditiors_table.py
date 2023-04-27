"""Create creditiors table

Revision ID: 7401a8161f64
Revises: e76f18c79bfa
Create Date: 2023-04-13 05:56:51.585159

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import func


# revision identifiers, used by Alembic.
revision = "7401a8161f64"
down_revision = "e76f18c79bfa"
branch_labels = None
depends_on = None

table = "creditors"


def upgrade() -> None:
    op.create_table(
        table,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.String(300)),
        sa.Column("street_address", sa.String),
        sa.Column("city", sa.String(40), nullable=False),
        sa.Column("state", sa.String(40), nullable=False),
        sa.Column("country", sa.String(40), server_default="Nigeria"),
        sa.Column("phone", sa.String(25), nullable=False, unique=True),
        sa.Column("email", sa.String(70), unique=True),
        sa.Column("bank_name", sa.String(100)),
        sa.Column("account_number", sa.String),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )
    op.create_check_constraint(
        constraint_name="creditors_account_number_bank_ck",
        table_name=table,
        condition="account_number IS NULL OR bank_name IS NOT NULL",
    ),
    op.create_unique_constraint(
        constraint_name="creditors_phone_account_number_key",
        table_name=table,
        columns=["account_number", "phone"],
    ),


# Dropping the table drops all the constraints
def downgrade() -> None:
    op.drop_table(table)
