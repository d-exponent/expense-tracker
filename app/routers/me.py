from typing import Annotated
from fastapi import APIRouter, Body, Path


from app.schema import user as u
from app.crud.users import UserCrud
from app.crud.bills import BillCrud
from app.crud.creditors import CreditorCrud
from app.crud.payments import PaymentCrud
from app.utils.database import dbSession
from app.schema import response as r, bill_payment as bp
from app.dependencies.auth import current_active_user

from app.utils.custom_exceptions import QueryExecError
from app.utils import error_utils as eu
from app.utils.bills import handle_make_bill
from app.utils.custom_exceptions import DataError


router = APIRouter(prefix="/me", dependencies=[current_active_user])
current_user = Annotated[u.UserAllInfo, current_active_user]


@router.get("/", response_model=u.UserOutWithBills)
def get_me(me: current_user):
    """Returns the data of the currently logged-in active user"""
    return me


@router.patch("/", response_model=u.UserOut)
def update_me(db: dbSession, me: current_user, data: Annotated[u.UpdateMe, Body()]):
    try:
        user_data = data.ensure_valid_field()
    except DataError as e:
        eu.RaiseHttpException.bad_request(str(e))
    else:
        return UserCrud.update_user_by_phone(db, me.phone, user_data)


@router.patch(
    "/password", response_model=r.DefaultResponse, dependencies=[current_active_user]
)
def update_my_password(
    db: dbSession,
    credentials: Annotated[u.UserUpdatePassword, Body()],
    me: current_user,
):
    """Updates only the user password
    - **password**: The current password
    - **new_password**: The new password
    - **new_password_confirm**: Same as the **new_password**
    """

    # Ensure the password is the user's password
    if not me.compare_password(password=credentials.password):
        eu.RaiseHttpException.unauthorized_with_headers("Invalid password")

    if credentials.new_password != credentials.new_password_confirm:
        eu.RaiseHttpException.bad_request("The passwords do not match")

    # Ensure the new password is not the same as the old one
    if me.compare_password(password=credentials.new_password):
        eu.RaiseHttpException.bad_request("The new password is the same as the old one")

    # Update the user's password
    UserCrud.update_user_password(db, me.id, new_password=credentials.new_password)
    return r.DefaultResponse(message="Password updated successfully")


@router.delete("/", status_code=204)
def delete_me(db: dbSession, me: current_user):
    """Deletes the currently logged-in user from the database"""
    UserCrud.delete_me(db=db, id=me.id)
    return ""


@router.get("/creditors", response_model=r.DefaultResponse)
def get_my_creditors(me: current_user):
    try:
        creditors = CreditorCrud.get_creditors_for_user(user_id=me.id)
    except QueryExecError:
        eu.RaiseHttpException.server_error("Error fetching your creditors.")
    else:
        return r.DefaultResponse(
            data=eu.handle_records(records=creditors, table_name="creditors")
        )


# MY BILLS
@router.post("/bills", response_model=r.DefaultResponse)
def create_my_bill(
    db: dbSession, me: current_user, bill: Annotated[bp.MyBillCreate, Body()]
):
    my_bill = bill.__dict__
    my_bill |= {"user_id": me.id}
    return handle_make_bill(db, bill=my_bill)


@router.get("/bills")
def get_my_bills(db: dbSession, me: current_user):
    my_bills = BillCrud.get_bills_for_user(db, user_id=me.id)
    return r.DefaultResponse(
        data=eu.handle_records(records=my_bills, table_name="bills")
    )


@router.delete("/bills/{id}", status_code=204)
def delete_my_bill(
    db: dbSession,
    id: Annotated[int, Path(description="The id of the bill to be deleted")],
    me: current_user,
):
    eu.ensure_positive_int(num=id)
    bill: bp.BillOutAllInfo = BillCrud.get_by_id(db, id)

    if bill.user_id != me.id:
        eu.RaiseHttpException.forbidden("You can only delete your bills")

    BillCrud.delete_by_id(db, id)
    return ""


# My payments
@router.get("/payments", response_model=r.DefaultResponse)
def get_my_payments(me: current_user):
    try:
        my_payments = PaymentCrud.get_payments_for_user(user_id=me.id)
    except QueryExecError:
        eu.RaiseHttpException.server_error("Error fetching your payments.")
    return r.DefaultResponse(
        data=eu.handle_records(records=my_payments, table_name="payments")
    )
