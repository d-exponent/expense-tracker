from pydantic import BaseModel, EmailStr, constr
from datetime import datetime

from app.schema.user import e_164_phone_regex
from app.schema.commons import Update


class CreditorCreateOptional(BaseModel):
    description: constr(strip_whitespace=True, max_length=300) = None
    country: constr(strip_whitespace=True, max_length=40) = None
    bank_name: constr(strip_whitespace=True, max_length=40) = None
    street_address: str = None
    account_number: str = None


class MyCreditorCreate(CreditorCreateOptional):
    phone: constr(max_length=25, regex=e_164_phone_regex, strip_whitespace=True)
    email: EmailStr = None
    name: constr(strip_whitespace=True, max_length=100)
    city: constr(strip_whitespace=True, max_length=40)
    state: constr(strip_whitespace=True, max_length=40)


class CreditorOwner(BaseModel):
    owner_id: int


class MyCreditorOut(MyCreditorCreate):
    id: int


class CreditorCreate(MyCreditorCreate, CreditorOwner):
    pass


class CreditorUpdate(CreditorCreateOptional, Update):
    email: EmailStr = None
    name: constr(strip_whitespace=True, max_length=100) = None
    city: constr(strip_whitespace=True, max_length=40) = None
    state: constr(strip_whitespace=True, max_length=40) = None
    phone: constr(max_length=25, regex=e_164_phone_regex, strip_whitespace=True) = None


class CreditorOut(MyCreditorOut, CreditorOwner):
    class Config:
        orm_mode = True


class CreditorAllInfo(CreditorOut):
    created_at = datetime
    updated_at = datetime

    class Config:
        orm_mode = True
