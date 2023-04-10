from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Annotated

from app.database.sqlalchemy_config import SessionLocal


class DbContextManager:
    def __init__(self) -> None:
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.db.close()


def db_init():
    with DbContextManager() as db:
        yield db


dbSession = Annotated[Session, Depends(db_init)]
