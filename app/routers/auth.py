from typing import Annotated
from sqlalchemy.exc import IntegrityError
import re
from fastapi import APIRouter, Response, Body, Depends, Query, Request

from app.routers import login, me
from app.crud.users import UserCrud
from app.dependencies.auth import protect, get_user, User as UserOrm
from app.dependencies.user_multipart import handle_user_multipart_data_create
from app.schema import user as u
from app.schema.response import DefaultResponse

from app.utils import auth as au
from app.utils.sms import SMSMessenger, SendSmsError
from app.utils.send_email import EmailMessenger, SendEmailError
from app.utils.database import dbSession
from app.utils.general import AddTime, get_user_full_name
from app.utils import error_utils as eu
from app.utils import error_messages as em

router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(me.router)
router.include_router(login.router)


def get_credentials_to_update(data: dict):
    update_data = au.set_otp_columns_data(verified=True)
    update_data.update(data)
    return update_data


def get_update_credentials_response_msg(phone: str = None, email: str = None):
    if phone and email:
        res_msg = "The phone number and email are updated successfully"
    elif phone:
        res_msg = "The  phone number is updated successfully."
    else:
        res_msg = "The email address is updated successfully"
    return res_msg


# Implementing temporary response message generator. Will be removed When twillo is setup
def get_signup_response_msg(sms_sent: str = None, email_sent: str = None) -> str:
    all_sent = all([sms_sent, email_sent])
    response_msg = "Your account has been successfully created."

    if all_sent:
        return f"{response_msg} otp was sent to your phone number and email address."
    elif sms_sent:
        return f"{response_msg} otp was sent to your registered phone number."
    elif email_sent:
        return f"{response_msg} otp was sent to your registered email address."
    return response_msg


@router.post("/signup", status_code=201, response_model=u.UserAuthSuccess)
async def sign_up(
        db: dbSession,
        user: Annotated[u.UserCreate, Depends(handle_user_multipart_data_create)],
        response: Response,
):
    """Registers a new user and stores the profile image if any
    - **role**: Defaults to user on this route irrespective of value provided.
    """
    user.role = 'user'  # Only the admin can create a user with a different role.
    user_data = user.dict().copy()
    user_otp = au.generate_otp(5)
    update_data = au.set_otp_columns_data(user_otp, AddTime.add_minutes(mins=5))
    user_data.update(update_data)

    db_user = None
    try:
        db_user = UserCrud.create(db=db, user=u.UserSignUp(**user_data))
    except IntegrityError as e:
        eu.handle_users_integrity_exceptions(str(e))

    # TEMPORARY RESPONSE IMPLEMENTATION
    # Twillo account is temporarily down. A better implementation using asyncio.gather..
    # ...will be implemented for a faster two-way messaging
    email_success = None
    sms_success = None
    user_full_name = get_user_full_name(db_user)
    try:
        await EmailMessenger(
            receiver_name=user_full_name, receiver_email=db_user.email
        ).send_welcome(user_otp)
        email_success = True
    except SendEmailError:
        pass

    try:
        sms_messenger = SMSMessenger(
            receiver_name=user_full_name, receiver_phone=db_user.phone
        )
        await sms_messenger.send_welcome(user_otp)
        sms_success = True
    except SendSmsError:
        pass

    access_token = au.handle_create_token_for_user(user_data=db_user)
    au.set_cookie_header_response(response=response, token=access_token)

    return au.get_auth_success_response(
        token=access_token,
        user_orm_data=db_user,
        message=get_signup_response_msg(sms_success, email_success)
    )


@router.get("/get-otp", response_model=DefaultResponse)
async def get_otp(
        db: dbSession,
        request: Request,
        phone: str = Query(default=None),
        email: u.EmailStr = Query(default=None),
):
    """Send one time password to the user's phone number or email address

    - **phone** : The user's registered phone number
    - **email**: The user's registered email address

    **REQUEST HEADER**
    - **Update-Email** : Set to "YES" to customize the email message if the otp is meant for an update email operation.

    """

    # Ensure only a phone or an email is processed, never both, never none.
    if (phone is None and email is None) or (phone and email):
        eu.RaiseHttpException.bad_request("Provide either a phone or an email")

    if phone:
        db_user = UserCrud.get_user_by_phone(db, phone="+" + phone.strip())
    else:
        db_user = UserCrud.get_user_by_email(db, email)

    if db_user is None:
        eu.RaiseHttpException.not_found("The user does not exist in our records")

    otp_data = au.set_otp_columns_data(au.generate_otp(5), AddTime.add_minutes(3))
    UserCrud.update_user_by_phone(db, db_user.phone, otp_data)
    user_full_name = get_user_full_name(db_user)
    receiver = None

    otp = otp_data.get("otp")
    if phone:
        try:
            await SMSMessenger(
                receiver_name=user_full_name, receiver_phone=db_user.phone
            ).send_otp(otp)
            receiver = db_user.phone
        except SendSmsError:
            eu.RaiseHttpException.server_error(
                em.GetMobileOtpErrorMessages.otp_send_error
            )
    else:
        try:
            email_handler = EmailMessenger(
                receiver_email=db_user.email, receiver_name=user_full_name
            )

            if request.headers.get("Update-Email") == "YES":
                await email_handler.send_update_email_otp(otp)
            else:
                await email_handler.send_login(otp)
            receiver = db_user.email
        except SendEmailError:
            eu.RaiseHttpException.server_error("Error sending Otp to email address")

    res_msg = f"The One Time Password has been successfully sent to {receiver}"
    return DefaultResponse(message=res_msg)


@router.patch("/credentials", response_model=DefaultResponse)
def update_phone_email(
        db: dbSession,
        request: Request,
        phone: str = Query(default=None, regex=u.e_164_phone_regex),
        email: u.EmailStr = Query(default=None),
):
    """
    User can update either of or both phone and email
    If the email and/or phone provided is the same as already in the database, no changes will be made
    -- **User-Otp**: Header must be set with the otp received by the user from auth/get_otp route.
    """

    if phone is None and email is None:
        eu.RaiseHttpException.bad_request(
            "Provide either a phone number or an email to be updated"
        )

    user = au.handle_get_user_by_otp(db, otp=request.headers.get("User-Otp"))
    au.check_otp_expired(user.otp_expires_at)

    credentials_to_update = {}
    phone and (phone != user.phone) and credentials_to_update.update({"phone": phone})
    email and (email != user.email) and credentials_to_update.update({"email": email})
    to_update = get_credentials_to_update(credentials_to_update)

    try:
        UserCrud.update_user_by_phone(db, user.phone, to_update)
    except IntegrityError as e:
        eu.handle_users_integrity_exceptions(str(e))
    return DefaultResponse(message=get_update_credentials_response_msg(phone, email))


@router.patch("/password", response_model=DefaultResponse)
def update_password(
        db: dbSession,
        credentials: Annotated[u.UserUpdatePassword, Body()],
        db_user: Annotated[UserOrm, Depends(get_user)],
):
    """Updates only the user password
    - **password**: The current password
    - **new_password**: The new password
    - **new_password_confirm**: Same as the **new_password**
    """

    if credentials.new_password != credentials.new_password_confirm:
        eu.RaiseHttpException.bad_request("The passwords do not match")

    # Ensure the password is correct
    if not db_user.compare_password(password=credentials.password):
        au.raise_unauthorized("Invalid password")

    # Ensure the new password is not the same as the old one
    if db_user.compare_password(password=credentials.new_password):
        au.raise_bad_request("The new password is the same as the old one")

    # Update the user's password
    UserCrud.update_user_password(db, db_user.id, new_password=credentials.new_password)
    return DefaultResponse(message="Password updated successfully")


@router.get("/logout", dependencies=[protect], response_model=DefaultResponse)
def logout(response: Response):
    """Destroys the access token on the response cookie"""

    au.set_cookie_header_response(response, token="logged out", max_age=au.LOGOUT_COOKIE_EXPIRES)
    return DefaultResponse(message="Logged out successfully")
