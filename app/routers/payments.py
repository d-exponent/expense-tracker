from pydantic import Field
from typing import Annotated
from fastapi import APIRouter, Query, Path, Body, Depends

from app.dependencies import auth

from app.utils.database import dbSession
from app.utils import error_utils as eu
from app.schema.user import UserAllInfo
from app.schema import bill_payment as bp
from app.crud.bills import BillCrud
from app.crud.payments import PaymentCrud, CreatePaymentException


allow_staff_admin = [Depends(auth.restrict_to("staff", "admin"))]
allow_only_user = [Depends(auth.restrict_to("user"))]


class PaymentWithOwnerBill(bp.PaymentOut):
    owner: bp.BillOut = Field(alias="owner_bill")


router = APIRouter(
    prefix="/payments", tags=["payments"], dependencies=[auth.current_active_user]
)


@router.post(
    "/",
    response_model=bp.PaymentOut,
    status_code=201,
)
def create_payment(db: dbSession, payment_data: Annotated[bp.PaymentCreate, Body()]):
    try:
        return PaymentCrud.create(db=db, payment=payment_data)
    except CreatePaymentException as e:
        eu.RaiseHttpException.bad_request(str(e))


@router.get("/", response_model=list[bp.PaymentOut], dependencies=allow_staff_admin)
def get_payments(
    db: dbSession, skip: int = Query(default=0), limit: int = Query(default=100)
):
    payments = PaymentCrud.get_records(db=db, skip=skip, limit=limit)
    return eu.handle_records(records=payments, table_name="payments")


@router.get(
    "/{id}",
    status_code=200,
    response_model=PaymentWithOwnerBill,
)
def get_payment(
    db: dbSession,
    id: Annotated[int, Path()],
    user: Annotated[UserAllInfo, auth.current_active_user],
):
    eu.ensure_positive_int(num=id)
    payment = PaymentCrud.get_by_id(db, id)

    if payment is None:
        eu.RaiseHttpException.not_found("The payment was not found")

    # Admins and staffs have unlimited access to get a payment
    # Alt users.role == 'user', however more roles might be added eg 'creditiors' which would break the check
    if user.role not in ("admin", "staff"):
        users_bills = BillCrud.get_bills_for_user(db, user_id=user.id)

        # Ensure only a user who made a payment can view it
        if len([bill for bill in users_bills if bill.id == payment.bill_id]) == 0:
            message = "You can only get a payment you made"
            eu.RaiseHttpException.forbidden(message)

    return payment
