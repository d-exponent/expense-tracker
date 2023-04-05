from pydantic import BaseModel, EmailStr, constr
from datetime import datetime


"""
USER PASSWORD REGEX REQUIREMENTS
1. Must have at least one Uppercase letter
2. Must have at least one number character
3. Must have at least one symbol
4. Must be at least eight(8) characters long

"""
password_reg = "^(?=(.*[A-Z]){1,})(?=(.*[0-9]){1,})(?=(.*[!@#$%^&*()\-__+.]){1,}).{8,}$"


class UserLoginEmailPassword(BaseModel):
    email_address: EmailStr | None
    password: str


class UserLoginPhoneNumber(BaseModel):
    phone_number: str | None


class UserLoginId(BaseModel):
    id: int | None


class UserBase(BaseModel):
    first_name: constr(max_length=40, strip_whitespace=True)
    middle_name: constr(max_length=40, strip_whitespace=True) = None
    last_name: constr(max_length=40, strip_whitespace=True)
    phone_number: constr(max_length=25, strip_whitespace=True)
    email_address: EmailStr | None
    image_url: str = None


class UserCreate(UserBase):
    password: constr(regex=password_reg)


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


# Password must never ever ever ever be sent from our server
class UserAllInfo(UserOut):
    is_active: bool = True
    created_at: datetime
    verified: bool
    updated_at: datetime
    password_modified_at: datetime = None
    password_reset_token: str = None
    password_reset_token_expires_at: datetime = None

    class Config:
        orm_mode = True
