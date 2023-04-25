from typing import Annotated
from datetime import datetime
from fastapi import APIRouter, Body, Response, Request


from app.utils import error_messages as em
from app.schema.user import UserAuthSuccess, UserLoginEmailPassword
from app.crud.users import UserCrud
from app.utils.database import dbSession
from app.utils import auth_utils as au


router = APIRouter(prefix="/login")
invalidCred = em.InvalidCredentials


@router.post("/", response_model=UserAuthSuccess, status_code=201)
def login_with_email_password(
    db: dbSession,
    user_data: Annotated[UserLoginEmailPassword, Body()],
    response: Response,
):
    user = UserCrud.get_user_by_email(db, user_data.email_address)
    if user is None:
        au.raise_unauthorized(invalidCred.email_password_required)

    is_authenticated = au.authenticate_password(user_data.password, user.password)
    if not is_authenticated:
        au.raise_unauthorized(invalidCred.invalid_password)

    access_token = au.handle_create_token_for_user(user_data=user)
    au.set_cookie_header_response(response=response, token=access_token)
    return au.get_auth_success_response(
        token=access_token, user_orm_data=user, message="Login successful"
    )


@router.get("/user-otp")
def login_with_otp(db: dbSession, response: Response, request: Request):
    my_otp = request.headers.get("User_Otp")
    if my_otp is None:
        au.raise_bad_request("Provide the one-time password for the user")

    user = UserCrud.get_user_by_otp(db, my_otp)
    if user is None:
        au.raise_unauthorized(invalidCred.invalid_otp)

    current_timestamp_secs = au.get_timestamp_secs(datetime.utcnow())
    otp_expire_timestamp_secs = au.get_timestamp_secs(user.otp_expires_at)

    if current_timestamp_secs > otp_expire_timestamp_secs:
        au.raise_unauthorized(invalidCred.expired_otp)

    update_data = au.config_users_otp_columns(verified=True)
    UserCrud.update_user_by_phone(db, user.phone_number, update_data)
    access_token = au.handle_create_token_for_user(user_data=user)

    au.set_cookie_header_response(response=response, token=access_token)
    return au.get_auth_success_response(
        token=access_token, user_orm_data=user, message="Login successful"
    )
