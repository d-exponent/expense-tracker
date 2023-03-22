from sqlalchemy.orm import relationship
from sqlalchemy.schema import FetchedValue, Computed
from sqlalchemy.sql.expression import text, func
from myapp.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    ForeignKey,
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
    last_name = Column(String(length=40), nullable=False)
    phone = Column(String(25), unique=True, nullable=False)
    email = Column(String(70), unique=True)
    password = Column(String)
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

    # bills = relationship("Bill", back_populates="users")
    # payments = relationship("Payment", back_populates="users")

    def __repr__(self) -> str:
        return f"""
            ID: {self.id}, Name: {self.first_name} {self.last_name}
            Phone: {self.phone}, Email: {self.email}
            Created: {self.created_at}, Updated: {self.updated_at}
            active: {self.is_active}
        """


class Creditor(Base):
    __tablename__ = "creditors"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(240))
    street_address = Column(String)
    city = Column(String(40))
    state = Column(String(40))
    country = Column(String(40), server_default="Nigeria")
    phone = Column(String(25), nullable=False)
    email = Column(String(70))
    bank_name = Column(String(100))
    account_number = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # bills = relationship("Bill", back_populates="creditors")
    # payments = relationship("Payment", back_populates="creditors")


# class Bill(Base):
#     __tablename__ = "bills"

#     id = Column(Integer, primary_key=True)
#     user_id = Column(
#         Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
#     )
#     creditor_id = Column(
#         Integer, ForeignKey("creditors.id", ondelete="CASCADE"), nullable=False
#     )
#     description = Column(String)
#     starting_amount = Column(Numeric(10, 2), nullable=False)
#     paid_amount = Column(Numeric(10, 2), server_default=text("0"))
#     current_balance = Column(Numeric(10, 2), Computed("paid_amount - starting_amount"))
#     paid = Column(Boolean, Computed("paid_amount >= starting_amount"))

#     created_at = Column(DateTime(timezone=True), server_default=func.now())
# updated_at = Column(
#     DateTime(timezone=True),
#     server_default=func.now(),
#     onupdate=func.now(),
# )

#     payments = relationship("Payment", back_populates="bills")
#     users = relationship("User", back_populates="users")
#     creditors = relationship("Creditor", back_populates="bills")


# class Payment(Base):
#     __tablename__ = "payments"

#     id = Column(Integer, primary_key=True)
#     bill_id = Column(
#         Integer, ForeignKey("bills.id", ondelete="CASCADE"), nullable=False
#     )
#     amount = Column(Numeric(10, 2), nullable=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

#     bills = relationship("Bill", back_populates="payments")
