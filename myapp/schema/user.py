from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from myapp.schema.bill import Bill
from myapp.schema.payment import Payment


class UserBase(BaseModel):
    id: int = None
    first_name: constr(max_length=40, strip_whitespace=True)
    last_name: constr(max_length=40, strip_whitespace=True)
    phone: constr(max_length=25, strip_whitespace=True)
    email: EmailStr | None
    image: str = None


"""
USER PASSWORD REGEX REQUIREMENTS
1. Must have at least one Uppercase letter
2. Must have at least one number character
3. Must have at least one symbol
4. Must be at least eight(8) characters long

"""
password_reg = "^(?=(.*[A-Z]){1,})(?=(.*[0-9]){1,})(?=(.*[!@#$%^&*()\-__+.]){1,}).{8,}$"


class UserCreate(UserBase):
    password: constr(regex=password_reg) = None


class UserOut(UserBase):
    bills: list[Bill] = []
    payments: list[Payment] = []

    class Config:
        orm_mode = True


class UserComplete(UserOut):
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    password_modified_at: datetime = None
    password_reset_token: str = None
    password_reset_token_expires_at: datetime = None

    class Config:
        orm_mode = True
