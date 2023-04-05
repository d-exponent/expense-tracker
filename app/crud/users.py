from sqlalchemy.orm import Session
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
        user.country_code = user.country_code.replace("+", "")

        if user.password:
            user.password = hash_password(user.password)

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
    def get_user_by_phone(cls, db: Session, phone: str):
        return (
            db.query(cls.orm_model).filter(cls.orm_model.phone_number == phone).first()
        )

    @classmethod
    def get_user_by_email(cls, db: Session, email: str):
        return (
            db.query(cls.orm_model).filter(cls.orm_model.email_address == email.lower()).first()
        )
