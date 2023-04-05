from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from fastapi import APIRouter, Body, Depends, Path, Response, HTTPException
from app.schema.user import UserOut
from app.crud.users import UserCrud
from app.utils.database import db_dependency
from app.utils.error_utils import raise_bad_request_http_error
from app.dependencies.auth import (
    create_access_token,
    authenticate_password,
    LOGIN_COOKIE_EXPIRES_AFTER,
    ACEESS_TOKEN_COOKIE_KEY,
)


router = APIRouter(prefix="/login")


def raise_404_exception(msg: str = "Not Found"):
    raise HTTPException(status_code=404, detail=msg)


class LoginSuccess(BaseModel):
    user: UserOut
    access_token: str
    token_type: str
    message: str


@router.get("/{user_id}", response_model=LoginSuccess, status_code=201)
def login(
    db: Annotated[Session, Depends(db_dependency)],
    user_id: Annotated[int, Path()],
    email: Annotated[str, Body(default=None)],
    password: Annotated[str, Body(default=None)],
    response: Response,
):
    if user_id > 0:
        user = UserCrud.get_by_id(db=db, id=user_id)
    else:
        if not all([email, password]):
            raise_bad_request_http_error(
                message="Provide the email address and password"
            )

        user = UserCrud.get_user_by_email(db, email)

        if user:
            is_authenticated = authenticate_password(
                plain_password=password, hashed_password=user.password
            )

            if not is_authenticated:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid Credentials. Provide the valid email and password",
                )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Credentials. Provide the valid email and password",
        )

    access_token = create_access_token({"id": user.id})

    response.set_cookie(
        key=ACEESS_TOKEN_COOKIE_KEY,
        value=access_token,
        httponly=True,
        secure=True,
        max_age=LOGIN_COOKIE_EXPIRES_AFTER,
    )

    return LoginSuccess(
        access_token=access_token,
        token_type="Bearer",
        user=user,
        message="Login successful",
    )


@router.put("/otp")
def auth_user_from_otp(
    db: Annotated[Session, Depends(db_dependency)],
    otp: Annotated[str, Body()],
    response: Response,
):
    user = UserCrud.get_user_by_otp(db, otp)
    if user is None:
        raise HTTPException(
            status_code=401, detail="Authentication Failure!! Invalid otp"
        )

    if datetime.utcnow() > user.mobile_otp_expires_at:
        raise HTTPException(
            status_code=401, detail="Authentication Failure!! Expired otp"
        )

    access_token = create_access_token({"id": user.id})

    response.set_cookie(
        key=ACEESS_TOKEN_COOKIE_KEY,
        value=access_token,
        httponly=True,
        secure=True,
        max_age=LOGIN_COOKIE_EXPIRES_AFTER,
    )

    return LoginSuccess(
        access_token=access_token,
        token_type="Bearer",
        user=user,
        message="Login successful",
    )
