from typing import Annotated
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Path, Query, Body, Depends

from app.dependencies import auth
from app.crud.users import UserCrud
from app.utils.database import dbSession
from app.schema import user as u
from app.schema.response import DefaultResponse
from app.utils.custom_exceptions import DataError
from app.dependencies.user_multipart import handle_user_multipart_data_create
from app.utils import error_utils as eu

router = APIRouter(prefix="/users", tags=["users"], dependencies=[auth.protect])


# If the admin doesn't provide a role for the user, it will default to user i.e. role='user'
@router.post(
    "/",
    response_model=u.CreateUser,
    status_code=201,
    dependencies=[auth.allow_only_admin],
)
def create_user(
        *,
        db: dbSession,
        role: str = Query(default='user'),
        user_data: Annotated[u.UserCreate, Depends(handle_user_multipart_data_create)]
):
    db_user = None
    try:
        user_data.role = role
        db_user = UserCrud.create(db=db, user=user_data)
    except IntegrityError as e:
        eu.handle_users_integrity_exceptions(str(e))
    return u.CreateUser(data=db_user)


@router.patch("/{id}", response_model=DefaultResponse, status_code=200)
def update_user(
        db: dbSession,
        id: Annotated[int, Path()],
        user_data: Annotated[u.UserUpdate, Body()],
):
    try:
        data = user_data.validate_data()
        updated_user = UserCrud.update_by_id(db, id, data, "user")
    except DataError as e:
        eu.RaiseHttpException.bad_request(str(e))
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
    users = UserCrud.get_records(db=db, skip=skip, limit=limit)
    records = eu.handle_records(records=users, table_name="users")
    return u.GetUsers(message="Success", data=records)


@router.get("/{id}", response_model=u.GetUser, status_code=200)
def get_user(
        db: dbSession,
        id: Annotated[int, Path()],
        phone: str = Query(regex=u.e_164_phone_regex, default=None),
        email: u.EmailStr = Query(default=None),
):
    if id > 0:
        user = UserCrud.get_by_id(db=db, id=id)
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


@router.delete("/{id}", status_code=204, dependencies=[Depends(auth.restrict_to("staff", "admin"))])
def delete_user(db: dbSession, id: Annotated[int, Path()]):
    try:
        UserCrud.delete_by_id(db=db, id=id)
    except Exception:
        if UserCrud.get_by_id(db=db, id=id) is None:
            eu.RaiseHttpException.bad_request(f"There is no user with id {id}")
        eu.RaiseHttpException.server_error()
    else:
        return "Success"
