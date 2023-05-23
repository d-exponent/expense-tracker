from typing import Annotated
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Path, Query, Body, Depends

from app.utils.database import dbSession
from app.utils import error_utils as eu
from app.utils.custom_exceptions import DataError

from app.crud.users import UserCrud
from app.schema import user as u
from app.schema.response import DefaultResponse
from app.dependencies import auth
from app.dependencies.user_multipart import handle_user_multipart_data_create

router = APIRouter(
    prefix="/users", tags=["users"], dependencies=[auth.current_active_user]
)

allow_admin_staff = [Depends(auth.restrict_to("admin", "staff"))]


# If the admin doesn't provide a role for the user, it will default to user i.e. role='user'
@router.post(
    "/",
    response_model=u.CreateUser,
    status_code=201,
    dependencies=allow_admin_staff,
)
def create_user(
    *,
    db: dbSession,
    user_data: Annotated[u.UserCreate, Depends(handle_user_multipart_data_create)],
):
    try:
        db_user = UserCrud.create(db=db, user=user_data)
    except IntegrityError as e:
        eu.handle_users_integrity_exception(str(e))
    else:
        return u.CreateUser(data=db_user)


@router.patch("/{id}", response_model=DefaultResponse, status_code=200)
def update_user(
    db: dbSession,
    id: Annotated[int, Path()],
    user_data: Annotated[u.UserUpdate, Body()],
):
    try:
        data = user_data.validate_data()
    except DataError as e:
        eu.RaiseHttpException.bad_request(str(e))
    else:
        updated_user = UserCrud.update_by_id(db, id, data, "user")
        return DefaultResponse(
            message="Successfully updated the user", data=updated_user
        )


@router.get(
    "/",
    response_model=u.GetUsers,
    status_code=200,
    dependencies=allow_admin_staff,
)
def get_all_users(
    db: dbSession,
    skip: int = Query(default=0),
    limit: int = Query(default=100),
):
    users = UserCrud.get_records(db=db, skip=skip, limit=limit)
    return u.GetUsers(
        message="Success", data=eu.handle_records(records=users, table_name="users")
    )


@router.get(
    "/{id}",
    response_model=u.GetUser,
    status_code=200,
    dependencies=allow_admin_staff,
)
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
            user = UserCrud.get_by_phone(db=db, phone=phone)
        else:  # Email address
            user = UserCrud.get_by_email(db=db, email=email)

    if user is None:
        eu.RaiseHttpException.not_found(msg="User not found")
    return u.GetUser(data=user)


@router.delete(
    "/{id}", status_code=204, dependencies=[Depends(auth.restrict_to("admin"))]
)
def delete_user(db: dbSession, id: Annotated[int, Path()]):
    UserCrud.delete_by_id(db=db, id=id, table="user")
    return ""
