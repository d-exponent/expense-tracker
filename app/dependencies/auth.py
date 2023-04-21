from fastapi import Request, Depends
from typing import Annotated

from app.crud.users import UserCrud
from app.schema.user import UserAllInfo
from app.utils import auth_utils as au
from app.utils.database import dbSession


def get_token_from_auth_header(request: Request):
    bearer = request.headers.get("Authorization")

    if bearer:
        # Validate the authorization header
        if bearer.startswith("Bearer") is False:
            return None

        bearer_contents = bearer.split(" ")
        if len(bearer_contents) != 2:
            return None

        return bearer_contents[1]

    return None


def get_token_from_cookies(request: Request):
    return request.cookies.get(au.ACEESS_TOKEN_COOKIE_KEY)


token_types = str | None


def get_token(
    cookie_token: Annotated[token_types, Depends(get_token_from_cookies)],
    header_token: Annotated[token_types, Depends(get_token_from_auth_header)],
):
    access_token = header_token if header_token else cookie_token

    if access_token is None:
        au.raise_unauthorized(msg="You are not logged in. Please login")

    if not au.validate_token_anatomy(token=access_token):
        au.raise_unauthorized("Invalid access token. Please Login")

    return access_token


def get_token_payload(token: Annotated[str, Depends(get_token)]):
    try:
        payload = au.decode_access_token(access_token=token)
    except Exception:
        au.raise_unauthorized("Invalid access token. Please Login")
    else:
        return payload


protect = Depends(get_token_payload)


def get_user(db: dbSession, payload: Annotated[dict, protect]) -> UserAllInfo:
    user = UserCrud.get_by_id(db, id=payload.get("id"))

    if user is None:
        au.raise_unauthorized(msg="Invalid user. Please login with valid credentials")

    if user.is_active is False:
        au.raise_unauthorized(msg="This user's profile has been deleted.")

    return user


def restrict_to(*args):
    # Check that all args are strings
    assert all(isinstance(i, str) for i in args), "All arguments must be strings"

    # Check that all args are in valid_roles list
    valid_roles = ["user", "staff", "admin"]
    assert all(i in valid_roles for i in args), "Invalid role arguments"

    def handle_restrict_to(user: Annotated[UserAllInfo, Depends(get_user)]):
        if user.role not in args:
            au.RaiseHttpException.forbidden(
                "Access Denied!! You do not have permission"
            )

        return user

    return handle_restrict_to


allow_only_user = Depends(restrict_to("user"))
allow_user_admin = Depends(restrict_to("user", "admin"))
allow_only_admin = Depends(restrict_to("admin"))
allow_only_staff = Depends(restrict_to("staff"))
