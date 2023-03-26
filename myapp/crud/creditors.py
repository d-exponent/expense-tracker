from myapp.crud.base_crud import Crud
from myapp.models import Creditor as CreditorOrm
from myapp.schema.creditor import CreditorCreate
from sqlalchemy.orm import Session
from myapp.crud.utils import to_title_case


class CreditorCrud(Crud):
    orm_model = CreditorOrm

    @classmethod
    def __process(cls, creditor: CreditorCreate):
        creditor.name = to_title_case(creditor.name)
        creditor.city = to_title_case(creditor.city)
        creditor.state = to_title_case(creditor.state)
        creditor.country = to_title_case(creditor.country) if creditor.country else None
        creditor.bank_name = (
            to_title_case(creditor.bank_name) if creditor.bank_name else None
        )
        creditor.country = creditor.country if creditor.country else None

        creditor.bank_name = (
            to_title_case(creditor.bank_name) if creditor.bank_name else None
        )

        return creditor

    @classmethod
    def create(cls, db: Session, creditor: CreditorCreate):
        processed_creditor = cls.__process(creditor)
        new_creditor = cls.orm_model(**processed_creditor.dict())

        db.add(new_creditor)
        db.commit()
        db.refresh(new_creditor)
        return new_creditor

    @classmethod
    def get_creditor_by_phone(cls, db: Session, phone: str):
        return db.query(cls.orm_model).filter(cls.orm_model.phone == phone).first()

    @classmethod
    def get_creditor_by_name(cls, db: Session, name: str):
        return db.query(cls.orm_model).filter(cls.orm_model.name == name).first()

    @classmethod
    def get_creditor_by_email(cls, db: Session, email: str):
        return db.query(cls.orm_model).filter(cls.orm_model.email == email).first()
