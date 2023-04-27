"""create payments table

Revision ID: 7e1f6e90055c
Revises: 9532cc16e134
Create Date: 2023-04-13 06:37:12.036088

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import func


# revision identifiers, used by Alembic.
revision = "7e1f6e90055c"
down_revision = "9532cc16e134"
branch_labels = None
depends_on = None
table = "payments"


def upgrade() -> None:
    op.create_table(
        table,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "bill_id",
            sa.Integer,
            sa.ForeignKey("bills.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("note", sa.Text),
        sa.Column(
            "issuer",
            sa.Enum("user", "creditor", name="payments_issuer_enum"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
    )


def downgrade() -> None:
    op.drop_table(table),
    sa.Enum("user", "creditor", name="payments_issuer_enum").drop(op.get_bind())
