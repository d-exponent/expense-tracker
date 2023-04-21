from fastapi import APIRouter, Depends, Body
from typing import Annotated

from app.schema import user as u
from app.utils.error_utils import RaiseHttpException
from app.crud.users import UserCrud
from app.utils.database import dbSession
from app.dependencies.auth import get_user, allow_only_user


router = APIRouter(prefix="/me", dependencies=[allow_only_user])
current_user = Annotated[u.UserAllInfo, Depends(get_user)]


@router.get("/", response_model=u.UserOutWithBills)
def get_me(me: current_user):
    return me


@router.patch("/", response_model=u.UserOut)
def update_me(db: dbSession, me: current_user, data: Annotated[u.UserUpdate, Body()]):
    user_data = data.validate_data()

    try:
        return UserCrud.update_user_by_phone(db, me.phone_number, user_data)
    except Exception as e:
        if "Password cannot be updated via this route" in str(e):
            RaiseHttpException.bad_request("Password cannot be updated via this route")

        RaiseHttpException.server_error()


@router.delete("/")
def delete_user(db: dbSession, me: current_user):
    try:
        UserCrud.handle_delete_me(db=db, id=me.id)
    except Exception:
        RaiseHttpException.server_error("Deleting profile failed. Please try again!")
    else:
        return {"message", "Delete successfull"}
