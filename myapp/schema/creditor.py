from pydantic import BaseModel


class CreditorBase(BaseModel):
    description: str
    name: str
    city: str
    email: str
    state: str
    country: str = None
    phone: str


class CreditorsCreate(CreditorBase):
    pass


class Creditors(CreditorBase):
    id: int
