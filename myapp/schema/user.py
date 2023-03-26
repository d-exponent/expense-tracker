from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from myapp.schema.bill import BillOut
from myapp.schema.payment import PaymentOut


"""
USER PASSWORD REGEX REQUIREMENTS
1. Must have at least one Uppercase letter
2. Must have at least one number character
3. Must have at least one symbol
4. Must be at least eight(8) characters long

"""
password_reg = "^(?=(.*[A-Z]){1,})(?=(.*[0-9]){1,})(?=(.*[!@#$%^&*()\-__+.]){1,}).{8,}$"


class UserCreate(BaseModel):
    first_name: constr(max_length=40, strip_whitespace=True)
    middle_name: constr(max_length=40, strip_whitespace=True) = None
    last_name: constr(max_length=40, strip_whitespace=True)
    phone: constr(max_length=25, strip_whitespace=True)
    email: EmailStr | None
    image: str = None
    password: constr(regex=password_reg) = None


class UserOut(UserCreate):
    id: int
    bills: list[BillOut] = []
    payments: list[PaymentOut] = []

    class Config:
        orm_mode = True


class UserAllInfo(UserOut):
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    password_modified_at: datetime = None
    password_reset_token: str = None
    password_reset_token_expires_at: datetime = None

    class Config:
        orm_mode = True
