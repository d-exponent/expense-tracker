from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import APIRouter, Body, Response, Depends

from myapp.schema.user import UserOut
from myapp.utils.database import db_dependency
from myapp.utils.app_utils import remove_none_properties
from myapp.dependencies.auth import (
    UserLogin,
    create_access_token,
    authenticate_user,
    LOGIN_COOKIE_EXPIRES_AFTER,
    LOGOUT_COOKIE_EXPIRES_AFTER,
    ACEESS_TOKEN_COOKIE_KEY,
)


class LoginSuccess(BaseModel):
    user: UserOut
    access_token: str
    token_type: str
    message: str


router = APIRouter(prefix="/auth", tags=["auth", "authenticcation"])


@router.post("/login", response_model=LoginSuccess, status_code=201)
def login(
    db: Annotated[Session, Depends(db_dependency)],
    user_data: Annotated[UserLogin, Body()],
    response: Response,
):
    user_data.validate_schema()
    db_user = authenticate_user(db=db, user_data=user_data)

    user_data.id = db_user.id
    filtered_user_data = remove_none_properties(user_data.dict())
    access_token = create_access_token(filtered_user_data)

    # Send a cookie with the access token
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
        user=db_user,
        message="Login successful",
    )


@router.get("/logout")
def logout(response: Response):
    response.set_cookie(
        key=ACEESS_TOKEN_COOKIE_KEY,
        value="logged out",
        httponly=True,
        secure=True,
        max_age=LOGOUT_COOKIE_EXPIRES_AFTER,
    )

    return {"message": "Logged out successfully"}
