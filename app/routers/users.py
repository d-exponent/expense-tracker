from typing import Annotated
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, HTTPException, Path, Query, Body, Depends

from app.dependencies import auth
from app.crud.users import UserCrud
from app.utils.database import dbSession
from app.schema.bill_payment import BillOut
from app.routers import me
from app.utils.error_messages import UserErrorMessages
from app.schema.user import UserCreate, UserOut, UserUpdate
from app.utils.error_utils import handle_records, RaiseHttpException


class UserOutWithBills(UserOut):
    user_bills: list[BillOut] = []


def handle_integrity_error(error_message):
    if "users_password_email_ck" in error_message:
        raise HTTPException(status_code=400, detail="Provide the email and password")

    if "users_phone_email_key" in error_message:
        raise HTTPException(status_code=400, detail=UserErrorMessages.already_exists)

    raise_server_error()


router = APIRouter(prefix="/users", tags=["users"], dependencies=[auth.protect])
router.include_router(me.router)

raise_server_error = RaiseHttpException.server_error
admin_user_restrict = Annotated[UserOut, Depends(auth.restrict_to("user", "admin"))]


@router.post(
    "/", response_model=UserOut, status_code=201, dependencies=[auth.allow_user_admin]
)
def create_user(user: UserCreate, db: dbSession):
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
    user_id: Annotated[int, Path()],
    user_data: Annotated[UserUpdate, Body()],
):
    try:
        user_data.validate_data()
        updated_user = UserCrud.update_by_id(
            db=db, id=user_id, data=user_data.dict(), model_name_repr="user"
        )
    except HTTPException as e:
        raise_server_error(str(e))
    else:
        return updated_user


@router.get("/", response_model=list[UserOut], status_code=200)
def get_all_users(
    db: dbSession,
    skip: int = Query(default=0),
    limit: int = Query(default=100),
):
    try:
        users = UserCrud.get_records(db=db, skip=skip, limit=limit)
    except Exception:
        raise_server_error()
    else:
        return handle_records(records=users, records_name="users")


@router.get("/{user_id}", response_model=UserOutWithBills, status_code=200)
def get_user(
    db: dbSession,
    user_id: Annotated[int, Path()],
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
    try:
        UserCrud.delete_by_id(db=db, id=user_id)
    except Exception:
        raise_server_error()
    else:
        return {"message": "Deleted successfully"}
