import bcrypt
from decouple import config
from typing import Annotated
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from myapp.crud.users import UserCrud
from myapp.schema.user import UserAllInfo
from myapp.utils.database import db_dependency


JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITYHM = config("JWT_ALGORITHM")
JWT_EXPIRES_AFTER = config("JWT_EXPIRES_AFTER")

CURRENT_UTC_TIME = datetime.utcnow()
EXPIRED_JWT_MESSAGE = "Your session has expired. Please login"


class UserLogin(BaseModel):
    id: int | None
    email: EmailStr | None
    phone: str | None
    password: str


class Payload(UserLogin):
    exp: int | float
    iat: int | float


def raise_credentials_exception(
    status_code: int = status.HTTP_401_UNAUTHORIZED,
    detail: str = "Could not validate credentials",
) -> None:
    raise HTTPException(
        status_code=status_code,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


oauth_scheme = OAuth2PasswordBearer(tokenUrl="")


def create_access_token(payload: dict, expires_delta: timedelta | None) -> str:
    to_encode = payload.copy()

    if expires_delta:
        expire_utc_time = CURRENT_UTC_TIME + expires_delta
    else:
        expire_utc_time = CURRENT_UTC_TIME + timedelta(days=JWT_EXPIRES_AFTER)

    to_encode.update({"exp": expire_utc_time, "iat": CURRENT_UTC_TIME})
    access_token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITYHM)

    return access_token


def decode_access_token(token: Annotated[str, Depends(oauth_scheme)]) -> Payload:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITYHM)
    except JWTError as e:
        if "Signature has expired" in str(e):
            raise_credentials_exception(detail=EXPIRED_JWT_MESSAGE)

        raise_credentials_exception()
    else:
        return Payload(**payload.dict())


def authenticate_user(
    db: Annotated[Session, Depends(db_dependency)],
    payload: Annotated[Payload, Depends(decode_access_token)],
) -> UserAllInfo:
    # Check that a phone number or email address is available
    if not any(payload.id, payload.phone, payload.email):
        raise_credentials_exception(
            detail="Provide the password AND phone number Or email address",
        )

    is_none = lambda x: False if x else True
    user = None

    # Check for the user in our database
    if payload.id:
        user = UserCrud.get_by_id(db=db, id=payload.id)

    if is_none(user) and payload.phone:
        user = UserCrud.get_user_by_phone(db=db, phone=payload.phone)

    if is_none(user) and payload.email:
        user = UserCrud.get_user_by_email(db=db, email=payload.email)

    if is_none(user):
        raise_credentials_exception(
            detail="User Does Not Exist", status_code=status.HTTP_404_NOT_FOUND
        )

    # Validate the user's password
    is_valid_password = bcrypt.checkpw(payload.password, user.password)
    if not is_valid_password:
        raise_credentials_exception(detail="Invalid password. Try again")

    return user
