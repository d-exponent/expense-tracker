from sqlalchemy.orm import Session

from app.crud.base_crud import Crud
from app.models import Creditor as CreditorOrm
from app.schema.creditor import CreditorCreate
from app.utils.general import title_case_words
from app.utils.raw_sql_operators import execute_query, map_to_creditor


class CreditorCrud(Crud):
    orm_model = CreditorOrm

    @classmethod
    def process(cls, creditor: CreditorCreate):
        creditor.name = title_case_words(creditor.name)
        creditor.city = title_case_words(creditor.city)
        creditor.state = title_case_words(creditor.state)
        creditor.country = (
            title_case_words(creditor.country) if creditor.country else None
        )
        creditor.bank_name = (
            title_case_words(creditor.bank_name) if creditor.bank_name else None
        )
        creditor.country = creditor.country if creditor.country else None

        creditor.bank_name = (
            title_case_words(creditor.bank_name) if creditor.bank_name else None
        )

        return creditor

    @classmethod
    def create(cls, db: Session, creditor: CreditorCreate):
        return super().create(db, data=cls.process(creditor))

    @classmethod
    def get_creditor_by_name(cls, db: Session, name: str):
        return db.query(cls.orm_model).filter(cls.orm_model.name == name).first()

    @classmethod
    def get_creditors_for_user(cls, user_id: int):
        user_creditors = execute_query(
            query="""
                    SELECT * FROM creditors WHERE creditors.id IN (
                        SELECT bills.creditor_id
                        FROM users
                        JOIN bills ON bills.user_id = %(id)s
                    );
                """,
            params={"id": user_id},
            mapper=map_to_creditor,
        )

        return next(user_creditors)
