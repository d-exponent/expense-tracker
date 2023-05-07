from fastapi import Request, Depends
from typing import Annotated

from app.crud.users import UserCrud
from app.models import User
from app.utils import auth as au
from app.utils.database import dbSession
from app.utils.error_utils import RaiseHttpException

token_types = str | None


def get_token_from_auth_header(request: Request) -> str | None:
    """
    Retrives access token from authorization header

    Args:
        request (Request): The incoming request object

    Returns:
        access_token (string): The token if found.
        None:If there's no valid authorization header
    """

    bearer = request.headers.get("Authorization")

    if bearer is None:
        return bearer

    if not bearer.startswith("Bearer"):
        return None

    bearer_contents = bearer.split(" ")
    if len(bearer_contents) != 2:
        return None

    return bearer_contents[1]


def get_token_from_cookies(request: Request) -> str | None:
    """Retrives the access token from cookies

    Args:
        request (Request): The incoming request object.

    Returns:
        access_token (string): The access token
        None: If the token was not set on the cookie

    """
    return request.cookies.get(au.ACEESS_TOKEN_COOKIE_KEY)


def get_token(
    cookie_token: Annotated[token_types, Depends(get_token_from_cookies)],
    header_token: Annotated[token_types, Depends(get_token_from_auth_header)],
) -> str:
    """Retrives the access token from authorization header or cookie

    Returns:
        access token (string): The access token\n
        raises HttpException if there's an invalid or no token
    """
    access_token = header_token if header_token else cookie_token

    if access_token is None:
        RaiseHttpException.unauthorized_with_headers(
            msg="You are not logged in. Please login"
        )

    if not au.validate_token_anatomy(token=access_token):
        RaiseHttpException.unauthorized_with_headers(
            "Invalid access token. Please Login"
        )
    return access_token


def get_token_payload(token: Annotated[str, Depends(get_token)]):
    """
    Returns the decoded access token payload

    Args:
        token (str): The access token from get_token

    Returns:
        payload (dict): token payload
    """
    return au.handle_decode_access_token(access_token=token)


protect = Depends(get_token_payload)


def get_user(db: dbSession, payload: Annotated[dict, protect]) -> User:
    """Gets the user from the database using the access token payload

    Args:
        db (dbSession): The running db session
        payload (dict): The token payload from get_token_payload


    Returns:
        user (User): The user data from databse
    """
    user = UserCrud.get_by_id(db, id=payload.get("my_id"))

    if user is None:
        RaiseHttpException.unauthorized_with_headers(
            msg="Please login with valid credentials"
        )

    return user


def get_active_user(user: Annotated[User, Depends(get_user)]):
    """
    Returns an active user
    raise HttpException if user is Invalid
    """
    if user.is_active is False:
        RaiseHttpException.bad_request("This user's profile has been deleted")

    return user


current_active_user = Depends(get_active_user)
active_user_annontated = Annotated[User, current_active_user]


def restrict_to(*args):
    """Restricts users by roles\n
    Params:
        *args (iterable): An iterable of permitted roles
    Returns:
        user (User) : The permitted user's data from database
    """
    # Check that all args are strings
    are_strings = all(isinstance(i, str) for i in args)
    assert are_strings, "All arguments must be strings"

    # Check that all args are in valid_roles list
    valid_roles = ["user", "staff", "admin"]
    assert all(i in valid_roles for i in args), "Invalid role arguments"

    def handle_restrict_to(user: Annotated[User, current_active_user]):
        if user.role not in args:
            au.RaiseHttpException.forbidden(
                "Access Denied!! You do not have permission"
            )

        return user

    return handle_restrict_to
