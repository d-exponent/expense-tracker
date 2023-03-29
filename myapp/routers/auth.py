from typing import Annotated
from fastapi import APIRouter, Body, Response, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from myapp.models import Base
from myapp.schema.user import UserOut
from myapp.database.sqlalchemy_config import engine
from myapp.utils.database import db_dependency
from myapp.dependencies.auth import (
    UserLogin,
    create_access_token,
    TokenPayload,
    authenticate_user,
    raise_credentials_exception,
)
from myapp.utils.app_utils import remove_none_properties


def validate_user_login_data(user: UserLogin) -> None:
    if not any([user.email, user.phone, user.id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide the email address or phone number or id of the user",
        )


class LoginOut(BaseModel):
    user: UserOut
    access_token: str
    token_type: str


Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/auth", tags=["auth", "authenticcation"])


@router.post("/login", response_model=LoginOut, status_code=201)
def login(
    db: Annotated[Session, Depends(db_dependency)],
    user_data: Annotated[UserLogin, Body()],
):
    validate_user_login_data(user_data)

    db_user = authenticate_user(db=db, user_data=user_data)

    if not db_user:
        raise_credentials_exception(detail="Incorrect credentials")

    # Don't want to overload our token with empty properties
    filtered_user_data = remove_none_properties(user_data.dict())
    access_token = create_access_token(filtered_user_data)

    return LoginOut(access_token=access_token, token_type="Bearer", user=db_user)
