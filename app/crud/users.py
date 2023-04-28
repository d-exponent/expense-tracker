from sqlalchemy.orm import Session
from bcrypt import gensalt, hashpw

from app.crud.base_crud import Crud
from app.models import User as UserOrm
from app.utils.general import to_title_case
from app.schema.user import UserCreate
from app.utils import custom_exceptions as ce


class UserCrud(Crud):
    orm_model = UserOrm

    @classmethod
    def __hash_password(cls, password: str) -> bytes:
        password_bytes = password.encode("utf-8")
        return hashpw(password_bytes, gensalt())

    @classmethod
    def __process(cls, user: UserCreate):
        user.first_name = to_title_case(user.first_name)
        user.middle_name = to_title_case(user.middle_name) if user.middle_name else None
        user.last_name = to_title_case(user.last_name)

        if user.password:
            user.password = cls.__hash_password(user.password)

        if user.email:
            user.email = user.email.lower()

        return user

    @classmethod
    def create(cls, db: Session, user: UserCreate) -> UserOrm:
        processed_user = cls.__process(user)
        new_user = cls.orm_model(**processed_user.dict())
        return cls.commit_data_to_db(db=db, data=new_user)

    @classmethod
    def __get_user_by_phone_query(cls, db: Session, phone: str):
        return db.query(cls.orm_model).filter(cls.orm_model.phone == phone)

    @classmethod
    def get_user_by_phone(cls, db: Session, phone: str) -> UserOrm:
        return cls.__get_user_by_phone_query(db, phone).first()

    @classmethod
    def get_user_by_email(cls, db: Session, email: str) -> UserOrm:
        return (
            db.query(cls.orm_model).filter(cls.orm_model.email == email.lower()).first()
        )

    @classmethod
    def get_user_by_otp(cls, db: Session, otp: str) -> UserOrm:
        return db.query(cls.orm_model).filter(cls.orm_model.otp == otp).first()

    @classmethod
    def update_user_by_phone(
        cls, db: Session, phone: str, update_data: dict
    ) -> UserOrm:
        query = cls.__get_user_by_phone_query(db, phone)
        query.update(update_data)
        db.commit()
        return query.first()

    @classmethod
    def update_user_password(cls, db: Session, user_id: int, new_password: str):
        hashed_password = cls.__hash_password(password=new_password)
        cls.get_by_id_query(db=db, id=user_id).update({"password": hashed_password})
        db.commit()

    @classmethod
    def handle_delete_me(cls, db: Session, id: int):
        query = cls.get_by_id_query(db=db, id=id)

        if query.first() is None:
            raise ce.UserNotFoundException

        query.update({"is_active": False})
        db.commit()
