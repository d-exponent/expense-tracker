from typing import Annotated
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Path, Response

from app.routers import login
from app.crud.users import UserCrud
from app.utils import auth_utils as au
from app.utils.sms import SMSMessenger
from app.models import User as UserOrm
from app.utils.database import dbSession
from app.utils.app_utils import AddTime
from app.utils.error_utils import RaiseHttpException
from app.utils.error_messages import SignupErrorMessages, GetMobileOtpErrorMessages
from app.schema.user import UserCreate, UserSignUp, UserOut


router = APIRouter(prefix="/auth", tags=["auth", "authenticcation"])
router.include_router(login.router)

raise_server_error = RaiseHttpException.server_error


@router.post("/signup", status_code=201)
def user_sign_up(db: dbSession, user: UserCreate):
    UserCrud.handle_user_if_exists(db, phone=user.phone_number)

    user_otp = au.generate_otp(6)
    user_data = user.dict().copy()
    user_data.update(
        au.otp_updated_user_info(otp=user_otp, otp_expires=AddTime.add_minutes(mins=5))
    )

    try:
        db_user: UserOrm = UserCrud.create(db=db, user=UserSignUp(**user_data))
    except IntegrityError as e:
        au.handle_integrity_error(error_message=str(e))
    except Exception:
        raise_server_error(SignupErrorMessages.server_error)

    full_name = f"{db_user.first_name} {db_user.last_name}"
    phone_number = db_user.phone_number

    try:
        SMSMessenger(full_name, phone_number).send_otp(user_otp, type="signup")
    except Exception:
        raise_server_error(SignupErrorMessages.server_error)

    return {
        "message": f"An otp was sent to {db_user.phone_number}. Login with the otp to complete your registration",
        "data": UserOut.from_orm(db_user),
    }


@router.get("/mobile/{phone_number}")
def get_otp(
    db: dbSession,
    phone_number: Annotated[str, Path()],
):
    user: UserOrm = UserCrud.get_user_by_phone(db, phone=phone_number)
    if user is None:
        RaiseHttpException.not_found(GetMobileOtpErrorMessages.not_found)

    user_otp = au.generate_otp(5)
    data = au.otp_updated_user_info(otp=user_otp, otp_expires=AddTime.add_minutes(3))

    try:
        UserCrud.update_user_by_phone(db, phone=phone_number, update_data=data)
    except Exception:
        raise_server_error(GetMobileOtpErrorMessages.update_user_error)

    try:
        user_name = f"{user.first_name} {user.last_name}"
        SMSMessenger(user_name, user.phone_number).send_otp(user_otp)
    except Exception:
        raise_server_error(GetMobileOtpErrorMessages.otp_send_error)
    else:
        return {"message": "Otp has been sent succcesfully! Expires in 2 minutes"}


@router.get("/logout")
def logout(response: Response):
    response.set_cookie(
        key=au.ACEESS_TOKEN_COOKIE_KEY,
        value="logged out",
        httponly=True,
        secure=True,
        max_age=au.LOGOUT_COOKIE_EXPIRES,
    )

    return {"message": "Logged out successfully"}
