import os
from typing import Annotated
from fastapi.responses import FileResponse
from fastapi import APIRouter, Body, Path, Depends

from app.crud.users import UserCrud
from app.crud.bills import BillCrud
from app.crud.payments import PaymentCrud, CreatePaymentException
from app.crud.creditors import CreditorCrud

from app.schema import user as u
from app.schema import response as r, bill_payment as bp
from app.dependencies.auth import current_active_user
from app.dependencies.user_multipart import handle_image_upload

from app.utils import error_utils as eu
from app.utils.database import dbSession
from app.utils.bills import handle_make_bill
from app.utils.file_operations import absolute_path_for_image
from app.utils.custom_exceptions import DataError, QueryExecError


router = APIRouter(prefix="/me", tags=["me"], dependencies=[current_active_user])
current_user = Annotated[u.UserAllInfo, current_active_user]


@router.get("/", response_model=u.UserOutWithBills)
def get_me(me: current_user):
    """Returns the data of the currently logged-in active user"""
    return me


@router.get('/profile-picture')
async def get_my_profile_image(me: current_user):
    image_file = absolute_path_for_image(me.image_url)

    if not os.path.exists(image_file):
        eu.RaiseHttpException.bad_request('The image does not exist')

    return FileResponse(image_file)


# ------------ MY UPDATE OPERATIONS ---


@router.patch("/", response_model=u.UserOut)
def update_me(db: dbSession, me: current_user, data: Annotated[u.UpdateMe, Body()]):
    try:
        user_data = data.ensure_valid_field()
    except DataError as e:
        eu.RaiseHttpException.bad_request(str(e))
    else:
        return UserCrud.update_user_by_phone(db, me.phone, user_data)


@router.patch('/profile-picture', response_model=r.DefaultResponse)
def update_profile_image(
    db: dbSession,
    me: current_user,
    image_url: Annotated[str, Depends(handle_image_upload)],
):
    if image_url is None:
        eu.RaiseHttpException.bad_request('Provide an image file!')

    prev_image_url = me.image_url
    updated_me = UserCrud.update_by_id(
        db=db, id=me.id, data={"image_url": image_url}, table='users'
    )

    # Delete the previous image
    prev_image_loc = absolute_path_for_image(prev_image_url)
    if os.path.exists(prev_image_loc):
        try:
            os.remove(prev_image_loc)
        except OSError:
            pass

    return r.DefaultResponse(
        data=u.UserOut.from_orm(updated_me),
        message='Profile image is updated successfully!',
    )


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


# ------------------UPDATE OPERATIONS END


@router.delete("/", status_code=204)
def delete_me(db: dbSession, me: current_user):
    """Deletes the currently logged-in user from the database"""
    UserCrud.delete_me(db=db, id=me.id)
    return ""


# ----------------------------------- MY CREDITORS ---------------------------


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


#  ----------------------------------- MY BILLS -----------------------------------


@router.post("/bills", response_model=r.DefaultResponse)
def create_my_bill(
    db: dbSession, me: current_user, bill: Annotated[bp.MyBillCreate, Body()]
):
    my_bill = bill.__dict__
    my_bill |= {"user_id": me.id}
    return handle_make_bill(db, bill=my_bill)


@router.get("/bills", response_model=r.DefaultResponse)
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


# ------------------------------------------ My PAYMENTS  -----------------------------------------


@router.get("/payments", response_model=r.DefaultResponse)
def get_my_payments(me: current_user):
    try:
        my_payments = PaymentCrud.get_payments_for_user(user_id=me.id)
    except QueryExecError:
        eu.RaiseHttpException.server_error("Error fetching your payments.")
    return r.DefaultResponse(
        data=eu.handle_records(records=my_payments, table_name="payments")
    )


@router.post('/payments', response_model=r.DefaultResponse)
def make_payment(
    db: dbSession, me: current_user, payment: Annotated[bp.PaymentCreate, Body()]
):
    bills = BillCrud.get_bills_for_user(db, me.id)

    # current user has no bills
    if len(bills) == 0:
        eu.RaiseHttpException.bad_request("You currently have no bills")

    # Ensure the referenced bill belongs to the current user
    if len([bill for bill in bills if bill.id == payment.bill_id]) == 0:
        msg = "You did not create the bill you are trying to make payment on"
        eu.RaiseHttpException.forbidden(msg)

    try:
        res_msg = "Payment created successfully!"
        db_payment = PaymentCrud.create(db, payment)
    except CreatePaymentException as e:
        eu.RaiseHttpException.bad_request(str(e))
    else:
        return r.DefaultResponse(message=res_msg, data=db_payment)
