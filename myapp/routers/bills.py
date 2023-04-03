from fastapi import APIRouter, Body, Depends, Query, Path
from typing import Annotated
from sqlalchemy.orm import Session

from myapp.utils.database import db_init
from myapp.crud.bills import BillCrud
from myapp.utils.database import db_init
from myapp.schema.bill_payment import BillCreate, BillOut, PaymentOut
from myapp.utils.error_utils import (
    raise_server_error,
    raise_bad_request_http_error,
    handle_empty_records,
)


class BillWithPayments(BillOut):
    payments: list[PaymentOut] = []


router = APIRouter(prefix="/bills", tags=["bills", "debts"])


@router.post("/", response_model=BillOut, status_code=201)
def make_bill(
    db: Annotated[Session, Depends(db_init)], bill_data: Annotated[BillCreate, Body()]
):
    try:
        return BillCrud.create(db=db, bill=bill_data)
    except Exception as e:
        print("🧰🧰", str(e))
        raise_server_error()


@router.patch("/")
def update_bill():
    pass


@router.get("/", response_model=list[BillOut], status_code=200)
def get_bills(
    db: Session = Depends(db_init),
    skip: int = Query(default=0),
    limit: int = Query(default=100),
):
    try:
        bills = BillCrud.get_records(db, skip, limit)
    except Exception:
        raise_server_error()
    else:
        handle_empty_records(records=bills, records_name="bills")
        return bills


@router.get("/{bill_id}", response_model=BillWithPayments, status_code=200)
def get_bill(bill_id: int = Path(), db: Session = Depends(db_init)):
    try:
        bill = BillCrud.get_by_id(db=db, id=bill_id)
    except Exception:
        raise_server_error()
    else:
        return bill
