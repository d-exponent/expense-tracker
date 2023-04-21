from typing import Annotated
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Path, Response, Body, Depends

from app.routers import me, login
from app.crud.users import UserCrud
from app.utils import auth_utils as au
from app.utils.sms import SMSMessenger
from app.models import User as UserOrm
from app.dependencies.auth import protect, get_user
from app.utils.database import dbSession
from app.utils.app_utils import AddTime
from app.utils.error_utils import RaiseHttpException
from app.utils.error_messages import SignupErrorMessages
from app.utils import error_messages as em
from app.schema import user as u


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


@router.post("/signup", status_code=201)
def user_sign_up(db: dbSession, user: u.UserCreate):
    UserCrud.handle_user_if_exists(db, phone=user.phone_number)

    user_data = user.dict().copy()
    user_otp = au.generate_otp(5)
    update_data = au.config_users_otp_columns(
        otp=user_otp, otp_expires=AddTime.add_minutes(mins=5)
    )
    user_data.update(update_data)

    try:
        db_user = UserCrud.create(db=db, user=u.UserSignUp(**user_data))
    except IntegrityError as e:
        handle_integrity_error(str(e))
    except Exception:
        RaiseHttpException.server_error(em.SignupErrorMessages.server_error)
    else:
        full_name = f"{db_user.first_name} {db_user.last_name}"
        phone_number = db_user.phone_number

        try:
            # Send signup sms with otp to the new user
            SMSMessenger(full_name, phone_number).send_signup_msg(otp=user_otp)
        except Exception:
            RaiseHttpException.server_error(em.SignupErrorMessages.otp_send_error)

        response_msg = "otp was sent to your phone number. "
        response_msg = response_msg + "Login with the otp to complete your registration"

        return {
            "message": response_msg,
            "data": u.UserOut.from_orm(db_user),
        }


@router.get("/mobile/{phone_number}")
def get_otp(
    db: dbSession,
    phone_number: Annotated[str, Path()],
):
    user = UserCrud.get_user_by_phone(db, phone=phone_number)

    if user is None:
        RaiseHttpException.not_found(em.GetMobileOtpErrorMessages.does_not_exist)

    user_otp = au.generate_otp(5)
    data = au.config_users_otp_columns(otp=user_otp, otp_expires=AddTime.add_minutes(3))

    try:
        UserCrud.update_user_by_phone(db, phone=phone_number, update_data=data)
    except Exception:
        RaiseHttpException.server_error(em.GetMobileOtpErrorMessages.update_user_error)

    user_name = f"{user.first_name} {user.last_name}"
    try:
        SMSMessenger(user_name, user.phone_number).send_otp(otp=user_otp)
    except Exception:
        RaiseHttpException.server_error(em.GetMobileOtpErrorMessages.otp_send_error)
    else:
        return {"message": "Otp has been sent successfully! Expires in 2 minutes"}


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
    return {"message": "Password updated successfully"}


@router.get("/logout", dependencies=[protect])
def logout(response: Response):
    response.set_cookie(
        key=au.ACEESS_TOKEN_COOKIE_KEY,
        value="logged out",
        httponly=True,
        secure=True,
        max_age=au.LOGOUT_COOKIE_EXPIRES,
    )

    return {"message": "Logged out successfully"}
