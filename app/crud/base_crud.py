from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Annotated

from app.utils.database import db_dependency


class Crud:
    orm_model = None

    def __init__(self, db: Annotated[Session, Depends(db_dependency)]):
        self.db = db

    def __process(cls, item):
        pass

    def create(cls, db: Session, item):
        pass

    def get_by_id(cls, db: Session, id: int):
        return db.query(cls.orm_model).filter(cls.orm_model.id == id).first()

    def get_records(cls, db: Session, skip: int, limit: int):
       