from sqlalchemy.orm import Session

from app.crud.base_crud import Crud
from app.models import Creditor as CreditorOrm
from app.schema.creditor import CreditorCreate


def to_title_case(str) -> str:
    words = str.split(" ")

    if len(words) == 1:
        return words[0].title()

    titled_words = [word.title() for word in words]
    return " ".join(titled_words)


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