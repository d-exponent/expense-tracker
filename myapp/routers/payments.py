from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.orm import Session
from pydantic import Field
from typing import Annotated


from myapp.utils.database import db_init
from myapp.schema.bill_payment import BillOut, PaymentOut, PaymentCreate
from myapp.crud.payments import PaymentCrud
from myapp.utils.error_utils import (
    raise_server_error,
    handle_empty_records,
)


class PaymentWithOwnerBill(PaymentOut):
    owner: BillOut = Field(alias="owner_bill")


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentOut)
def create_payment(
    db: Annotated[Session, Depends(db_init)],
    payment_data: Annotated[PaymentCreate, Body()],
):
    return PaymentCrud.create(db=db, payment=payment_data)


@router.get("/", status_code=200, response_model=list[PaymentOut])
def get_payments(
    db: Session = Depends(db_init),
    skip: int = Query(default=0),
    limit: int = Query(default=100),
):
    try:
        payments = PaymentCrud.get_records(db=db, skip=skip, limit=limit)
    except Exception:
        raise_server_error()
    else:
        handle_empty_records(records=payments, records_name="payments")
        return payments


@router.get("/{payment_id}", status_code=200, response_model=PaymentWithOwnerBill)
def get_payment(payment_id: int = Path(), db: Session = Depends(db_init)):
    try:
        payment = PaymentCrud.get_by_id(db=db, id=payment_id)
    except Exception:
        raise_server_error()
    else:
        return payment
