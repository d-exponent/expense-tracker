from sqlalchemy.orm import Session
from fastapi import HTTPException
from decouple import config
from bcrypt import gensalt, hashpw

from app.schema.user import UserCreate, UserAllInfo
from app.crud.base_crud import Crud
from app.models import User as UserOrm


def hash_password(password: str) -> bytes:
    password_bytes = password.encode(config("ENCODE_FMT"))
    return hashpw(password_bytes, gensalt())


class UserCrud(Crud):
    orm_model = UserOrm

    @classmethod
    def __process(cls, user: UserCreate):
        user.first_name = user.first_name.title()
        user.middle_name = user.middle_name.title() if user.middle_name else None
        user.last_name = user.last_name.title()

        if user.password:
            user.password = cls._hash_password(user.password)

        if user.email_address:
            user.email_address = user.email_address.lower()

        return user

    @classmethod
    def create(cls, db: Session, user: UserCreate) -> UserAllInfo:
        processed_user = cls.__process(user)
        new_user = cls.orm_model(**processed_user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @classmethod
    def __get_user_by_phone_query(cls, db: Session, phone: str):
        return db.query(cls.orm_model).filter(cls.orm_model.phone_number == phone)

    @classmethod
    def __get_user_by_otp_query(cls, db: Session, otp: str):
        return db.query(cls.orm_model).filter(cls.orm_model.mobile_otp == otp)

    @classmethod
    def __get_user_by_email_query(cls, db: Session, email: str):
        return db.query(cls.orm_model).filter(
            cls.orm_model.email_address == email.lower()
        )

    @classmethod
    def __get_user_by_phone_query(cls, db: Session, phone: str):
        return db.query(cls.orm_model).filter(cls.orm_model.phone_number == phone)

    @classmethod
    def __get_user_by_otp_query(cls, db: Session, otp: str):
        return db.query(cls.orm_model).filter(cls.orm_model.mobile_otp == otp)

    @classmethod
    def __get_user_by_email_query(cls, db: Session, email: str):
        return db.query(cls.orm_model).filter(
            cls.orm_model.email_address == email.lower()
        )

    @classmethod
    def get_user_by_phone(cls, db: Session, phone: str):
        return cls.__get_user_by_phone_query(db, phone).first()

    @classmethod
    def get_user_by_email(cls, db: Session, email: str):
        return cls.__get_user_by_email_query(db, email).first()

    @classmethod
    def get_user_by_otp(cls, db: Session, otp: str):
        return cls.__get_user_by_otp_query(db, otp).first()

    @classmethod
    def update_user_by_phone(cls, db: Session, phone: str, update_data: dict):
        cls.__get_user_by_phone_query(db, phone).update(update_data)
        db.commit()
