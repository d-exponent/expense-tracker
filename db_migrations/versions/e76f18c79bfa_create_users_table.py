"""create users table

Revision ID: e76f18c79bfa
Revises:
Create Date: 2023-04-04 15:11:24.572980

"""
from alembic import op
from sqlalchemy.sql.expression import text, func

# from sqlalchemy.sql import column, func
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e76f18c79bfa"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("first_name", sa.String(length=40), nullable=False),
        sa.Column("middle_name", sa.String(40)),
        sa.Column("last_name", sa.String(length=40), nullable=False),
        sa.Column("phone_number", sa.String(25), nullable=False),
        sa.Column("verified", sa.Boolean(), server_default=text("False")),
        sa.Column("mobile_otp", sa.String(6)),
        sa.Column("mobile_otp_expires_at", sa.DateTime(timezone=True)),
        sa.Column("email_address", sa.String(30), unique=True),
        sa.Column("password", sa.LargeBinary),
        sa.Column("image_url", sa.String),
        sa.Column("is_active", sa.Boolean, server_default=text("True")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column("role", sa.Enum("user", "staff", "admin", name="users_role_enum")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
        sa.Column("password_modified_at", sa.DateTime(timezone=True)),
        sa.Column("password_reset_token", sa.String),
        sa.Column("password_reset_token_expires_at", sa.DateTime(timezone=True)),
    ),
    op.create_check_constraint(
        constraint_name="users_password_email_address_ck",
        table_name="users",
        condition="""
            (password IS NUll AND email_address IS NULL)
            OR
            (password IS NOT NULL AND email_address IS NOT NULL)
        """,
    ),
    op.create_unique_constraint(
        constraint_name="users_phone_number_email_address_key",
        table_name="users",
        columns=["email_address", "phone_number"],
    ),


def downgrade():
    op.drop_table(table_name="users"),
    sa.Enum("user", "staff", "admin", name="users_role_enum").drop(op.get_bind())
