from bcrypt import checkpw
from decouple import config
from jose import jwt, JWTError
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Response
from random import randint

from app.utils.error_utils import RaiseHttpException
from app.schema.user import UserAuthSuccess, UserOut

oauth_scheme = OAuth2PasswordBearer(tokenUrl="")


def get_timestamp_secs(date: datetime) -> int:
    return int(date.timestamp())


# JWT CONFIG
JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITYHM = config("JWT_ALGORITHM")
JWT_EXPIRES_AFTER = config("JWT_EXPIRES_AFTER")
EXPIRED_JWT_MESSAGE = "Your session has expired. Please login"
ACEESS_TOKEN_COOKIE_KEY = "exptc_jwt"

# TOKEN-COOKIE DATE-TIME CONFIG
CURRENT_UTC_TIME = datetime.utcnow()
TOKEN_EXPIRES = CURRENT_UTC_TIME + timedelta(days=int(JWT_EXPIRES_AFTER))
AUTH_COOKIE_EXPIRES = get_timestamp_secs(TOKEN_EXPIRES)
LOGOUT_COOKIE_EXPIRES = get_timestamp_secs(CURRENT_UTC_TIME + timedelta(seconds=1))


def handle_integrity_error(error_message):
    if "users_password_email_ck" in error_message:
        RaiseHttpException.bad_request(msg="Provide the email and password")

    if "users_phone_email_key" in error_message:
        RaiseHttpException.bad_request(msg="he user already exists")

    RaiseHttpException.server_error()


def otp_updated_user_info(otp: str, otp_expires: datetime):
    return {
        "mobile_otp": otp,
        "mobile_otp_expires_at": otp_expires,
    }


def generate_otp(digits_num: int = 4):
    otp_digits = [str(randint(0, 9)) for _ in range(0, digits_num)]
    otp = "".join(otp_digits)
    return otp


def create_access_token(data: dict) -> str:
    """Create a new access token"""

    to_encode = data.copy()
    to_encode.update({"exp": TOKEN_EXPIRES, "iat": CURRENT_UTC_TIME})
    access_token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITYHM)

    return access_token


def decode_access_token(access_token: str) -> dict:
    """
    Return a decoded access token\n
    Throws exception if access token is not valid or Expired
    """

    try:
        return jwt.decode(access_token, JWT_SECRET, algorithms=JWT_ALGORITYHM)

    except JWTError as e:
        if "Signature has expired" in str(e):
            RaiseHttpException.unauthorized_with_headers(msg=EXPIRED_JWT_MESSAGE)

        RaiseHttpException.unauthorized_with_headers()


def authenticate_password(plain_password: str, hashed_password: bytes):
    """
    Returns True if the user is authenticated
    Else returns False
    """

    plain_password_bytes = plain_password.encode(config("ENCODE_FMT"))
    is_valid_password = checkpw(plain_password_bytes, hashed_password)

    if not is_valid_password:
        return False

    return True


def get_auth_success_response(
    token: str, user_orm_data, message: str = "Success"
) -> UserAuthSuccess:
    return UserAuthSuccess(
        access_token=token,
        token_type="Bearer",
        message=message,
        user=UserOut.from_orm(user_orm_data),
    )


def set_cookie_header_response(response: Response, token: str):
    response.set_cookie(
        key=ACEESS_TOKEN_COOKIE_KEY,
        value=token,
        httponly=True,
        secure=True,
        max_age=AUTH_COOKIE_EXPIRES,
    )