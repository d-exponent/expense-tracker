from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from myapp.utils.error_messages import UserErrorMessages
from myapp.schema.bill import BillOut
from myapp.utils.database import db_dependency
from myapp.schema.user import UserCreate, UserOut
from myapp.crud.users import UserCrud
from myapp.utils.error_utils import (
    raise_server_error,
    handle_empty_records,
)


class UserOutWithBills(UserOut):
    user_bills: list[BillOut] = []


def handle_integrity_error(error_message):
    if "users_password_email_ck" in error_message:
        raise HTTPException(status_code=400, detail="Provide the email and password")

    if "users_phone_email_key" in error_message:
        raise HTTPException(status_code=400, detail=UserErrorMessages.already_exists)

    raise_server_error()


router = APIRouter(prefix="/users", tags=["users"])


# CREATE AND PERSIT A NEW USER TO DB IF NOT EXISTS
@router.post("/", response_model=UserOut, status_code=201)
def create_users(user: UserCreate, db: Session = Depends(db_dependency)):
    db_user = UserCrud.get_user_by_phone(db, user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail=UserErrorMessages.already_exists)

    try:
        return UserCrud.create(db, user)
    except IntegrityError as error:
        handle_integrity_error(str(error))
    except Exception:
        raise_server_error()


# GET AN ARRAY OF USERS
@router.get("/", response_model=list[UserOut], status_code=200)
def get_all_users(
    db: Session = Depends(db_dependency),
    skip: int = Query(default=0),
    limit: int = Query(default=100),
):
    try:
        users = UserCrud.get_records(db=db, skip=skip, limit=limit)
    except Exception:
        raise_server_error()
    else:
        handle_empty_records(records=users, records_name="users")
        return users


user_id_description = "If you don't have the users id, provide any integer less than one and the users phone number or email adress via a query"


# GET A SINGLE USER BY ID
@router.get("/{user_id}", response_model=UserOutWithBills, status_code=200)
def get_user(
    user_id: int = Path(description=user_id_description),
    phone: str = Query(default=None, description="Retrieve the user by phone number"),
    email: str = Query(default=None, description="Retrive the user by email address"),
    db: Session = Depends(db_dependency),
):
    if user_id > 0:
        user = UserCrud.get_by_id(db=db, id=user_id)
    else:
        if phone is None and email is None:
            raise HTTPException(
                status_code=400,
                detail="Provide the user's phone number or email address",
            )

        if phone:
            user = UserCrud.get_user_by_phone(db=db, phone=phone)
        else:  # Email address
            user = UserCrud.get_user_by_email(db=db, email=email)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
