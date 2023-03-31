from pydantic import BaseModel, constr
from datetime import datetime


class BillCreate(BaseModel):
    user_id: int
    creditor_id: int
    description: constr(strip_whitespace=True)
    starting_amount: float
    paid_amount: float = 0.00


class BillOut(BillCreate):
    id: int
    paid: bool
    current_balance: float

    class Config:
        orm_mode = True


class BillALlInfo(BillOut):
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# FOR BILLS CRUD ONLY
class UserInfo(BaseModel):
    user_id: int
    user_names: constr(strip_whitespace=True)


class CreditorInfo(BaseModel):
    creditor_id: int
    creditor_name: constr(strip_whitespace=True)


class CustomBillOut(BaseModel):
    bill_id: int
    user: UserInfo
    creditor: CreditorInfo
    starting_amount: float
    paid_amount: float
    paid: bool
    description: str
    current_balance: float
    created_at: datetime
    last_updated: datetime
    payment_record_id: int
    balance_detail: constr(strip_whitespace=True)
