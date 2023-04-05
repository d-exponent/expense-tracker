from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session


from app.utils.database import db_dependency
from app.schema.payment import PaymentOut
from app.schema.bill import BillOut
from app.crud.payments import PaymentCrud
from app.utils.error_utils import (
    raise_server_error,
    handle_empty_records,
)


class PaymentWithOwnerBill(PaymentOut):
    owner_bill: BillOut


router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/", status_code=200, response_model=list[PaymentOut])
def get_payments(
    db: Session = Depends(db_dependency),
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
def get_payment(payment_id: int = Path(), db: Session = Depends(db_dependency)):
    try:
        payment = PaymentCrud.get_by_id(db=db, id=payment_id)
    except Exception:
        raise_server_error()
    else:
        return payment
