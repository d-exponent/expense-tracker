from sqlalchemy.orm import Session
from app.crud.base_crud import Crud
from app.models import Payment as PaymentOrm
from app.schema.bill_payment import PaymentCreate, PaymentOut
from app.utils.error_utils import RaiseHttpException
from app.crud.bills import BillCrud


class PaymentCrud(Crud):
    orm_model = PaymentOrm

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
        processed_payment = cls.__process(payment=payment)

        BillCrud.init_bill_payment_transaction(db=db, payment=payment)

        db_payment = cls.orm_model(**processed_payment.dict())

        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)

        return db_payment
