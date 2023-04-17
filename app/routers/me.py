from fastapi import APIRouter, Depends, Body
from typing import Annotated

from app.schema.user import UserOut, UserUpdate
from app.utils.error_utils import RaiseHttpException
from app.crud.users import UserCrud
from app.utils.database import dbSession
from app.dependencies.auth import get_user, allow_only_user


router = APIRouter(prefix="/me", dependencies=[allow_only_user])
# Make a protected route
current_user = Annotated[UserOut, Depends(get_user)]


@router.get("/", response_model=UserOut)
def get_me(me=current_user):
    if me is None:
        RaiseHttpException.not_found("The requested user does not exist")
        
    return me


@router.patch("/")
def update_me(db: dbSession, me: current_user, data: Annotated[UserUpdate, Body()]):
    try:
        data.validate()
        user = UserCrud.update_user_by_phone(db, me.phone_number, data)
    except Exception as e:
        if "Password cannot be updated via this route" in str(e):
            RaiseHttpException.bad_request("Password cannot be updated via this route")

        RaiseHttpException.server_error()
    else:
        return user


@router.delete("/")
def delete_user(db: dbSession, me: current_user):
    try:
        UserCrud.handle_delete_me(db=db, id=me.id)
    except Exception:
        RaiseHttpException.server_error("Deleting profile failed. Please try again!")
    else:
        return {"message", "Delete successfull"}