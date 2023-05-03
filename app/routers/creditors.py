from typing import Annotated
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Body, Path, Query, Depends

from app.dependencies import auth
from app.crud.creditors import CreditorCrud
from app.utils.database import dbSession
from app.utils.custom_exceptions import DataError
from app.schema.response import DefaultResponse
from app.schema import creditor as cr
from app.utils import error_utils as eu

router = APIRouter(
    prefix="/creditors",
    tags=["creditors"],
    dependencies=[auth.current_active_user],
)


@router.post("/", response_model=DefaultResponse, status_code=201)
def create_creditor(db: dbSession, creditor: Annotated[cr.CreditorCreate, Body()]):
    try:
        creditor = CreditorCrud.create(db, creditor)
    except IntegrityError as e:
        eu.handle_create_creditor_integrity_exception(str(e))
    else:
        return DefaultResponse(
            data=creditor, message="Creditor is created successfully"
        )


@router.get("/", response_model=DefaultResponse)
def get_creditors(db: dbSession, skip: int = 0, limit: int = 100):
    creditors = CreditorCrud.get_records(db, skip=skip, limit=limit)
    return DefaultResponse(
        data=eu.handle_records(records=creditors, table_name="creditors")
    )


@router.get("/{id}", response_model=DefaultResponse)
def get_creditor(
    db: dbSession,
    id: Annotated[int, Path()],
    name: str = Query(default=None),
    phone: str = Query(default=None),
    email: str = Query(default=None),
):
    if id > 0:
        creditor = CreditorCrud.get_by_id(db, id=id)
    else:
        if not any([phone, name, email]):
            eu.RaiseHttpException.bad_request(
                "Provide the phone number, name or email address"
            )

        if phone:
            creditor = CreditorCrud.get_by_phone(db, phone)
        elif name:
            creditor = CreditorCrud.get_creditor_by_name(db, name)
        else:  # email address
            creditor = CreditorCrud.get_by_email(db, email)

    if creditor is None:
        eu.RaiseHttpException.not_found("The creditor does not exist")

    return DefaultResponse(data=creditor)


@router.patch("/{id}", response_model=DefaultResponse)
def update_creditor(
    db: dbSession,
    id: Annotated[int, Path()],
    creditor_data: Annotated[cr.CreditorUpdate, Body()],
):
    try:
        data = creditor_data.ensure_valid_field()
    except DataError as e:
        eu.RaiseHttpException.bad_request(str(e))
    else:
        updated = CreditorCrud.update_by_id(db, id, data, table_name="creditors")
        return DefaultResponse(data=updated)


@router.delete(
    "/{my_id}",
    status_code=204,
    dependencies=[Depends(auth.restrict_to("staff", "admin"))],
)
def delete_creditor(db: dbSession, id: Annotated[int, Path()]):
    CreditorCrud.delete_by_id(db=db, id=id, record_name="creditor")
    return ""
