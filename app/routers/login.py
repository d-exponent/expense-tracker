from typing import Annotated
from fastapi import APIRouter, Body, Response, Path

from app.schema import user as u
from app.crud.users import UserCrud

from app.utils import error_messages as em
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

    user = UserCrud.get_by_email(db, user_data.email)
    if user is None:
        au.RaiseHttpException.unauthorized_with_headers(
            invalidCred.email_password_required
        )

    is_authenticated = au.authenticate_password(user_data.password, user.password)
    if not is_authenticated:
        au.RaiseHttpException.unauthorized_with_headers(invalidCred.invalid_password)

    access_token = au.handle_create_token_for_user(user_data=user)
    au.set_cookie_header_response(response=response, token=access_token)
    return au.get_auth_success_response(
        token=access_token, user_orm_data=user, message="Login successful"
    )


@router.get("/access-code/{code}")
def login_with_access_code(
    *,
    db: dbSession,
    code: Annotated[str, Path()],
    response: Response,
):
    """
    Login a user from the access_code passed from request header

    Returns the user data and access token
    """
    user = au.handle_get_user_by_otp(db, otp=code)
    au.check_otp_expired(user.otp_expires_at)

    to_update = au.set_otp_columns_data(verified=True)
    UserCrud.update_user_by_phone(db, user.phone, to_update)
    access_token = au.handle_create_token_for_user(user)

    au.set_cookie_header_response(response=response, token=access_token)
    return au.get_auth_success_response(
        token=access_token, user_orm_data=user, message="Login successful"
    )
