from typing import Annotated
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Body, Path, Query

from app.dependencies import auth
from app.crud.creditors import CreditorCrud
from app.utils.database import dbSession
from app.schema import creditor as cr
from app.utils import error_utils as er


router = APIRouter(
    prefix="/creditors",
    tags=["creditors"],
    dependencies=[auth.allow_user_admin],
)

raise_bad_request = er.RaiseHttpException.bad_request
raise_server_error = er.RaiseHttpException.server_error


def handle_integrity_error(error_message):
    if "creditors_name_key" in error_message:
        raise_bad_request("The user with this name already exists")

    if "creditors_account_number_bank_ck" in error_message:
        raise_bad_request("Please provide an account number and a bank name.")

    if "creditors_email_key" in error_message:
        raise_bad_request("This email is already associated with an account")

    if "creditors_phone_key" in error_message:
        raise_bad_request("This phone is already associated with an account")

    if "creditors_phone_account_number_key" in error_message:
        raise_bad_request("An account number can only be linked with one phone number")

    raise_server_error()


@router.post("/", response_model=cr.CreditorOut, status_code=201)
def create_creditor(db: dbSession, creditor: Annotated[cr.CreditorCreate, Body()]):
    try:
        return CreditorCrud.create(db, creditor)
    except IntegrityError as e:
        handle_integrity_error(str(e))
    except Exception:
        raise_server_error()


@router.get("/", response_model=list[cr.CreditorOut])
def get_creditors(db: dbSession, skip: int = 0, limit: int = 100):
    try:
        creditors = CreditorCrud.get_records(db, skip=skip, limit=limit)
    except Exception:
        raise_server_error()
    else:
        return er.handle_records(records=creditors, table_name="creditors")


@router.get("/{creditor_id}", response_model=cr.CreditorOut)
def get_creditor(
    db: dbSession,
    creditor_id: Annotated[int, Path()],
    name: str = Query(default=None),
    phone: str = Query(default=None),
    email: str = Query(default=None),
):
    if creditor_id > 0:
        creditor = CreditorCrud.get_by_id(db, id=creditor_id)
    else:
        if not any([phone, name, email]):
            raise_bad_request(msg="Provide the phone number, name or email address")

        if phone:
            creditor = CreditorCrud.get_creditor_by_phone(db, phone)
        elif name:
            creditor = CreditorCrud.get_creditor_by_name(db, name)
        else:  # email address
            creditor = CreditorCrud.get_creditor_by_email(db, email)

    if creditor is None:
        er.RaiseHttpException.not_found("The creditor does not exist")

    return creditor


@router.patch("/{creditor_id}", response_model=cr.CreditorOut)
def update_creditor(
    db: dbSession,
    creditor_id: Annotated[int, Path()],
    creditor_data: Annotated[cr.CreditorUpdate, Body()],
):
    try:
        return CreditorCrud.update_by_id(
            db, creditor_id, creditor_data.dict(), "creditor"
        )
    except Exception:
        raise_server_error()


@router.delete("/{creditor_id}", status_code=204)
def delete_user(db: dbSession, creditor_id: Annotated[int, Path()]):
    try:
        CreditorCrud.delete_by_id(db=db, id=creditor_id)
    except Exception:
        raise_server_error()
    else:
        return {"message": "Deleted successfully"}
