from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, Path, Response, HTTPException

from app.routers import login
from app.utils.app_utils import add_minutes
from app.schema.user import UserCreate, UserSignUp, UserOut
from app.crud.users import UserCrud
from app.utils.error_messages import UserErrorMessages
from app.utils.error_utils import raise_404_exception
from app.utils.database import db_init
from app.utils.sms import SMSMessenger
from app.utils.auth_utils import (
    ACEESS_TOKEN_COOKIE_KEY,
    LOGOUT_COOKIE_EXPIRES,
    handle_integrity_error,
    generate_otp,
    raise_server_error,
    get_user_update_dict,
)


router = APIRouter(prefix="/auth", tags=["auth", "authenticcation"])
router.include_router(login.router)


@router.post("/sign_up", status_code=201)
def user_sign_up(*, db: Session = Depends(db_init), user: UserCreate):
    db_user = UserCrud.get_user_by_phone(db, user.phone_number)
    if db_user:
        raise HTTPException(status_code=400, detail=UserErrorMessages.already_exists)

    user_otp = generate_otp(6)
    user_dict = user.dict().copy()
    user_dict.update(
        get_user_update_dict(user_otp, add_minutes(12))
    )  # allow 2 mins for lag

    try:
        db_user = UserCrud.create(db=db, user=UserSignUp(**user_dict))
    except IntegrityError as e:
        handle_integrity_error(error_message=str(e))
    except Exception:
        raise_server_error(message="Error creating the User")

    user_full_name = f"{db_user.first_name} {db_user.last_name}"
    sms_messenger = SMSMessenger(user_full_name, db_user.phone_number)

    try:
        sms_messenger.send_otp(user_otp, type="sign-up")
    except Exception:
        raise_server_error(
            message="Something went wrong while sending the user's otp sms. Please login with the phone number to recieve a new otp sms"
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
        raise_404_exception("This user does not exist")

    user_otp = generate_otp(5)
    data = get_user_update_dict(otp=user_otp, otp_expires=add_minutes(4))
    # Allowing extra 2 minutes for

    try:
        UserCrud.update_user_by_phone(db, phone=phone_number, update_data=data)
    except Exception:
        raise_server_error()

    try:
        user_name = f"{user.first_name} {user.last_name}"
        SMSMessenger(user_name, user.phone_number).send_otp(user_otp)
        return {"message": "Otp has been sent succcesfully! Expires in 2 minutes"}
    except Exception:
        raise_server_error(
            message="Something went wrong in sending the otp. Please try again"
        )


@router.get("/logout")
def logout(response: Response):
    response.set_cookie(
        key=ACEESS_TOKEN_COOKIE_KEY,
        value="logged out",
        httponly=True,
        secure=True,
        max_age=LOGOUT_COOKIE_EXPIRES,
    )

    return {"message": "Logged out successfully"}
