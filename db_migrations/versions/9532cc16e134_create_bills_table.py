"""create bills table

Revision ID: 9532cc16e134
Revises: 7401a8161f64
Create Date: 2023-04-13 06:22:50.194556

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text, func


# revision identifiers, used by Alembic.
revision = "9532cc16e134"
down_revision = "7401a8161f64"
branch_labels = None
depends_on = None
table = "bills"


def upgrade() -> None:
    op.create_table(
        table,
        sa.Column("my_id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.my_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "creditor_id",
            sa.Integer,
            sa.ForeignKey("creditors.my_id", ondelete="SET NULL"),
            nullable=False,
        ),
        sa.Column("total_credit_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("total_paid_amount", sa.Numeric(10, 2), server_default=text("0.00")),
        sa.Column(
            "current_balance",
            sa.Numeric(10, 2),
            sa.Computed("total_paid_amount - total_credit_amount"),
        ),
        sa.Column(
            "paid", sa.Boolean, sa.Computed("total_paid_amount >= total_credit_amount")
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )
    op.create_unique_constraint(
        constraint_name="bills_user_id_creditor_id_key",
        table_name=table,
        columns=["user_id", "creditor_id"],
    )


def downgrade() -> None:
    op.drop_table(table)
