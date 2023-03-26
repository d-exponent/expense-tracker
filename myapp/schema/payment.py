from pydantic import BaseModel
from datetime import datetime


class PaymentCreate(BaseModel):
    bill_id: int
    amount: float


class PaymentOut(PaymentCreate):
    id: int

    class Config:
        orm_mode = True


class PaymentAllInfo(PaymentOut):
    created_at: datetime

    class Config:
        orm_mode = True
