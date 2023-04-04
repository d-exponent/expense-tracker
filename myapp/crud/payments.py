from sqlalchemy.orm import Session


from myapp.crud.base_crud import Crud
from myapp.models import Payment as PaymentOrm
from myapp.schema.bill_payment import PaymentCreate, PaymentOut
from myapp.utils.error_utils import raise_bad_request_http_error
from myapp.crud.bills import BillCrud


class PaymentCrud(Crud):
    orm_model = PaymentOrm
    create_schema = PaymentCreate

    @classmethod
    def __process(cls, payment: PaymentCreate):
        cls.assert_item_schema(payment)

        if payment.issuer != "user" and payment.issuer != "creditor":
            raise_bad_request_http_error(
                message="A payment must have an issuer as a user or a creditor"
            )

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
