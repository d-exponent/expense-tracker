from pydantic import BaseModel, EmailStr, constr
from datetime import datetime

from app.schema.bill import BillOut
from app.schema.payment import PaymentOut


class CreditorCreate(BaseModel):
    name: constr(strip_whitespace=True, max_length=100)
    description: constr(strip_whitespace=True, max_length=300) = None
    street_address: str = None
    city: constr(strip_whitespace=True, max_length=40)
    state: constr(strip_whitespace=True, max_length=40)
    country: constr(strip_whitespace=True, max_length=40) = None
    phone: str
    email: EmailStr = None
    bank_name: constr(strip_whitespace=True, max_length=40) = None
    account_number: str = None


class CreditorOut(CreditorCreate):
    id: int = None

    class Config:
        orm_mode = True


class CreditorAllInfo(CreditorOut):
    created_at = datetime
    updated_at = datetime

    class Config:
        orm_mode = True
