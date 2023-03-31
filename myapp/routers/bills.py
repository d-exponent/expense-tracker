from fastapi import APIRouter, Body, Depends, Query, Path
from sqlalchemy.orm import Session

from myapp.crud.bills import BillCrud, CustomBillOut, BillTransactionError
from myapp.utils.database import db_dependency
from myapp.schema.bill import BillCreate, BillOut
from myapp.schema.payment import PaymentOut
from myapp.utils.error_utils import (
    raise_server_error,
    raise_bad_request_http_error,
    handle_empty_records,
)


"""
Doing this here to avoid circular import at myapp.schema.bills
... because Bill Schema and Payment Schema depend on each other
"""


class BillWithPayments(BillOut):
    payments: list[PaymentOut] = []


router = APIRouter(prefix="/bills", tags=["bills", "debts"])


@router.post("/", response_model=CustomBillOut, status_code=201)
def make_bill(bill: BillCreate = Body()):
    try:
        return BillCrud.create(bill=bill)
    except BillTransactionError as e:
        raise_bad_request_http_error(str(e))
    except Exception:
        raise_server_error()


@router.get("/", response_model=list[BillOut], status_code=200)
def get_bills(
    db: Session = Depends(db_dependency),
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
def get_bill(bill_id: int = Path(), db: Session = Depends(db_dependency)):
    try:
        bill = BillCrud.get_by_id(db=db, id=bill_id)
    except Exception:
        raise_server_error()
    else:
        return bill
