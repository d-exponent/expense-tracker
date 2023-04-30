from sqlalchemy.orm import Session

from app.crud.base_crud import Crud
from app.models import Bill as BillOrm
from app.schema import bill_payment as bp
from app.utils.custom_exceptions import CreatePaymentException
from app.utils.error_utils import RaiseHttpException


def add_payment_amount(payment_amount: float, bill_amount) -> float:
    return payment_amount + float(bill_amount)


class BillCrud(Crud):
    orm_model = BillOrm

    @classmethod
    def create(cls, db: Session, bill: bp.BillCreate) -> bp.BillOutAllInfo:
        new_bill = cls.orm_model(**bill.dict())
        return cls.commit_data_to_db(db, data=new_bill)

    @classmethod
    def init_bill_payment_transaction(cls, db: Session, payment: bp.PaymentCreate):
        bill: bp.BillOut = cls.get_by_id(db=db, id=payment.bill_id)

        if bill is None:
            error_msg = f"There is no bill with the id {payment.bill_id}"
            raise CreatePaymentException(error_msg)

        query = cls.get_by_id_query(db=db, id=payment.bill_id)

        to_update = {}

        if payment.issuer == "user":
            to_update["total_paid_amount"] = add_payment_amount(
                payment.amount, bill_amount=bill.total_paid_amount
            )

        if payment.issuer == "creditor":
            to_update["total_credit_amount"] = add_payment_amount(
                payment.amount, bill_amount=bill.total_credit_amount
            )

        query.update(to_update)

    @classmethod
    def delete_bill(cls, db: Session, user_id: int, bill_id: int):
        bill = cls.get_by_id(db, id=bill_id)
        if bill is None:
            RaiseHttpException.bad_request("Theres no bill with this ID")

        if bill.user_id != user_id:
            RaiseHttpException.unauthorized("This pill doesn't belong to this user")

        
