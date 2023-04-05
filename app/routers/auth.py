from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Path, Response, HTTPException
from random import randint
from app.crud.users import UserCrud
from app.utils.database import db_dependency
from app.utils.sms import SMSMessenger
from app.dependencies.auth import LOGOUT_COOKIE_EXPIRES_AFTER, ACEESS_TOKEN_COOKIE_KEY

from app.routers import login


def raise_404_exception(msg: str = "Not Found"):
    raise HTTPException(status_code=404, detail=msg)


def generate_otp(digits_num: int = 4):
    otp_digits = [str(randint(0, 9)) for _ in range(0, digits_num)]
    return "".join(otp_digits)


router = APIRouter(prefix="/auth", tags=["auth", "authenticcation"])
router.include_router(login.router)


@router.get("/mobile_token/{phone_number}")
def get_otp_sms(
    db: Annotated[Session, Depends(db_dependency)],
    phone_number: Annotated[str, Path()],
):
    user = UserCrud.get_user_by_phone(db, phone=phone_number)

    if user is None:
        raise_404_exception("This user does not exist")

    user_otp = generate_otp(5)

    # Update the user
    UserCrud.update_user_otp(db=db, phone=phone_number, otp=user_otp)

    try:
        user_name = f"{user.first_name} {user.last_name}"
        SMSMessenger(user_name, user.phone_number).send_login_otp_sms(user_otp)
        return {"message": "Otp has been sent succcesfully! Expires in 5 minutes"}
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong in sending the otp. Please try again",
        )


@router.get("/logout")
def logout(response: Response):
    response.set_cookie(
        key=ACEESS_TOKEN_COOKIE_KEY,
        value="logged out",
        httponly=True,
        secure=True,
        max_age=LOGOUT_COOKIE_EXPIRES_AFTER,
    )

    return {"message": "Logged out successfully"}
