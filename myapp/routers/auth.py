from jose import jwt, JWTError
from typing import Annotated
from datetime import timedelta, datetime, timezone
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from decouple import config

JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITYHM = config("JWT_ALGORITHM")

current_datetime = datetime.now(tz=timezone.utc)
expiration_time = current_datetime + timedelta(minutes=5)


class UserLogin(BaseModel):
    email: str
    password: str


class Payload(UserLogin):
    exp: int
    iat: int


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

oauth_scheme = OAuth2PasswordBearer(tokenUrl="")


def decode_token(token: Annotated[str, Depends(oauth_scheme)]) -> Payload:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITYHM])
    except JWTError:
        raise credentials_exception
    else:
        return Payload(**decoded_token.dict())
