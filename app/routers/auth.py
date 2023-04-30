from typing import Annotated
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Response, Body, Depends, Query, Response
from asyncio import create_task


from app.routers import me, login
from app.crud.users import UserCrud
from app.models import User as UserOrm
from app.dependencies.auth import protect, get_user
from app.dependencies.image_uploader import handle_user_image_upload
from app.schema import user as u
from app.schema.response import DefaultResponse

from app.utils import auth as au
from app.utils.sms import SMSMessenger
from app.utils.send_email import EmailMessenger
from app.utils.database import dbSession
from app.utils.general import AddTime, get_user_full_name
from app.utils import error_utils as eu
from app.utils.error_messages import SignupErrorMessages
from app.utils import error_messages as em


router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(login.router)
router.include_router(me.router)
invalidCred = em.InvalidCredentials


def handle_integrity_error(error_message):
    if "already exists" in error_message:
        eu.RaiseHttpException.bad_request(SignupErrorMessages.already_exists)

    if "users_password_email_ck" in error_message:
        eu.RaiseHttpException.bad_request(SignupErrorMessages.provide_credentials)

    if "users_phone_email_key" in error_message:
        eu.RaiseHttpException.bad_request(SignupErrorMessages.already_exists)

    eu.RaiseHttpException.server_error(SignupErrorMessages.server_error)


# Implementing temporary response message getter. Will be removed before production
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


@router.post("/signup", status_code=201)
async def sign_up(
    db: dbSession,
    user: Annotated[u.UserCreate, Depends(handle_user_image_upload)],
    response: Response,
):
    user_data = user.dict().copy()
    user_otp = au.generate_otp(5)
    update_data = au.config_users_otp_columns(user_otp, AddTime.add_minutes(mins=5))
    user_data.update(update_data)

    db_user = None

    try:
        db_user = UserCrud.create(db=db, user=u.UserSignUp(**user_data))
    except IntegrityError as e:
        eu.handle_create_user_integrity_exception(str(e))
    except Exception:
        eu.RaiseHttpException.server_error(em.SignupErrorMessages.server_error)

    # TEMPORARY RESPONSE IMPLEMENTATION
    # Will be removed in production as soon as twillo is set back up
    # Email messagin and sms messging will be implemented with asyncio.gather
    email_success = None
    sms_success = None
    user_full_name = get_user_full_name(db_user)

    try:
        await EmailMessenger(
            receiver_name=user_full_name, receiver_email=db_user.email
        ).send_welcome(user_otp)
        email_success = True
    except Exception:
        pass

    try:
        sms_messenger = SMSMessenger(
            receiver_name=user_full_name, receiver_phone=db_user.phone
        )
        await sms_messenger.send_welcome(user_otp)
        sms_success = True
    except Exception:
        pass

    access_token = au.handle_create_token_for_user(user_data=db_user)
    au.set_cookie_header_response(response=response, token=access_token)
    return au.get_auth_success_response(
        token=access_token,
        user_orm_data=db_user,
        message=get_response_msg(sms_sent=sms_success, email_sent=email_success),
    )


@router.get("/get-otp", response_model=DefaultResponse)
async def get_otp(
    db: dbSession, phone: str = Query(default=None), email: str = Query(default=None)
):
    if not any([phone, email]):
        eu.RaiseHttpException.bad_request("Provide either a phone or email via query")

    if all([phone, email]):
        eu.RaiseHttpException.bad_request("Provide either a phone or email via query")

    if phone:
        db_user = UserCrud.get_user_by_phone(db, phone=f"+{phone.strip()}")
    else:
        db_user = UserCrud.get_user_by_email(db, email)

    if db_user is None:
        eu.RaiseHttpException.not_found("The user does not exist in our records")

    otp_data = au.config_users_otp_columns(au.generate_otp(5), AddTime.add_minutes(3))
    try:
        UserCrud.update_user_by_phone(db, db_user.phone_number, otp_data)
    except Exception:
        eu.RaiseHttpException.server_error()

    otp = otp_data.get("otp")
    user_full_name = get_user_full_name(db_user)

    if phone:
        try:
            sms_handler = SMSMessenger(
                receiver_name=user_full_name, receiver_phone=db_user.phone
            )
            await create_task(sms_handler.send_otp(otp))
        except Exception:
            eu.RaiseHttpException.server_error(
                em.GetMobileOtpErrorMessages.otp_send_error
            )
    else:
        try:
            email_handler = EmailMessenger(
                receiver_email=db_user.email, receiver_name=user_full_name
            )
            await email_handler.send_login(otp)
        except Exception:
            eu.RaiseHttpException.server_error("Error sending Otp to email address")

    email = db_user.email_address
    return DefaultResponse(
        message=f"The One Time Password has been successfully sent to {email}"
    )


@router.post("/update-password", response_model=DefaultResponse)
def update_password(
    db: dbSession,
    credentials: Annotated[u.UserUpdatePassword, Body()],
    db_user: Annotated[UserOrm, Depends(get_user)],
):
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
    response.set_cookie(
        key=au.ACEESS_TOKEN_COOKIE_KEY,
        value="logged out",
        httponly=True,
        secure=True,
        max_age=au.LOGOUT_COOKIE_EXPIRES,
    )

    return DefaultResponse(message="Logged out successfully")
