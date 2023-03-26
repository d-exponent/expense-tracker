from pydantic import BaseModel
from datetime import datetime


class BillCreate(BaseModel):
    description: str = None
    starting_amount: float
    user_id: int
    creditor_id: int
    paid_amount: float = 0.00


class BillOut(BillCreate):
    id: int = None
    paid: bool = None
    current_balance: float = 0.00

    class Config:
        orm_mode = True


class BillALlInfo(BillOut):
    created_at: datetime = None
    updated_at: datetime = None

    class Config:
        orm_mode = True
