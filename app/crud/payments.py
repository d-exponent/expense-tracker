from sqlalchemy.orm import Session

from app.crud.base_crud import Crud
from app.crud.bills import BillCrud
from app.models import Payment
from app.schema.bill_payment import PaymentCreate, PaymentOut
from app.utils.custom_exceptions import CreatePaymentException
from app.utils.raw_sql_operators import execute_query, map_to_payment


class PaymentCrud(Crud):
    orm_model = Payment

    @classmethod
    def process(cls, payment: PaymentCreate):
        if payment.issuer != "user" and payment.issuer != "creditor":
            msg = "A payment must have an issuer as a user or a creditor"
            raise CreatePaymentException(msg)
        return payment

    @classmethod
    def create(cls, db: Session, payment: PaymentCreate) -> Payment:
        """Handles a bills payments transaction"""

        processed_payment = cls.process(payment=payment)
        BillCrud.init_bill_payment_transaction(db=db, payment=payment)
        db_payment = cls.orm_model(**processed_payment.dict())
        return cls.commit_data_to_db(db, data=db_payment)

    @classmethod
    def get_payments_for_user(cls, user_id: int) -> list[PaymentOut]:
        user_payments = execute_query(
            query="""
                    SELECT * FROM payments WHERE payments.bill_id IN (
                        SELECT id FROM bills WHERE user_id = %(id)s
                    );
                """,
            params={"id": user_id},
            mapper=map_to_payment,
        )

        return next(user_payments)
