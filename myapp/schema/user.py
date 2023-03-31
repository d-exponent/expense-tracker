from pydantic import BaseModel, EmailStr, constr
from fastapi import HTTPException
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


class UserLogin(BaseModel):
    id: int | None
    email: EmailStr | None
    phone: str | None
    password: str

    def validate_schema(self):
        """
        Trows an HTTPException if the object doesn't have
        a name or an email or a phone attribute as not None
        """
        if not any([self.email, self.phone, self.id]):
            raise HTTPException(
                status_code=400,
                detail="Provide the email address or phone number or id of the user",
            )


class UserBase(BaseModel):
    first_name: constr(max_length=40, strip_whitespace=True)
    middle_name: constr(max_length=40, strip_whitespace=True) = None
    last_name: constr(max_length=40, strip_whitespace=True)
    phone: constr(max_length=25, strip_whitespace=True)
    email: EmailStr | None
    image: str = None


class UserCreate(UserBase):
    password: constr(regex=password_reg) | bytes = None


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


# Password must never ever ever ever be sent from our server
class UserAllInfo(UserOut):
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    password_modified_at: datetime = None
    password_reset_token: str = None
    password_reset_token_expires_at: datetime = None

    class Config:
        orm_mode = True
