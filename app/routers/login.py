from typing import Annotated
from fastapi import APIRouter, Body, Response, Request

from app.utils import error_messages as em
from app.crud.users import UserCrud
from app.schema import user as u
from app.utils.database import dbSession
from app.utils import auth as au


router = APIRouter(prefix="/login")
invalidCred = em.InvalidCredentials


@router.post("/", response_model=u.UserAuthSuccess, status_code=201)
def login_with_email_password(
    db: dbSession,
    user_data: Annotated[u.UserLoginEmailPassword, Body()],
    response: Response,
):
    """Authenticates and returns a user's email and password

    - **email**: The user's registered email address
    - **password**: The user's registered password

    Returns the userdata and access token

    """

    user = UserCrud.get_user_by_email(db, user_data.email)
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


@router.get("/otp")
def login_with_otp(db: dbSession, response: Response, request: Request):
    """
    Get a user from the otp passed from request header
    - **Request Header Format** =>  key: (User-Otp), value: (otp)

    Returns the user data and access token
    """
    otp = request.headers.get("User-Otp")
    user = au.handle_get_user_by_otp(db, otp)
    au.check_otp_expired(user.otp_expires_at)

    to_update = au.set_otp_columns_data(verified=True)
    UserCrud.update_user_by_phone(db, user.phone, to_update)
    access_token = au.handle_create_token_for_user(user_data=user)

    au.set_cookie_header_response(response=response, token=access_token)
    return au.get_auth_success_response(
        token=access_token, user_orm_data=user, message="Login successful"
    )
