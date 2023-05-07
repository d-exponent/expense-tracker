from fastapi import APIRouter, Body, Query, Path, Depends
from typing import Annotated


from app.crud.bills import BillCrud
from app.dependencies import auth

from app.schema import bill_payment as bp
from app.schema.response import DefaultResponse
from app.utils.database import dbSession
from app.utils import error_utils as eu, bills as b


class BillWithPayments(bp.BillOut):
    payments: list[bp.PaymentOut] = []


router = APIRouter(
    prefix="/bills", tags=["bills"], dependencies=[auth.current_active_user]
)

allow_admin_staff = [Depends(auth.restrict_to("staff", "admin"))]


@router.post(
    "/",
    response_model=DefaultResponse,
    status_code=201,
    dependencies=allow_admin_staff,
)
def create_bill(db: dbSession, bill_data: Annotated[bp.BillCreate, Body()]):
    return b.handle_make_bill(db, bill=bill_data.__dict__)


@router.get("/", response_model=list[bp.BillOut], dependencies=allow_admin_staff)
def get_bills(
    db: dbSession,
    skip: int = Query(default=0),
    limit: int = Query(default=100),
):
    bills = BillCrud.get_records(db, skip, limit)
    return eu.handle_records(records=bills, table_name="bills")


@router.get("/{id}", response_model=BillWithPayments)
def get_bill(
    db: dbSession, id: Annotated[int, Path()], user: auth.active_user_annontated
):
    eu.ensure_positive_int(num=id)
    bill = BillCrud.get_by_id(db=db, id=id)

    if bill is None:
        eu.RaiseHttpException.not_found("The bill does not exist")

    if user.role not in ("admin", "staff"):
        bills = BillCrud.get_bills_for_user(db, user_id=user.id)

        # Error out if the user didn't make the bill
        if not any(b for b in bills if b.id == bill.id):
            eu.RaiseHttpException.forbidden("You can't get a bill you didn't create")

    return bill


@router.delete(
    "/{id}", status_code=204, dependencies=[Depends(auth.restrict_to("admin"))]
)
def delete_bill(
    db: dbSession,
    id: Annotated[int, Path()],
):
    eu.ensure_positive_int(num=id)

    BillCrud.delete_by_id(db=db, id=id)
    return ""
