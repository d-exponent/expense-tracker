import re
from bcrypt import checkpw
from random import randint
from fastapi import Response
from jose import jwt, JWTError
from datetime import timedelta, datetime

from app.utils.error_utils import RaiseHttpException
from app.schema.user import UserAuthSuccess, UserOut
from app.utils.database import Session
from app.settings import settings

raise_unauthorized = RaiseHttpException.unauthorized_with_headers
raise_bad_request = RaiseHttpException.bad_request


def get_timestamp_secs(date: datetime) -> int:
    """
    Returns the timestamp of a given date as an integer
    """
    return int(date.timestamp())


# JWT CONFIG
JWT_SECRET = settings.jwt_secret
JWT_ALGORITYHM = settings.jwt_algorithm
JWT_EXPIRES_AFTER = settings.jwt_expires_after
ACEESS_TOKEN_COOKIE_KEY = settings.cookie_key
EXPIRED_JWT_MESSAGE = "Your session has expired. Please login"

# TOKEN-COOKIE DATE-TIME CONFIG
CURRENT_UTC_TIME = datetime.utcnow()
TOKEN_EXPIRES = CURRENT_UTC_TIME + timedelta(days=JWT_EXPIRES_AFTER)
AUTH_COOKIE_EXPIRES = get_timestamp_secs(TOKEN_EXPIRES)
LOGOUT_COOKIE_EXPIRES = get_timestamp_secs(CURRENT_UTC_TIME + timedelta(seconds=1))


def set_otp_columns_data(
        otp: str = None, otp_expires: datetime = None, verified: bool = False
) -> dict:
    """
    Returns a dictionary for updating the db user's otp columns
    """
    otp_expires_is_date = isinstance(otp_expires, datetime)
    verified_is_bool = isinstance(verified, bool)
    assert otp is None or isinstance(otp, str), "otp must be a string"
    assert otp_expires is None or otp_expires_is_date, "otp_expires must be a datetime"
    assert verified is None or verified_is_bool, "verified must be a boolean"

    return {"otp": otp, "otp_expires_at": otp_expires, "verified": verified}


def generate_otp(num_of_digits: int = 4):
    """
    Returns a random sequence of positive integers\n
    The length of the sequence defaults to 4
    """
    otp_digits = [str(randint(0, 9)) for _ in range(0, num_of_digits)]
    return "".join(otp_digits)


def create_access_token(data: dict) -> str:
    """Create a new access token"""
    assert isinstance(data, dict), "data must be a dict"

    to_encode = data.copy()
    to_encode.update({"exp": TOKEN_EXPIRES, "iat": CURRENT_UTC_TIME})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITYHM)


def validate_token_anatomy(token: str) -> bool:
    """
    Returns True if the token matches the jwt token anatomy\n
    Else returns False
    """
    jwt_token_regex = "^[A-Za-z0-9_-]{2,}(?:\\.[A-Za-z0-9_-]{2,}){2}$"
    return bool(re.fullmatch(jwt_token_regex, token))


def handle_create_token_for_user(user_data: UserOut) -> str:
    """
    Accepts a user object and handles creating a new token for that user
    """
    if not user_data.id:
        raise_unauthorized(msg="invalid user credentails")
    return create_access_token({"id": user_data.id})


def handle_decode_access_token(access_token: str) -> dict:
    """
    Return a decoded access token
    """
    if not validate_token_anatomy(access_token):
        raise_unauthorized(msg="Invalid access token")

    try:
        return jwt.decode(access_token, JWT_SECRET, algorithms=JWT_ALGORITYHM)
    except JWTError as e:
        error_msg = str(e)
        if "Signature has expired" in error_msg:
            raise_unauthorized(msg=EXPIRED_JWT_MESSAGE)

        if "Signature verification failed" in error_msg:
            raise_unauthorized(msg="Invalid access token")

        raise_unauthorized()


def authenticate_password(plain_password: str, hashed_password: bytes) -> bool:
    """
    Returns True if the password matches the hashed password\n
    Else returns False
    """
    return checkpw(plain_password.encode("utf-8"), hashed_password)


def handle_get_user_by_otp(db: Session, otp: str):
    from app.crud.users import UserCrud  # Circular Import issues
    if otp is None:
        RaiseHttpException.bad_request("Provide the user's otp")

    user = UserCrud.get_user_by_otp(db, otp)
    if user is None:
        RaiseHttpException.unauthorized_with_headers("Invalid Otp")

    return user


def check_otp_expired(otp_exp_time: datetime):
    # Get datetime as timestamps
    current_timestamp = get_timestamp_secs(datetime.utcnow())
    otp_expire_timestamp = get_timestamp_secs(otp_exp_time)

    # Raise HttpException is otp has expired.
    if current_timestamp > otp_expire_timestamp:
        RaiseHttpException.bad_request("The one time password (otp) has expired")


def get_auth_success_response(token: str, user_orm_data, message: str = "Success"):
    """
    Creates and returns an auth response for the given user and the token
    """
    return UserAuthSuccess(
        access_token=token,
        token_type="Bearer",
        message=message,
        user=UserOut.from_orm(user_orm_data),
    )


def set_cookie_header_response(response: Response, token: str, max_age: datetime | int = None):
    """
    Handles setting the response cookie with token information
    """
    if max_age is None:
        max_age = AUTH_COOKIE_EXPIRES

    response.set_cookie(
        key=ACEESS_TOKEN_COOKIE_KEY,
        value=token,
        httponly=True,
        secure=True,
        max_age=max_age,
    )
