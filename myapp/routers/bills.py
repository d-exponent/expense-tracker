from fastapi import APIRouter, Body
from myapp.crud.bills import BillCrud
from myapp.schema.bill import BillCreate


router = APIRouter(prefix="/bills", tags=["bills", "debts"])


@router.post("/")
def make_bill(bill: BillCreate = Body()):
    BillCrud.create(bill=bill)
    return "Bills Routes"
