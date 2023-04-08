from sqlalchemy.orm import Session

from app.crud.base_crud import Crud
from app.models import Bill as BillOrm
from app.schema import bill_payment as bp
from app.utils.error_utils import RaiseHttpException


def add_payment_amount(payment_amount: float, bill_amount) -> float:
    return payment_amount + float(bill_amount)


class BillCrud(Crud):
    orm_model = BillOrm
    create_schema = bp.BillCreate

    @classmethod
    def create(cls, db: Session, bill: bp.BillCreate) -> bp.BillOutAllInfo:
        new_bill = cls.orm_model(**bill.dict())
        return cls.commit_data_to_db(new_bill)

    @classmethod
    def init_bill_payment_transaction(cls, db: Session, payment: bp.PaymentCreate):
        bill: bp.BillOut = cls.get_by_id(db, id=payment.bill_id)

        if bill is None:
            error_msg = f"There is no bill with the id {payment.bill_id}"
            RaiseHttpException.bad_request(msg=error_msg)

        query = cls._get_by_id_query(db=db, id=payment.bill_id)

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
