from typing import Annotated
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Response, Body, Depends, Query
from twilio.rest import Client
from email.message import EmailMessage
from asyncio import create_task


from app.routers import me, login
from app.crud.users import UserCrud
from app.models import User as UserOrm
from app.dependencies.auth import protect, get_user
from app.schema import user as u
from app.schema.response import DefaultResponse

from app.utils import auth_utils as au
from app.utils.sms import SMSMessenger
from app.utils.send_email import EmailMessenger
from app.utils.database import dbSession
from app.utils.app_utils import AddTime
from app.utils.error_utils import RaiseHttpException
from app.utils.error_messages import SignupErrorMessages
from app.utils import error_messages as em


router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(login.router)
router.include_router(me.router)
invalidCred = em.InvalidCredentials


def handle_integrity_error(error_message):
    if "already exists" in error_message:
        RaiseHttpException.bad_request(SignupErrorMessages.already_exists)

    if "users_password_email_ck" in error_message:
        RaiseHttpException.bad_request(SignupErrorMessages.provide_credentials)

    if "users_phone_email_key" in error_message:
        RaiseHttpException.bad_request(SignupErrorMessages.already_exists)

    RaiseHttpException.server_error(SignupErrorMessages.server_error)


# Implementing tempory reposne message getter. Will be removed in production
def get_response_msg(**kwargs) -> str:
    # sms_send: bool, email_send: bool) -> str:
    sms_sent = kwargs.get("sms_sent")
    email_sent = kwargs.get("email_sent")
    all_sent = all([sms_sent, email_sent])
    response_msg = "Your account has been successfully created."

    if not all_sent:
        response_msg = (
            f"{response_msg} Get otp with your email address to verify your account"
        )
    else:
        if all_sent:
            response_msg = (
                f"{response_msg} otp was sent to your phone number and email address. "
            )
        elif sms_sent:
            response_msg = (
                f"{response_msg} otp was sent to your registered phone number. "
            )
        else:
            response_msg = (
                f"{response_msg} otp was sent to your registered email address. "
            )

    return response_msg


@router.post("/signup", status_code=201, response_model=u.CreateUser)
async def sign_up(db: dbSession, user: u.UserCreate):
    UserCrud.handle_user_if_exists(db, phone=user.phone_number)

    user_data = user.dict().copy()
    user_otp = au.generate_otp(5)
    update_data = au.config_users_otp_columns(user_otp, AddTime.add_minutes(mins=5))
    user_data.update(update_data)

    db_user = None

    try:
        db_user = UserCrud.create(db=db, user=u.UserSignUp(**user_data))
    except IntegrityError as e:
        handle_integrity_error(str(e))
    except Exception:
        RaiseHttpException.server_error(em.SignupErrorMessages.server_error)

    """
    The below implemetation will be enabled when twillo account is setup
    For now it will be commented out as it will raise an exception
    """
    # try:
    #     # Send signup messages with otp to the new user
    #     await gather(
    #         EmailMessenger(db_user, EmailMessage).send_signup_email(user_otp),
    #         SMSMessenger(db_user, Client).send_signup_msg(user_otp),
    #     )

    # except Exception:
    #     RaiseHttpException.server_error(em.SignupErrorMessages.otp_send_error)
    # else:
    #     res_msg = "Your account has been successfully created."
    #     res_msg = f"{res_msg} otp was sent to your phone number and email address."

    # return u.CreateUser(**{
    #     "message": res_msg,
    #     "data": u.UserOut.from_orm(db_user),
    # })

    # ALTERNATIATE TEMPORARY RESPONSE IMPLEMENTATION
    # Will be removed in production
    email_success = None
    sms_success = None

    try:
        emailer = EmailMessenger(db_user, EmailMessage)
        await create_task(emailer.send_welcome(user_otp))
        email_success = True
    except Exception:
        pass

    try:
        sms_messenger = SMSMessenger(db_user, Client)
        await create_task(sms_messenger.send_welcome(user_otp))
        sms_success = True
    except Exception:
        pass

    return u.CreateUser(
        message=get_response_msg(sms_sent=sms_success, email_sent=email_success),
        data=u.UserOut.from_orm(db_user),
    )


@router.get("/get-otp")
async def get_otp(
    db: dbSession, phone: str = Query(default=None), email: str = Query(default=None)
):
    if not any([phone, email]):
        RaiseHttpException.bad_request("Provide either a phone or email via query")

    if all([phone, email]):
        RaiseHttpException.bad_request("Provide either a phone or email via query")

    if phone:
        db_user = UserCrud.get_user_by_phone(db, phone=f"+{phone.strip()}")
    else:
        db_user = UserCrud.get_user_by_email(db, email)

    if db_user is None:
        RaiseHttpException.not_found("The user does not exist in our records")

    otp_data = au.config_users_otp_columns(au.generate_otp(5), AddTime.add_minutes(3))
    try:
        UserCrud.update_user_by_phone(db, db_user.phone_number, otp_data)
    except Exception:
        RaiseHttpException.server_error()

    otp = otp_data.get("otp")

    if phone:
        try:
            sms_handler = SMSMessenger(db_user, Client)
            await create_task(sms_handler.send_otp(otp))
        except Exception:
            RaiseHttpException.server_error(em.GetMobileOtpErrorMessages.otp_send_error)
    else:
        try:
            email_handler = EmailMessenger(db_user, EmailMessage)
            await create_task(email_handler.send_login(otp))
        except Exception:
            RaiseHttpException.server_error("Error sending Otp to email address")

    email = db_user.email_address
    return DefaultResponse(
        message=f"The One Time Password has been successfully sent to {email}"
    )


@router.post("/update-password")
def update_password(
    db: dbSession,
    credentials: Annotated[u.UserUpdatePassword, Body()],
    db_user: Annotated[UserOrm, Depends(get_user)],
):
    if credentials.new_password != credentials.new_password_confirm:
        RaiseHttpException.bad_request("The passwords do not match")

    # Ensure the password is correct
    if not db_user.compare_password(password=credentials.password):
        au.raise_unauthorized("Invalid password")

    # Ensure the new password is not the same as the old one
    if db_user.compare_password(password=credentials.new_password):
        au.raise_bad_request("The new password is the same as the old one")

    # Update the user's password
    UserCrud.update_user_password(db, db_user.id, new_password=credentials.new_password)
    return DefaultResponse(message="Password updated successfully")


@router.get("/logout", dependencies=[protect])
def logout(response: Response):
    response.set_cookie(
        key=au.ACEESS_TOKEN_COOKIE_KEY,
        value="logged out",
        httponly=True,
        secure=True,
        max_age=au.LOGOUT_COOKIE_EXPIRES,
    )

    return DefaultResponse(message="Logged out successfully")
