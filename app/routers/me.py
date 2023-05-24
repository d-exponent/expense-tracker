import os
from typing import Annotated
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Body, Path, Depends

from app.crud.users import UserCrud
from app.crud.bills import BillCrud
from app.crud.payments import PaymentCrud, CreatePaymentException
from app.crud.creditors import CreditorCrud

from app.schema import user as u
from app.schema import response as r, bill_payment as bp, creditor as c
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
    if me.image_url is None:
        eu.raise_400_exception("There is no image associated with this user")

    image_file = absolute_path_for_image(me.image_url)

    if not os.path.exists(image_file):
        eu.RaiseHttpException.server_error('The image weirdly doesn\'t exist')

    return FileResponse(image_file)


# ------------ MY UPDATE OPERATIONS ---


@router.patch("/", response_model=u.UserOut)
def update_me(db: dbSession, me: current_user, data: Annotated[u.UpdateMe, Body()]):
    try:
        user_data = data.ensure_valid_field()
    except DataError as e:
        eu.raise_400_exception(str(e))
    else:
        return UserCrud.update_user_by_phone(db, me.phone, user_data)


@router.patch('/profile-picture', response_model=r.DefaultResponse)
def upload_profile_image(
    db: dbSession,
    me: current_user,
    image_url: Annotated[str, Depends(handle_image_upload)],
):
    if image_url is None:
        eu.raise_400_exception('Provide an image file!')

    prev_image_url = me.image_url
    updated_me = UserCrud.update_by_id(
        db=db, id=me.id, data={"image_url": image_url}, table='users'
    )

    # Delete the previous image if exists
    if prev_image_url:
        prev_image_loc = absolute_path_for_image(prev_image_url)
        if os.path.exists(prev_image_loc):
            try:
                os.remove(prev_image_loc)
            except OSError:
                pass

    return r.DefaultResponse(
        data={"image_url": updated_me.image_url},
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

    if me.email is None:
        eu.raise_400_exception("User does not have an email and password credentils")

    # Ensure the password is the user's password
    if not me.compare_password(password=credentials.password):
        eu.RaiseHttpException.unauthorized_with_headers("Invalid password")

    if credentials.new_password != credentials.new_password_confirm:
        eu.raise_400_exception("The passwords do not match")

    # Ensure the new password is not the same as the old one
    if me.compare_password(password=credentials.new_password):
        eu.raise_400_exception("The new password is the same as the old one")

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
        creditors = CreditorCrud.get_creditors_for_user(me.id)
    except QueryExecError:
        eu.RaiseHttpException.server_error("Error fetching your creditors.")
    else:
        return r.DefaultResponse(
            data=eu.handle_records(records=creditors, table_name="creditors")
        )


#  ----------------------------------- MY BILLS -----------------------------------


class MyCreditorBillCreate(c.MyCreditorCreate):
    total_credit_amount: float = 0.00
    total_paid_amount: float = 0.00


@router.post("/bills", response_model=r.DefaultResponse)
def create_my_bill(
    db: dbSession,
    me: current_user,
    bill_data: Annotated[bp.MyBillCreate | MyCreditorBillCreate, Body()],
):
    bill = {}
    if isinstance(bill_data, MyCreditorBillCreate):
        creditor = bill_data.copy().__dict__
        creditor["owner_id"] = me.id
        creditor.pop("total_credit_amount") and creditor.pop("total_paid_amount")

        try:
            db_creditor = CreditorCrud.create(db, c.CreditorCreate(**creditor))
        except IntegrityError as e:
            eu.handle_creditors_integrity_exception(str(e))
        else:
            bill = {
                "user_id": me.id,
                "total_credit_amount": bill_data.total_credit_amount,
                "total_paid_amount": bill_data.total_paid_amount,
                "creditor_id": db_creditor.id,
            }

    elif isinstance(bill_data, bp.MyBillCreate):
        bill = bill_data.__dict__
        bill["user_id"] = me.id

    return handle_make_bill(db, bill)


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
        eu.raise_400_exception("You currently have no bills")

    # Ensure the referenced bill belongs to the current user
    if len([bill for bill in bills if bill.id == payment.bill_id]) == 0:
        msg = "You did not create the bill you are trying to make payment on"
        eu.RaiseHttpException.forbidden(msg)

    try:
        res_msg = "Payment created successfully!"
        db_payment = PaymentCrud.create(db, payment)
    except CreatePaymentException as e:
        eu.raise_400_exception(str(e))
    else:
        return r.DefaultResponse(message=res_msg, data=db_payment)
