from pydantic import Field
from typing import Annotated
from fastapi import APIRouter, Query, Path, Body

from app.utils.database import dbSession
from app.schema import bill_payment as bp
from app.crud.payments import PaymentCrud
from app.utils.error_utils import handle_records, RaiseHttpException


class PaymentWithOwnerBill(bp.PaymentOut):
    owner: bp.BillOut = Field(alias="owner_bill")


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=bp.PaymentOut)
def create_payment(
    db: dbSession,
    payment_data: Annotated[bp.PaymentCreate, Body()],
):
    return PaymentCrud.create(db=db, payment=payment_data)


@router.get("/", status_code=200, response_model=list[bp.PaymentOut])
def get_payments(
    db: dbSession,
    skip: int = Query(default=0),
    limit: int = Query(default=100),
):
    try:
        payments = PaymentCrud.get_records(db=db, skip=skip, limit=limit)
    except Exception:
        RaiseHttpException.server_error()
    else:
        return handle_records(records=payments, records_name="payments")


@router.get("/{payment_id}", status_code=200, response_model=PaymentWithOwnerBill)
def get_payment(*, payment_id: Annotated[int, Path()], db: dbSession):
    try:
        return PaymentCrud.get_by_id(db=db, id=payment_id)
    except Exception:
        RaiseHttpException.server_error()
