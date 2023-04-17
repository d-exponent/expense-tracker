import re
from bcrypt import checkpw
from random import randint
from decouple import config
from fastapi import Response
from jose import jwt, JWTError
from datetime import timedelta, datetime

from app.utils.error_utils import RaiseHttpException
from app.utils.error_messages import SignupErrorMessages
from app.schema.user import UserAuthSuccess, UserOut

raise_unauthorized = RaiseHttpException.unauthorized_with_headers
raise_bad_request = RaiseHttpException.bad_request


def get_timestamp_secs(date: datetime) -> int:
    """
    Returns the timestamp of a given date as an integer
    """
    return int(date.timestamp())


# JWT CONFIG
JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITYHM = config("JWT_ALGORITHM")
JWT_EXPIRES_AFTER = config("JWT_EXPIRES_AFTER")
EXPIRED_JWT_MESSAGE = "Your session has expired. Please login"
ACEESS_TOKEN_COOKIE_KEY = config("COOKIE_KEY")

# TOKEN-COOKIE DATE-TIME CONFIG
CURRENT_UTC_TIME = datetime.utcnow()
TOKEN_EXPIRES = CURRENT_UTC_TIME + timedelta(days=int(JWT_EXPIRES_AFTER))
AUTH_COOKIE_EXPIRES = get_timestamp_secs(TOKEN_EXPIRES)
LOGOUT_COOKIE_EXPIRES = get_timestamp_secs(CURRENT_UTC_TIME + timedelta(seconds=1))


def handle_integrity_error(error_message):
    """Raises HttpException by processing the error message"""

    if "already exists" in error_message:
        raise_bad_request(SignupErrorMessages.already_exists)

    if "users_password_email_ck" in error_message:
        raise_bad_request(SignupErrorMessages.provide_credentials)

    if "users_phone_email_key" in error_message:
        raise_bad_request(SignupErrorMessages.already_exists)

    RaiseHttpException.server_error(SignupErrorMessages.server_error)


def otp_updated_user_info(otp: str, otp_expires: datetime):
    """
    Returns a dictionary for updating the db user mobile otp colums
    """
    assert isinstance(otp, str), "Otp must be a string"

    return {
        "mobile_otp": otp,
        "mobile_otp_expires_at": otp_expires,
    }


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
    match = re.match(jwt_token_regex, token)
    return bool(match)


def handle_create_token_for_user(user_data: UserOut) -> str:
    """
    Accepts a user object and handles creating a new token for that user
    """
    if not user_data.id:
        raise_unauthorized(msg="invalid user credentails")

    access_token = create_access_token({"id": user_data.id})
    return access_token


def decode_access_token(access_token: str) -> dict:
    """
    Return a decoded access token\n
    Throws exception if access token is Expired or unverified
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
            raise_unauthorized(msg="Invalid token signature")

        raise_unauthorized()


def authenticate_password(plain_password: str, hashed_password: bytes) -> bool:
    """
    Returns True if the password matches the hashed password\n
    Else returns False
    """

    password_bytes = plain_password.encode(config("ENCODE_FMT"))
    return checkpw(password_bytes, hashed_password)


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


def set_cookie_header_response(response: Response, token: str):
    """
    Handles setting the reponse cookie with token information
    """
    response.set_cookie(
        key=ACEESS_TOKEN_COOKIE_KEY,
        value=token,
        httponly=True,
        secure=True,
        max_age=AUTH_COOKIE_EXPIRES,
    )
