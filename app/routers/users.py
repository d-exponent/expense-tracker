from typing import Annotated
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, HTTPException, Path, Query, Body

from app.crud.users import UserCrud
from app.utils.database import dbSession
from app.schema import user as u
from app.schema.response import DefaultResponse
from app.utils import error_utils as eu
from app.dependencies import auth


router = APIRouter(prefix="/users", tags=["users"], dependencies=[auth.protect])


@router.post(
    "/",
    response_model=u.CreateUser,
    status_code=201,
    dependencies=[auth.allow_only_admin],
)
def create_user(db: dbSession, user: Annotated[u.UserCreate, Body()]):
    try:
        user = UserCrud.create(db, user)
    except IntegrityError as e:
        eu.handle_create_user_integrity_exception(str(e))
    except Exception:
        eu.RaiseHttpException.server_error()

    return u.CreateUser(data=user)


@router.patch("/{user_id}", response_model=DefaultResponse, status_code=200)
def update_user(
    db: dbSession,
    user_id: Annotated[int, Path()],
    user_data: Annotated[u.UserUpdate, Body()],
):
    try:
        data = user_data.validate_data()
        updated_user = UserCrud.update_by_id(db, user_id, data, "user")
    except HTTPException as e:
        eu.RaiseHttpException.server_error(str(e))
    else:
        return DefaultResponse(
            message="Successfully updated the user", data=updated_user
        )


@router.get("/", response_model=u.GetUsers, status_code=200)
def get_all_users(
    db: dbSession,
    skip: int = Query(default=0),
    limit: int = Query(default=100),
):
    try:
        users = UserCrud.get_records(db=db, skip=skip, limit=limit)
    except Exception:
        eu.RaiseHttpException.server_error()
    else:
        records = eu.handle_records(records=users, table_name="users")
        return u.GetUsers(message="Success", data=records)


@router.get("/{user_id}", response_model=u.GetUser, status_code=200)
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
            eu.RaiseHttpException.bad_request(
                "Provide the user's phone number or email address"
            )

        if phone:
            user = UserCrud.get_user_by_phone(db=db, phone=phone)
        else:  # Email address
            user = UserCrud.get_user_by_email(db=db, email=email)

    if user is None:
        eu.RaiseHttpException.not_found(msg="User not found")

    return u.GetUser(data=user)


@router.delete("/{user_id}", status_code=204)
def delete_user(db: dbSession, user_id: Annotated[int, Path()]):
    try:
        UserCrud.delete_by_id(db=db, id=user_id)
    except Exception:
        if UserCrud.get_by_id(db=db, id=user_id) is None:
            eu.RaiseHttpException.bad_request(f"There is no user with id {user_id}")
        eu.RaiseHttpException.server_error()
    else:
        return "Success"
