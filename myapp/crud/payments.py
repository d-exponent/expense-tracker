from myapp.crud.base_crud import Crud
from sqlalchemy.orm import Session
from myapp.schema.payment import PaymentCreate
from myapp.models import Payment as PaymentOrm


class PaymentCrud(Crud):
    orm_model = PaymentOrm
    bill_id: int
    amount: float

    def create_payment(self, db: Session, payment_schema):
        new_payment_schema = payment_schema(bill_id=self.bill_id, amount=self.amount)
        new_payment = self.orm_model(new_payment_schema.dict())
        return PaymentCrud.__handle_add_commit_payment(
            db=db,
            payment=new_payment,
        )

    @classmethod
    def __handle_add_commit_payment(cls, db: Session, payment, commit: bool = False):
        db.add(payment)

        if commit:
            db.commit()
            db.refresh(payment)

        return payment

    @classmethod
    def create(cls, db: Session, payment: PaymentCreate):
        new_payment = cls.orm_model(**payment.dict())
        return cls.__handle_add_commit_payment(db=db, payment=new_payment, commit=True)
