from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, Path, Response

from app.routers import login
from app.crud.users import UserCrud
from app.utils import auth_utils as au
from app.utils.error_utils import RaiseHttpException
from app.utils.app_utils import add_minutes
from app.utils.sms import SMSMessenger
from app.utils.database import db_init
from app.schema.user import UserCreate, UserSignUp, UserOut


router = APIRouter(prefix="/auth", tags=["auth", "authenticcation"])
router.include_router(login.router)


@router.post("/sign_up", status_code=201)
def user_sign_up(*, db: Session = Depends(db_init), user: UserCreate):
    UserCrud.handle_user_if_exists(db, phone=user.phone_number)

    user_otp = au.generate_otp(6)
    user_data = user.dict().copy()
    update_data = au.otp_updated_user_info(
        user_otp, add_minutes(12)
    )  # allow two minutes for lag
    user_data.update(update_data)

    try:
        db_user = UserCrud.create(db=db, user=UserSignUp(**user_data))
    except IntegrityError as e:
        au.handle_integrity_error(error_message=str(e))
    except Exception:
        RaiseHttpException.server_error(msg="Error creating the User")

    full_name = f"{db_user.first_name} {db_user.last_name}"
    phone_number = db_user.phone_number

    try:
        SMSMessenger(full_name, phone_number).send_otp(user_otp, type="sign-up")
    except Exception:
        RaiseHttpException.server_error(
            msg="Something went wrong with sending the otp via sms. Login with the phone number to recieve a new otp"
        )

    return {
        "message": f"An otp was sent to {db_user.phone_number}. Login with the otp to complete your registration",
        "data": UserOut.from_orm(db_user),
    }


@router.get("/mobile/{phone_number}")
def get_otp(
    db: Annotated[Session, Depends(db_init)],
    phone_number: Annotated[str, Path()],
):
    user = UserCrud.get_user_by_phone(db, phone=phone_number)
    if user is None:
        RaiseHttpException.not_found(msg="The user does not exist")

    user_otp = au.generate_otp(5)
    data = au.otp_updated_user_info(otp=user_otp, otp_expires=add_minutes(4))

    try:
        UserCrud.update_user_by_phone(db, phone=phone_number, update_data=data)
    except Exception:
        RaiseHttpException.server_error()

    try:
        user_name = f"{user.first_name} {user.last_name}"
        SMSMessenger(user_name, user.phone_number).send_otp(user_otp)
    except Exception:
        RaiseHttpException.server_error(
            msg="Something went wrong in sending the otp. Please try again"
        )
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
