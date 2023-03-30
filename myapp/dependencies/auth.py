from bcrypt import checkpw
from decouple import config
from typing import Annotated
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

from myapp.crud.users import UserCrud
from myapp.schema.user import UserAllInfo, UserLogin


def raise_credentials_exception(
    status_code: int = 401,
    detail: str = "Could not validate credentials",
) -> None:
    raise HTTPException(
        status_code=status_code,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_datetime_timestamp_secs(date: datetime) -> int:
    return int(date.timestamp())


# JWT CONFIG
JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITYHM = config("JWT_ALGORITHM")
JWT_EXPIRES_AFTER = config("JWT_EXPIRES_AFTER")
EXPIRED_JWT_MESSAGE = "Your session has expired. Please login"
ACEESS_TOKEN_COOKIE_KEY = "exptc_jwt"

# TOKEN-COOKIE DATE-TIME CONFIG
CURRENT_UTC_TIME = datetime.utcnow()
LOGIN_TOKEN_EXPIRES_AFTER = CURRENT_UTC_TIME + timedelta(days=int(JWT_EXPIRES_AFTER))
LOGIN_COOKIE_EXPIRES_AFTER = get_datetime_timestamp_secs(LOGIN_TOKEN_EXPIRES_AFTER)
LOGOUT_COOKIE_EXPIRES_AFTER = get_datetime_timestamp_secs(
    CURRENT_UTC_TIME + timedelta(seconds=1)
)


class TokenPayload(UserLogin):
    exp: int | float
    iat: int | float


class UserData(BaseModel):
    user: UserAllInfo
    plain_password = str


oauth_scheme = OAuth2PasswordBearer(tokenUrl="")


def create_access_token(data: dict) -> str:
    """Create a new access token"""

    to_encode = data.copy()
    del to_encode["password"]  # Just incase
    to_encode.update({"exp": LOGIN_TOKEN_EXPIRES_AFTER, "iat": CURRENT_UTC_TIME})
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
            raise_credentials_exception(detail=EXPIRED_JWT_MESSAGE)

        raise_credentials_exception()


def get_user(db: Session, user_data: UserLogin | TokenPayload) -> UserAllInfo:
    """Returns a User object from the database or None"""

    if user_data.id:
        return UserCrud.get_by_id(db=db, id=user_data.id)

    if user_data.phone:
        return UserCrud.get_user_by_phone(db=db, phone=user_data.phone)

    if user_data.email:
        return UserCrud.get_user_by_email(db=db, email=user_data.email)


def authenticate_user(db: Session, user_data: UserLogin) -> UserAllInfo:
    """
    Returns a user if the user is authenticated\n
    Throws a 401 if the user is not authenticated or None
    """

    user = get_user(db, user_data)
    if user is None:
        raise_credentials_exception(detail="Incorrect login credentials")

    password_bytes = user_data.password.encode(config("ENCODE_FMT"))
    is_valid_password = checkpw(password_bytes, user.password)

    if not is_valid_password:
        raise_credentials_exception(detail="Incorrect password")

    return UserAllInfo.from_orm(user)


# DEPENDENCIES --------------------------------
def get_token_payload(access_token: Annotated[str, Depends(oauth_scheme)]):
    """
    Returns a token payload\n
    Extracts access token from Authorization header
    """
    token_data = decode_access_token(access_token)

    return TokenPayload(**token_data)


def get_user_from_token_payload(
    db: Session,
    token_payload: Annotated[TokenPayload, Depends(get_token_payload)],
) -> UserData:
    return get_user(db, token_payload)


# def get_active_user(
#     authenticated_user: Annotated[UserAllInfo, Depends(authenticate_user)]
# ) -> UserAllInfo:
#     if not authenticated_user.is_active:
#         raise HTTPException(status_code=400, detail="Inactive user")

#     return authenticated_user
