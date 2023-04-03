from psycopg2 import connect
from fastapi import HTTPException
from sqlalchemy.orm import Session

from myapp.crud.base_crud import Crud
from myapp.models import Bill as BillOrm
from myapp.schema.bill_payment import BillCreate, BillOutAllInfo, PaymentCreate, BillOut
from myapp.utils.error_utils import raise_bad_request_http_error


def add_payment_amount(payment_amount: float, bill_amount) -> float:
    return payment_amount + float(bill_amount)


class BillCrud(Crud):
    orm_model = BillOrm
    create_schema = BillCreate

    @classmethod
    def create(cls, db: Session, bill: BillCreate) -> BillOutAllInfo:
        cls.assert_item_schema(bill)

        new_bill = cls.orm_model(**bill.dict())
        db.add(new_bill)
        db.commit()
        db.refresh(new_bill)
        return new_bill

    @classmethod
    def init_bill_payment_transaction(cls, db: Session, payment: PaymentCreate):
        bill: BillOut = cls.get_by_id(db, id=payment.bill_id)

        if bill is None:
            raise_bad_request_http_error(
                message=f"There is no bill with the id {payment.bill_id}"
            )

        query = cls._get_by_id_query(db=db, id=payment.bill_id)

        update_prop = {}

        if payment.issuer_type == "user":
            update_prop["total_paid_amount"] = add_payment_amount(
                payment.amount, bill_amount=bill.total_paid_amount
            )

        if payment.issuer_type == "creditor":
            update_prop["total_credit_amount"] = add_payment_amount(
                payment.amount, bill_amount=bill.total_credit_amount
            )

        query.update(update_prop)

    @classmethod 
    def update_by_id(cls, db: Session, id: int, data: dict, model_name_repr: str):
        return super().update_by_id(db, id, data, model_name_repr)