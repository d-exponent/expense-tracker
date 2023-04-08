from sqlalchemy.orm import Session
from app.crud.base_crud import Crud
from app.models import Payment as PaymentOrm
from app.schema.bill_payment import PaymentCreate, PaymentOut
from app.utils.error_utils import RaiseHttpException
from app.crud.bills import BillCrud


class PaymentCrud(BillCrud, Crud):
    orm_model = PaymentOrm
    create_schema = PaymentCreate

    @classmethod
    def __process(cls, payment: PaymentCreate):
        if payment.issuer != "user" and payment.issuer != "creditor":
            RaiseHttpException.bad_request(
                msg="A payment must have an issuer as a user or a creditor"
            )

        # Might seem dumb at the moment but we may modify the payment in future versions
        return payment

    @classmethod
    def create(cls, db: Session, payment: PaymentCreate) -> PaymentOut:
        # Start a new transaction

        processed_payment = cls.__process(payment=payment)

        # Updates the bill record with the payment information
        cls.init_bill_payment_transaction(db=db, payment=processed_payment)

        db_payment = cls.orm_model(**processed_payment.dict())

        # Commit the transaction
        return cls.commit_data_to_db(db=db, data=db_payment)
