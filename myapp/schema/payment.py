from pydantic import BaseModel
from datetime import datetime


class PaymentBase(BaseModel):
    amount: float
    created_at: datetime


class Payment(PaymentBase):
    id: int
    bill_id: int
