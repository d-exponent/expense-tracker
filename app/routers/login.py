from typing import Annotated
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import APIRouter, Body, Depends, Response, Request
from app.schema.user import UserAuthSuccess
from app.utils.error_utils import RaiseHttpException
from app.crud.users import UserCrud
from app.utils.database import db_init
from app.utils import auth_utils as au


router = APIRouter(prefix="/login")


@router.post("/", response_model=UserAuthSuccess, status_code=201)
def login_with_email_password(
    db: Annotated[Session, Depends(db_init)],
    email: Annotated[str, Body()],
    password: Annotated[str, Body()],
    response: Response,
):
    user = UserCrud.get_user_by_email(db, email)

    if user is None:
        RaiseHttpException.unauthorized(msg="Invalid email address or password")

    is_authenticated = au.authenticate_password(password, user.password)
    if not is_authenticated:
        RaiseHttpException.unauthorized(msg="Password is invalid")

    access_token = au.create_access_token({"user_id": user.id})
    au.set_cookie_header_response(response=response, token=access_token)

    return au.get_auth_success_response(
        token=access_token, user_orm_data=user, message="Login successful"
    )


@router.get("/otp")
def validate_user_otp(
    db: Annotated[Session, Depends(db_init)],
    response: Response,
    request: Request,
):
    my_otp = request.headers.get("Mobile_Otp")
    user = UserCrud.get_user_by_otp(db, my_otp)

    if user is None:
        RaiseHttpException.unauthorized(msg="Invalid otp")

    current_timestamp_secs = au.get_timestamp_secs(datetime.utcnow())
    otp_expire_timestamp_secs = au.get_timestamp_secs(user.mobile_otp_expires_at)

    if current_timestamp_secs > otp_expire_timestamp_secs:
        RaiseHttpException.unauthorized(msg="Expired otp")

    to_update_data = {
        "verified": True,
        "mobile_otp": None,
        "mobile_otp_expires_at": None,
    }

    UserCrud.update_user_by_phone(db, user.phone_number, to_update_data)

    access_token = au.create_access_token({"user_id": user.id})
    au.set_cookie_header_response(response=response, token=access_token)

    return au.get_auth_success_response(
        token=access_token, user_orm_data=user, message="Login successful"
    )
