import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text, func

from app.database.sqlalchemy_config import Base
from app.utils import auth as au


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        sa.UniqueConstraint(
            "phone_number", "email_address", name="users_phone_email_key"
        ),
        sa.CheckConstraint(  # Password and email must exist or not exist together
            """
                (password IS NUll AND email_address IS NULL)
                OR
                (password IS NOT NULL AND email_address IS NOT NULL)
            """,
            name="users_password_email_ck",
        ),
    )

    id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.String(length=40), nullable=False)
    middle_name = sa.Column(sa.String(length=40))
    last_name = sa.Column(sa.String(length=40), nullable=False)
    phone_number = sa.Column(sa.String(25), unique=True, nullable=False)
    email_address = sa.Column(sa.String(30), unique=True)
    verified = sa.Column(sa.Boolean(), server_default=text("False"))
    otp = sa.Column(sa.String)
    otp_expires_at = sa.Column(
        sa.DateTime(timezone=True),
    )
    role = sa.Column(sa.Enum("user", "staff", "admin", name="users_role_enum"))
    password = sa.Column(sa.LargeBinary)
    image_url = sa.Column(sa.String)
    is_active = sa.Column(sa.Boolean, server_default=text("True"))
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    password_modified_at = sa.Column(sa.DateTime(timezone=True))
    password_reset_token = sa.Column(sa.String)
    password_reset_token_expires_at = sa.Column(sa.DateTime(timezone=True))

    user_bills = relationship("Bill", back_populates="user_owner")

    def compare_password(self, password) -> bool:
        return au.authenticate_password(password, self.password)


class Creditor(Base):
    __tablename__ = "creditors"
    __table_args__ = (
        sa.UniqueConstraint(
            "phone",
            "account_number",
            name="creditors_phone_account_number_key",
        ),
        sa.CheckConstraint(
            "account_number IS NULL OR bank_name IS NOT NULL",
            name="creditors_account_number_bank_ck",
        ),
    )

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), nullable=False, unique=True)
    description = sa.Column(sa.String(300))
    street_address = sa.Column(sa.String)
    city = sa.Column(sa.String(40), nullable=False)
    state = sa.Column(sa.String(40), nullable=False)
    country = sa.Column(sa.String(40), server_default="Nigeria")
    phone = sa.Column(sa.String(25), nullable=False, unique=True)
    email = sa.Column(sa.String(70), unique=True)
    bank_name = sa.Column(sa.String(100))
    account_number = sa.Column(sa.String)

    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Bill(Base):
    __tablename__ = "bills"
    __table_args__ = (
        sa.UniqueConstraint(
            "user_id", "creditor_id", name="bills_user_id_creditor_id_key"
        ),
    )

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    creditor_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("creditors.id", ondelete="SET NULL"),
        nullable=False,
    )
    total_credit_amount = sa.Column(sa.Numeric(10, 2), server_default=text("0.00"))
    total_paid_amount = sa.Column(sa.Numeric(10, 2), server_default=text("0.00"))
    current_balance = sa.Column(
        sa.Numeric(10, 2), sa.Computed("total_paid_amount - total_credit_amount")
    )
    paid = sa.Column(
        sa.Boolean, sa.Computed("total_paid_amount >= total_credit_amount")
    )

    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    updated_at = sa.Column(
        sa.DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    payments = relationship("Payment", back_populates="owner_bill")
    user_owner = relationship("User", back_populates="user_bills")


class Payment(Base):
    __tablename__ = "payments"

    id = sa.Column(sa.Integer, primary_key=True)
    bill_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("bills.id", ondelete="CASCADE"),
        nullable=False,
    )
    note = sa.Column(sa.Text)
    issuer = sa.Column(
        sa.Enum("user", "creditor", name="payments_issuer_enum"), nullable=False
    )
    amount = sa.Column(sa.Numeric(10, 2), nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())

    owner_bill = relationship("Bill", back_populates="payments")
