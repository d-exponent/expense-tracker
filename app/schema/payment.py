from pydantic import BaseModel
from datetime import datetime


class PaymentCreate(BaseModel):
    bill_id: int
    amount: float
    first_payment: bool = False


class PaymentOut(PaymentCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True