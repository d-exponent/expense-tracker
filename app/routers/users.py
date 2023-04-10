from typing import Annotated
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, HTTPException, Path, Query, Body, Depends

from app.dependencies import auth
from app.crud.users import UserCrud
from app.utils.database import dbSession
from app.schema.bill_payment import BillOut
from app.utils.error_messages import UserErrorMessages
from app.schema.user import UserCreate, UserOut, UserUpdate
from app.utils.error_utils import handle_empty_records, RaiseHttpException


class UserOutWithBills(UserOut):
    user_bills: list[BillOut] = []


def handle_integrity_error(error_message):
    if "users_password_email_ck" in error_message:
        raise HTTPException(status_code=400, detail="Provide the email and password")

    if "users_phone_email_key" in error_message:
        raise HTTPException(status_code=400, detail=UserErrorMessages.already_exists)

    raise_server_error()


router = APIRouter(prefix="/users", tags=["users"])
raise_server_error = RaiseHttpException.server_error


@router.post("/", response_model=UserOut, status_code=201)
def create_user(
    user: UserCreate,
    db: dbSession,
    protect: Annotated[UserOut, Depends(auth.restrict_to("admin"))],
    # Users should use the signup route ../auth/signup
):
    UserCrud.handle_user_if_exists(db, phone=user.phone_number)

    try:
        user = UserCrud.create(db, user)
    except IntegrityError as error:
        handle_integrity_error(str(error))
    except Exception:
        raise_server_error()
    else:
        return user


@router.patch("/{user_id}", response_model=UserOut, status_code=200)
def update_user(
    db: dbSession,
    user_data: UserUpdate = Body(),
    user_id: int = Path(),
):
    user_data.validate_data()
    updated_user = UserCrud.update_by_id(
        db=db, id=user_id, data=user_data.dict(), model_name_repr="user"
    )

    return updated_user


@router.get("/", response_model=list[UserOut], status_code=200)
def get_all_users(
    db: dbSession,
    protect: Annotated[UserOut, Depends(auth.restrict_to("admin"))],
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
    db: dbSession,
    user_id: int = Path(description=user_id_description),
    phone: str = Query(default=None, description="Retrieve the user by phone number"),
    email: str = Query(default=None, description="Retrive the user by email address"),
):
    if user_id > 0:
        user = UserCrud.get_by_id(db=db, id=user_id)
    else:
        if phone is None and email is None:
            RaiseHttpException.bad_request(
                msg="Provide the user's phone number or email address"
            )

        if phone:
            user = UserCrud.get_user_by_phone(db=db, phone=phone)
        else:  # Email address
            user = UserCrud.get_user_by_email(db=db, email=email)

    if user is None:
        RaiseHttpException.not_found(msg="User not found")

    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(db: dbSession, user_id: Annotated[int, Path()]):
    UserCrud.delete_by_id(db=db, id=user_id)

    return {"message": "Deleted successfully"}
