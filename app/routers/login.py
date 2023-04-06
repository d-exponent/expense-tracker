from typing import Annotated
import pytz
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone
from fastapi import APIRouter, Body, Depends, Path, Response, HTTPException
from app.schema.user import UserAuthSuccess
from app.crud.users import UserCrud
from app.utils.database import db_dependency
from app.utils.error_utils import raise_bad_request_http_error
from app.utils.auth_utils import (
    create_access_token,
    authenticate_password,
    set_cookie_header_response,
    get_auth_success_response,
    get_timestamp_secs,
)


router = APIRouter(prefix="/login")


@router.post("/", response_model=UserAuthSuccess, status_code=201)
def login_with_email_password(
    db: Annotated[Session, Depends(db_dependency)],
    email: Annotated[str, Body()],
    password: Annotated[str, Body()],
    response: Response,
):
    user = UserCrud.get_user_by_email(db, email)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Credentials. Provide the valid email and password",
        )

    is_authenticated = authenticate_password(password, user.password)

    if not is_authenticated:
        raise HTTPException(
            status_code=401,
            detail="Invalid Credentials. Provide the valid email and password",
        )

    access_token = create_access_token({"user_id": user.id})

    set_cookie_header_response(response=response, token=access_token)

    return get_auth_success_response(
        token=access_token, user_orm_data=user, message="Login successful"
    )


class UserLoginOtp(BaseModel):
    otp: str


@router.put("/otp")
def validate_user_otp(
    db: Annotated[Session, Depends(db_dependency)],
    user_otp: Annotated[UserLoginOtp, Body()],
    response: Response,
):
    user = UserCrud.get_user_by_otp(db, user_otp.otp)

    if user is None:
        raise HTTPException(
            status_code=401, detail="Authentication Failure!! Invalid otp"
        )

    current_timestamp_secs = get_timestamp_secs(datetime.utcnow())
    otp_expire_timestamp_secs = get_timestamp_secs(user.mobile_otp_expires_at)

    if current_timestamp_secs > otp_expire_timestamp_secs:
        raise HTTPException(
            status_code=401, detail="Authentication Failure!! Expired otp"
        )

    UserCrud.update_user_by_phone(
        db=db,
        phone=user.phone_number,
        update_data={
            "verified": True,
            "mobile_otp": None,
            "mobile_otp_expires_at": None,
        },
    )

    access_token = create_access_token({"user_id": user.id})

    set_cookie_header_response(response=response, token=access_token)

    return get_auth_success_response(
        token=access_token, user_orm_data=user, message="Login successful"
    )
