from typing import Annotated
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter, Body, Depends, Response, Request
from app.schema.user import UserAuthSuccess, UserLoginEmailPassword
from app.crud.users import UserCrud
from app.utils.database import db_init
from app.utils import auth_utils as au


router = APIRouter(prefix="/login")


@router.post("/", response_model=UserAuthSuccess, status_code=201)
def login_with_email_password(
    db: Annotated[Session, Depends(db_init)],
    user_data: Annotated[UserLoginEmailPassword, Body()],
    response: Response,
):
    user = UserCrud.get_user_by_email(db, user_data.email_address)
    print(user)

    if user is None:
        au.raise_unauthorized(msg="Invalid email address or password")

    is_authenticated = au.authenticate_password(user_data.password, user.password)

    if not is_authenticated:
        au.raise_unauthorized(msg="Password is invalid")

    access_token = au.handle_create_token_for_user(user_data=user)

    au.set_cookie_header_response(response=response, token=access_token)

    return au.get_auth_success_response(
        token=access_token, user_orm_data=user, message="Login successful"
    )


@router.get("/user-otp")
def login_with_otp(
    db: Annotated[Session, Depends(db_init)],
    response: Response,
    request: Request,
):
    my_otp = request.headers.get("Mobile_Otp")
    user = UserCrud.get_user_by_otp(db, my_otp)

    if user is None:
        au.raise_unauthorized(msg="Invalid otp")

    current_timestamp_secs = au.get_timestamp_secs(datetime.utcnow())
    otp_expire_timestamp_secs = au.get_timestamp_secs(user.mobile_otp_expires_at)

    if current_timestamp_secs > otp_expire_timestamp_secs:
        au.raise_unauthorized(msg="Expired otp")

    to_update_data = {
        "verified": True,
        "mobile_otp": None,
        "mobile_otp_expires_at": None,
    }

    UserCrud.update_user_by_phone(db, user.phone_number, to_update_data)

    access_token = au.handle_create_token_for_user(user_data=user)
    au.set_cookie_header_response(response=response, token=access_token)

    return au.get_auth_success_response(
        token=access_token, user_orm_data=user, message="Login successful"
    )
