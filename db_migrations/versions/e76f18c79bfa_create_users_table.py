"""create users table

Revision ID: e76f18c79bfa
Revises:
Create Date: 2023-04-04 15:11:24.572980

"""
from alembic import op
from sqlalchemy.sql.expression import text, func
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
        sa.Column("middle_name", sa.String(25), unique=True),
        sa.Column("last_name", sa.String(length=40), nullable=False),
        sa.Column("phone_number", sa.String(25), nullable=False),
        sa.Column("verified", sa.Boolean(), server_default=text("False")),
        sa.Column("phone_number_login_otp", sa.String(6)),
        sa.Column("phone_number_login_otp_expires", sa.DateTime(timezone=True)),
        sa.Column("phone_number_signup_otp", sa.String(6)),
        sa.Column("phone_number_signup_otp_expires", sa.DateTime(timezone=True)),
        sa.Column("email_address", sa.String(70), unique=True),
        sa.Column("password", sa.LargeBinary),
        sa.Column("image_url", sa.String),
        sa.Column("is_active", sa.Boolean, server_default=text("True")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
        sa.Column("password_modified_at", sa.DateTime(timezone=True)),
        sa.Column("password_reset_token", sa.String),
        sa.Column("password_reset_token_expires_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint(
            "country_code", "phone_number", name="users_country_code_phone_number_key"
        ),
        sa.UniqueConstraint(
            "phone_number", "email_address", name="users_phone_number_email_address_key"
        ),
        sa.CheckConstraint(
            """
                (password IS NUll AND email_address IS NULL)
                OR
                (password IS NOT NULL AND email_address IS NOT NULL)
            """,
            name="users_password_email_address_ck",
        ),
    )


def downgrade():
    op.drop_table(table_name="users")
