from sqlalchemy.orm import Session

from app.crud.base_crud import Crud
from app.models import Bill
from app.schema import bill_payment as bp
from app.utils.custom_exceptions import CreatePaymentException
from app.utils.error_utils import RaiseHttpException


class BillCrud(Crud):
    orm_model = Bill

    @classmethod
    def create(cls, db: Session, bill: bp.BillCreate) -> Bill:
        return super().create(db, data=bill)

    @classmethod
    def init_bill_payment_transaction(cls, db: Session, payment: bp.PaymentCreate):
        bill: bp.BillOut = cls.get_by_id(db=db, id=payment.bill_id)

        if bill is None:
            error_msg = f"There is no bill with the id {payment.bill_id}"
            raise CreatePaymentException(error_msg)

        query = cls.get_by_id_query(db=db, id=payment.bill_id)

        def add_payment_amount(payment_amount: float, bill_amount) -> float:
            return payment_amount + float(bill_amount)

        to_update = {}
        if payment.issuer == "user":
            to_update["total_paid_amount"] = add_payment_amount(
                payment.amount, bill.total_paid_amount
            )

        if payment.issuer == "creditor":
            to_update["total_credit_amount"] = add_payment_amount(
                payment.amount, bill.total_credit_amount
            )

        query.update(to_update)

    @classmethod
    def get_bills_for_user(cls, db: Session, user_id: int) -> list[Bill] | list:
        return db.query(cls.orm_model).filter(cls.orm_model.user_id == user_id).all()

    @classmethod
    def delete_by_id(cls, db: Session, id: int):
        bill: Bill = super().get_by_id(db, id)

        if bill is None:
            RaiseHttpException.not_found("This bill does not exist")

        if not bill.paid:
            RaiseHttpException.forbidden("The bill has an outstanding debt")

        super().delete_by_id(db, id)
