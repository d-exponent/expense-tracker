from typing import Annotated
import asyncio
from sqlalchemy.exc import IntegrityError
from pydantic import EmailStr
from fastapi import APIRouter, Response, Depends, Query, Request

from app.routers import login
from app.crud.users import UserCrud
from app.schema import user as u
from app.schema.response import DefaultResponse
from app.features.sms import SMSMessenger, SendSmsError
from app.features.send_email import EmailMessenger, SendEmailError

from app.dependencies.auth import current_active_user
from app.dependencies import user_multipart as um
from app.utils import auth as au
from app.utils import error_utils as eu
from app.utils.database import dbSession
from app.utils import error_messages as em
from app.utils.general import add_minutes, get_user_full_name, to_bool_to_int

router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(login.router)


@router.post("/signup", status_code=201, response_model=u.UserAuthSuccess)
async def sign_up_user(
    db: dbSession,
    user: Annotated[u.UserCreate, Depends(um.handle_user_multipart_data_create)],
    response: Response,
):
    """Registers a new user and stores the profile image if any
    - **role**: Persited to 'user' on this route so it can be ommited from multipart form
    """

    # Only the admin or staff can create a user with a different role.
    user.role = "user"
    user_data = user.__dict__
    user_otp = au.generate_otp(5)
    update_data = au.set_otp_columns_data(user_otp, add_minutes(minutes=10))
    user_data.update(update_data)

    try:
        db_user = UserCrud.create(db=db, user=u.UserSignUp(**user_data))
    except IntegrityError as e:
        eu.handle_create_user_integrity_exception(str(e))

    user_full_name = get_user_full_name(db_user)
    email_success = True
    sms_success = True
    tasks = [
        EmailMessenger(db_user.email, user_full_name).send_welcome(user_otp),
        SMSMessenger(db_user.phone, user_full_name).send_welcome(user_otp),
    ]

    for task in asyncio.as_completed(tasks):
        try:
            await task
        except SendSmsError:
            sms_success = False
        except SendEmailError:
            email_success = False

    access_token = au.handle_create_token_for_user(db_user)
    au.set_cookie_header_response(response, access_token)
    res_msg = au.signup_response_msg(sms_success, email_success)

    return au.get_auth_success_response(access_token, db_user, res_msg)


@router.get("/access-code", response_model=DefaultResponse)
async def get_access_code(
    db: dbSession,
    request: Request,
    phone: str = Query(default=None),
    email: EmailStr = Query(default=None),
):
    """Send one time password (access-code) to the user's phone number or email address

    - **phone** : The user's registered phone number
    - **email**: The user's registered email address

    **REQUEST HEADER**
    - **Update-Email** : Set to "YES" to customize the email message for update email operation.
    """

    # Ensure only a phone or an email is processed, never both, never none.
    if to_bool_to_int(phone) + to_bool_to_int(email) != 1:
        msg = "Provide either a phone or an email via url query"
        eu.RaiseHttpException.bad_request(msg)

    if phone:
        phone_number = "+" + phone if "+" not in phone else phone

        if not au.validate_phone_number(phone=phone_number):
            eu.RaiseHttpException.bad_request("Provide a valid phone number")

        db_user = UserCrud.get_by_phone(db, phone=phone_number)
    else:
        db_user = UserCrud.get_by_email(db, email)

    if db_user is None:
        eu.RaiseHttpException.not_found("The user does not exist in our records")

    otp = au.generate_otp(5)
    to_update = au.set_otp_columns_data(otp, add_minutes())
    UserCrud.update_user_by_phone(db, db_user.phone, to_update)
    user_full_name = get_user_full_name(db_user)
    receiver = None

    if phone:
        try:
            await SMSMessenger(db_user.phone, user_full_name).send_otp(otp)
            receiver = db_user.phone

        except SendSmsError:
            msg = em.GetMobileOtpErrorMessages.otp_send_error
            eu.RaiseHttpException.server_error(msg)
    else:
        try:
            email_handler = EmailMessenger(db_user.email, user_full_name)
            if request.headers.get("Update-Email") == "YES":
                await email_handler.send_update_email_otp(otp)
            else:
                await email_handler.send_login(otp)

            receiver = db_user.email
        except SendEmailError:
            eu.RaiseHttpException.server_error("Error sending Otp to email address")

    return DefaultResponse(
        message=f"The One Time Password has been successfully sent to {receiver}"
    )


@router.patch(
    "/credentials", response_model=DefaultResponse, dependencies=[current_active_user]
)
def update_phone_email(
    db: dbSession,
    request: Request,
    phone: str = Query(default=None, regex=u.e_164_phone_regex),
    email: EmailStr = Query(default=None),
):
    """
    User can update either of or both phone and email
    If the email and/or phone provided is the same as already in the database, no changes will be made
    -- **Access-Code**: Header must be set with the otp received by the user from auth/get_otp route.
    """

    if phone is None and email is None:
        msg = "Provide either a phone number or an email address to be updated"
        eu.RaiseHttpException.bad_request(msg)

    user = au.handle_get_user_by_otp(db, otp=request.headers.get("Access-Code"))
    au.check_otp_expired(user.otp_expires_at)

    # Ensure credentials to be updated are not the same as already in database
    # No need to query the db when we don't have to
    credentials_to_update = {}
    if phone and (user.phone == phone):
        msg = "The phone number is the user's current phone number"
        eu.RaiseHttpException.bad_request(msg)

    elif email and (user.email == email):
        msg = "The email address is the user's current email address"
        eu.RaiseHttpException.bad_request(msg)

    else:
        phone and credentials_to_update.update({"phone": phone})
        email and credentials_to_update.update({"email": email})

    to_update = au.handle_credentials_to_update_config(credentials_to_update)
    try:
        UserCrud.update_user_by_phone(db, user.phone, to_update)
    except IntegrityError as e:
        eu.handle_create_user_integrity_exception(str(e))
    else:
        return DefaultResponse(message=au.update_credentials_response_msg(phone, email))


@router.get(
    "/logout", dependencies=[current_active_user], response_model=DefaultResponse
)
def logout(response: Response):
    """Logs out the current user"""
    token = "logged out"

    au.set_cookie_header_response(
        response, token=token, max_age=au.LOGOUT_COOKIE_EXPIRES
    )

    return au.get_auth_success_response(token, message="Logged out successfully")
