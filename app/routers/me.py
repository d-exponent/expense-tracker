from fastapi import APIRouter, Depends, Body
from typing import Annotated

from app.schema import user as u
from app.utils.error_utils import RaiseHttpException
from app.utils.custom_exceptions import UserNotFoundException, DataError
from app.crud.users import UserCrud
from app.utils.database import dbSession
from app.dependencies.auth import get_user, get_active_user

router = APIRouter(prefix="/me", dependencies=[Depends(get_active_user)])
current_user = Annotated[u.UserAllInfo, Depends(get_user)]


@router.get("/", response_model=u.UserOutWithBills)
def get_me(me: current_user):
    """Returns the data of the currently logged-in active user"""
    return me


@router.patch("/", response_model=u.UserOut)
def update_me(db: dbSession, me: current_user, data: Annotated[u.UpdateMe, Body()]):
    user_data = None
    try:
        user_data = data.ensure_at_least_one_field()
    except DataError as e:
        RaiseHttpException.bad_request(str(e))

    return UserCrud.update_user_by_phone(db, me.phone, user_data)


@router.delete("/", status_code=204)
def delete_me(db: dbSession, me: current_user):
    """Deletes the currently logged-in user from the database"""
    try:
        UserCrud.handle_delete_me(db=db, id=me.id)
    except UserNotFoundException:
        RaiseHttpException.not_found("You don't exist in our records")
    else:
        return {"message", "Delete successfull"}

