from pydantic import BaseModel
from datetime import datetime


class MyBillCreate(BaseModel):
    creditor_id: int
    total_credit_amount: float = 0.00
    total_paid_amount: float = 0.00


class BillCreate(MyBillCreate):
    user_id: int


class BillOut(BillCreate):
    id: int
    paid: bool
    current_balance: float

    class Config:
        orm_mode = True


class BillOutAllInfo(BillOut):
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# PAYMENTS
class PaymentCreate(BaseModel):
    bill_id: int
    note: str = None
    issuer: str
    amount: float


class PaymentOut(PaymentCreate):
    id: int
    created_at: datetime
    owner_bill = list[BillOut]

    class Config:
        orm_mode = True
