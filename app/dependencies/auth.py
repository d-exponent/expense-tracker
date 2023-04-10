from fastapi import Request
from fastapi import Depends, Cookie
from typing import Annotated

from app.crud.users import UserCrud
from app.utils.database import dbSession
from app.utils import auth_utils as au
from app.models import User as UserOrm


def get_token_from_auth_header(request: Request):
    bearer = request.headers.get("Authorization", None)
    invalid_bearer_token_msg = "Invalid authorization header credentials"

    if bearer is None:
        return None
    else:
        # Validate the authorization header
        if bearer.startswith("Bearer") is False:
            au.raise_unauthorized(msg=invalid_bearer_token_msg)

        bearer_contents = bearer.split(" ")
        len_bearer_contents = len(bearer_contents)

        if len_bearer_contents != 2:
            au.raise_unauthorized(msg=invalid_bearer_token_msg)

        return bearer_contents[1]


def get_token(
    exptc_jwt: str = Cookie(default=None),
    token: str | None = Depends(get_token_from_auth_header),
) -> str:
    access_token = exptc_jwt if exptc_jwt else token

    au.validate_token_anatomy(token=access_token)
    return access_token


def get_payload(token: Annotated[str, Depends(get_token)]):
    return au.decode_access_token(access_token=token)


def get_user(
    payload: Annotated[dict, Depends(get_payload)],
    db: dbSession,
):
    user: UserOrm = UserCrud.get_by_id(db, id=payload.get("id"))
    if user is None:
        au.raise_unauthorized(msg="Invalid user ID")

    if user.is_active is False:
        au.RaiseHttpException.not_found()

    return user


def restrict_to(*args):
    def handle_restrict_to(user: Annotated[UserOrm, Depends(get_user)]):
        if user.role not in args:
            au.RaiseHttpException.forbidden(
                "Access Denied!! You do not have permission"
            )

        return user

    return handle_restrict_to
