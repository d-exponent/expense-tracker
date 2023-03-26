from fastapi import APIRouter, HTTPException, Body, Depends, Path, Query
from sqlalchemy.exc import IntegrityError, DataError
from myapp.schema.creditor import CreditorCreate, CreditorOut
from myapp.crud.creditors import CreditorCrud
from myapp.models import Base
from myapp.dependencies import database, error_utils
from myapp.database.sqlalchemy_config import engine
from sqlalchemy.orm import Session


Base.metadata.create_all(bind=engine)

db_instance = database.db_dependency

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

    print("🧰🧰🧰 INTEGRITY", error_message)
    error_utils.raise_server_error()


def handle_data_error(error_message):
    # TODO: handle Data errors
    print("🧰🧰🧰 DATAERROR", error_message)
    error_utils.raise_server_error()


@router.post("/", response_model=CreditorOut, status_code=201)
def create_creditor(
    creditor: CreditorCreate = Body(), db: Session = Depends(db_instance)
):
    db_creditor = CreditorCrud.get_creditor_by_phone(db, creditor.phone)

    if db_creditor:
        raise HTTPException(
            status_code=400, detail="This phone is already registered to an account."
        )

    try:
        users = CreditorCrud.create(db, creditor)
    except IntegrityError as error:
        handle_integrity_error(str(error))

    except DataError as error:
        handle_data_error(str(error))

    except Exception as error:
        print('🧰🧰🧰🧰 Operator', str(error))
        error_utils.raise_server_error()
    else:
        return users


@router.get("/", status_code=200, response_model=list[CreditorOut])
def get_creditors(db: Session = Depends(db_instance), skip: int = 0, limit: int = 100):
    creditors = CreditorCrud.get_records(db, skip=skip, limit=limit)

    if len(creditors) == 0:
        raise HTTPException(
            status_code=404, detail="There are no creditors at this time."
        )

    return creditors


@router.get("/{creditor_id}", response_model=CreditorOut)
def get_creditor(
    creditor_id: int = Path(),
    name: str = Query(default=None),
    phone: str = Query(default=None),
    email: str = Query(default=None),
    db: Session = Depends(db_instance),
):
    creditor = None

    if creditor_id > 0:
        creditor = CreditorCrud.get_by_id(db, id=creditor_id)
    else:
        if not any([phone, name, email]):
            raise HTTPException(
                status_code=400,
                detail="Please provide the phone number, name or email address",
            )

        if phone:
            creditor = CreditorCrud.get_creditor_by_phone(db, phone)
        elif name:
            creditor = CreditorCrud.get_creditor_by_name(db, name)
        else:  # email address
            creditor = CreditorCrud.get_creditor_by_email(db, email)

    if creditor is None:
        raise HTTPException(status_code=404, detail="Could not find this creditor")

    return creditor
