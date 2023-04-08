from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, HTTPException, Body, Depends, Path, Query

from app.schema.creditor import CreditorCreate, CreditorOut, CreditorUpdate
from app.crud.creditors import CreditorCrud
from app.utils.database import db_init
from app.utils.error_utils import handle_empty_records, RaiseHttpException


router = APIRouter(prefix="/creditors", tags=["creditors"])


def handle_integrity_error(error_message):
    if "creditors_name_key" in error_message:
        raise HTTPException(
            status_code=400, detail="The user with this name already exists"
        )

    if "creditors_account_number_bank_ck" in error_message:
        raise HTTPException(
            status_code=400, detail="Please provide an account number and a bank name."
        )

    if "creditors_email_key" in error_message:
        raise HTTPException(
            status_code=400, detail="This email is already associated with an account"
        )

    if "creditors_phone_account_number_key" in error_message:
        raise HTTPException(
            status_code=400,
            detail="An account number can only be linked with a phone number",
        )

    RaiseHttpException.server_error()


# UPDATE USERS NAMES
@router.patch("/{creditor_id}", response_model=CreditorOut, status_code=200)
def update_user(
    db: Session = Depends(db_init),
    creditor_data: CreditorUpdate = Body(),
    creditor_id: int = Path(),
):
    return CreditorCrud.update_by_id(
        db=db, id=creditor_id, data=creditor_data.dict(), model_name_repr="creditor"
    )


@router.post("/", response_model=CreditorOut, status_code=201)
def create_creditor(creditor: CreditorCreate = Body(), db: Session = Depends(db_init)):
    db_creditor = CreditorCrud.get_creditor_by_phone(db, creditor.phone)

    if db_creditor:
        RaiseHttpException.bad_request(
            msg="This phone is already registered with an account."
        )

    try:
        return CreditorCrud.create(db, creditor)
    except IntegrityError as error:
        handle_integrity_error(str(error))
    except Exception:
        RaiseHttpException.server_error()


@router.get("/", status_code=200, response_model=list[CreditorOut])
def get_creditors(db: Session = Depends(db_init), skip: int = 0, limit: int = 100):
    try:
        creditors = CreditorCrud.get_records(db, skip=skip, limit=limit)
    except Exception:
        RaiseHttpException.server_error()
    else:
        handle_empty_records(records=creditors, records_name="creditors")
        return creditors


@router.get("/{creditor_id}", response_model=CreditorOut)
def get_creditor(
    creditor_id: int = Path(),
    name: str = Query(default=None),
    phone: str = Query(default=None),
    email: str = Query(default=None),
    db: Session = Depends(db_init),
):
    if creditor_id > 0:
        creditor = CreditorCrud.get_by_id(db, id=creditor_id)
    else:
        if not any([phone, name, email]):
            RaiseHttpException.bad_request(
                msg="Provide the phone number, name or email address"
            )

        if phone:
            creditor = CreditorCrud.get_creditor_by_phone(db, phone)
        elif name:
            creditor = CreditorCrud.get_creditor_by_name(db, name)
        else:  # email address
            creditor = CreditorCrud.get_creditor_by_email(db, email)

    if creditor is None:
        RaiseHttpException.not_found(mes="The creditor does not exist")

    return creditor


@router.patch("/{creditor_id}", response_model=CreditorOut)
def update_creditor(
    db: Annotated[Session, Depends(db_init)],
    creditor_id: Annotated[int, Path()],
    creditor_data: Annotated[CreditorUpdate, Body()],
):
    try:
        return CreditorCrud.update_by_id(
            db=db, id=creditor_id, data=creditor_data, model_name_repr="creditor"
        )
    except Exception:
        RaiseHttpException.server_error()


@router.delete("/{creditor_id}", status_code=204)
def delete_user(
    db: Annotated[Session, Depends(db_init)], creditor_id: Annotated[int, Path()]
):
    CreditorCrud.delete_by_id(db=db, id=creditor_id)

    return {"message": "Deleted successfully"}
