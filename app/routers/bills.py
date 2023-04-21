from fastapi import APIRouter, Body, Query, Path
from typing import Annotated

from app.crud.bills import BillCrud
from app.utils.database import dbSession
from app.schema import bill_payment as bp
from app.dependencies import auth
from app.utils.error_utils import RaiseHttpException, handle_records


class BillWithPayments(bp.BillOut):
    payments: list[bp.PaymentOut] = []


raise_server_error = RaiseHttpException.server_error
raise_bad_request_error = RaiseHttpException.bad_request

router = APIRouter(
    prefix="/bills", tags=["bills"], dependencies=[auth.allow_only_user]
)


@router.post("/", response_model=bp.BillOut, status_code=201)
def make_bill(db: dbSession, bill_data: Annotated[bp.BillCreate, Body()]):
    try:
        return BillCrud.create(db, bill=bill_data)
    except Exception as e:
        error = str(e)
        if 'is not present in table "creditors"' in error:
            raise_bad_request_error(
                f"Creditor with id:{bill_data.creditor_id} - does not exist"
            )
        if 'is not present in table "users"' in error:
            raise_bad_request_error(
                f"User with id:{bill_data.user_id} - does not exist"
            )

        if "bills_user_id_creditor_id_key" in error:
            raise_bad_request_error("This bill already exists")

        raise_server_error()


@router.get("/", response_model=list[bp.BillOut])
def get_bills(
    db: dbSession,
    skip: int = Query(default=0),
    limit: int = Query(default=100),
):
    try:
        bills = BillCrud.get_records(db, skip, limit)
    except Exception:
        raise_server_error()
    else:
        return handle_records(records=bills, table_name="bills")


@router.get("/{bill_id}", response_model=BillWithPayments)
def get_bill(db: dbSession, bill_id: Annotated[int, Path()]):
    try:
        bill = BillCrud.get_by_id(db=db, id=bill_id)
    except Exception:
        raise_server_error()
    else:
        if bill is None:
            RaiseHttpException.not_found("The bill does not exist")
        return bill


@router.delete("/{bill_id}", status_code=204, dependencies=[auth.allow_only_user])
def delete_bill(db: dbSession, bill_id: Annotated[int, Path()]):
    try:
        BillCrud.delete_by_id(db=db, id=bill_id)
    except Exception:
        raise_server_error("Something went wrong when deleting the bill")

    return {"message": "Bill deleted successfully"}
