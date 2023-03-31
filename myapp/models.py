from myapp.database.sqlalchemy_config import Base

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Computed
from sqlalchemy.sql.expression import text, func
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    ForeignKey,
    LargeBinary,
    Numeric,
    DateTime,
    CheckConstraint,
    UniqueConstraint,
)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("phone", "email", name="users_phone_email_key"),
        CheckConstraint(  # Password and email must exist or not exist together
            "(password IS NUll AND email IS NULL) OR (password IS NOT NULL AND email IS NOT NULL)",
            name="users_password_email_ck",
        ),
    )

    id = Column(Integer, primary_key=True)
    first_name = Column(String(length=40), nullable=False)
    middle_name = Column(String(length=40))
    last_name = Column(String(length=40), nullable=False)
    phone = Column(String(25), unique=True, nullable=False)
    email = Column(String(70), unique=True)
    password = Column(LargeBinary)
    image = Column(String)
    is_active = Column(Boolean, server_default=text("True"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    password_modified_at = Column(DateTime(timezone=True))
    password_reset_token = Column(String)
    password_reset_token_expires_at = Column(DateTime(timezone=True))

    user_bills = relationship("Bill", back_populates="user_owner")


class Creditor(Base):
    __tablename__ = "creditors"
    __table_args__ = (
        UniqueConstraint(
            "phone",
            "account_number",
            name="creditors_phone_account_number_key",
        ),
        CheckConstraint(
            "account_number IS NULL OR bank_name IS NOT NULL",
            name="creditors_account_number_bank_ck",
        ),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(300))
    street_address = Column(String)
    city = Column(String(40), nullable=False)
    state = Column(String(40), nullable=False)
    country = Column(String(40), server_default="Nigeria")
    phone = Column(String(25), nullable=False, unique=True)
    email = Column(String(70), unique=True)
    bank_name = Column(String(100))
    account_number = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Bill(Base):
    __tablename__ = "bills"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "creditor_id", name="bills_user_id_creditor_id_key"
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    creditor_id = Column(
        Integer,
        ForeignKey("creditors.id", ondelete="CASCADE"),
        nullable=False,
    )
    description = Column(String, nullable=False)
    starting_amount = Column(Numeric(10, 2), nullable=False)
    paid_amount = Column(Numeric(10, 2), server_default=text("0.00"))
    current_balance = Column(Numeric(10, 2), Computed("paid_amount - starting_amount"))
    paid = Column(Boolean, Computed("paid_amount >= starting_amount"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    payments = relationship("Payment", back_populates="owner_bill")
    user_owner = relationship("User", back_populates="user_bills")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    bill_id = Column(
        Integer,
        ForeignKey("bills.id", ondelete="CASCADE"),
        nullable=False,
    )
    first_payment = Column(Boolean, server_default=text("False"))
    amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner_bill = relationship("Bill", back_populates="payments")
