from sqlalchemy.orm import Session

from myapp.crud.base_crud import Crud
from myapp.database.config import user, password, db
from myapp.models import Bill as BillOrm
from myapp.schema.bill import BillCreate, CustomBillOut
from myapp.crud.utils.bills_utils import (
    BILL_TYPES,
    map_record_to_dict,
    handle_transaction_exceptions,
    TransactionQueries,
    BillTransactionError,  # Just so the bill router can accessed from this module
)


def add_payment_amount(payment_amount: float, bill_amount) -> float:
    return payment_amount + float(bill_amount)

"""

(psycopg2.errors.ForeignKeyViolation) insert or update on table "bills" violates foreign key co  nstra
int "bills_user_id_fkey"
DETAIL:  Key (user_id)=(1) is not present in table "users"
"""

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

        if payment.issuer == "user":
            update_prop["total_paid_amount"] = add_payment_amount(
                payment.amount, bill_amount=bill.total_paid_amount
            )

        if payment.issuer == "creditor":
            update_prop["total_credit_amount"] = add_payment_amount(
                payment.amount, bill_amount=bill.total_credit_amount
            )

        query.update(update_prop)
