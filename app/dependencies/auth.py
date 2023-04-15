from fastapi import Request, Depends
from typing import Annotated

from app.crud.users import UserCrud
from app.utils.database import dbSession
from app.utils import auth_utils as au
from app.models import User as UserOrm


def get_token_from_auth_header(request: Request):
    bearer = request.headers.get("Authorization")
    invalid_bearer_token_msg = "Invalid authorization header credentials"

    if bearer:
        # Validate the authorization header
        if bearer.startswith("Bearer") is False:
            au.raise_unauthorized(msg=invalid_bearer_token_msg)

        bearer_contents = bearer.split(" ")

        if len(bearer_contents) != 2:
            au.raise_unauthorized(msg=invalid_bearer_token_msg)

        return bearer_contents[1]

    return None


def get_token_from_cookies(request: Request):
    return request.cookies.get(au.ACEESS_TOKEN_COOKIE_KEY)


def get_token(
    cookie_token: str | None = Depends(get_token_from_cookies),
    header_token: str | None = Depends(get_token_from_auth_header),
):
    access_token = header_token if header_token else cookie_token

    if access_token is None:
        au.raise_unauthorized(
            msg="Provide a valid access token via authorization header or cookie"
        )

    if not au.validate_token_anatomy(token=access_token):
        au.raise_unauthorized("Invalid access token")

    return access_token


def get_token_payload(token: Annotated[str, Depends(get_token)]):
    return au.decode_access_token(access_token=token)


def get_user(
    payload: Annotated[dict, Depends(get_token_payload)],
    db: dbSession,
):
    user: UserOrm = UserCrud.get_by_id(db, id=payload.get("id"))
    if user is None:
        au.raise_unauthorized()

    if user.is_active is False:
        au.raise_unauthorized()

    return user


def restrict_to(*args):
    valid_roles = ["user", "staff", "admin"]

    # Check that all args are strings
    assert all(isinstance(i, str) for i in args), "All arguments must be strings"

    # CHeck that all args are in valid_roles list
    assert all(i in valid_roles for i in args), "Invalid role arguments"

    def handle_restrict_to(user: Annotated[UserOrm, Depends(get_user)]):
        if user.role not in args:
            au.RaiseHttpException.forbidden(
                "Access Denied!! You do not have permission"
            )

        return user

    return handle_restrict_to
