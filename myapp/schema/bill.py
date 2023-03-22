from pydantic import BaseModel


class BillBase(BaseModel):
    description: str = None
    starting_amount: float
    paid_amount: float = 0.00
    current_balance: float = 0
    paid: bool


class BillCreate(BillBase):
    pass


class Bill(BillBase):
    id: int
    user_id: int
    creditor_id: int
