from decouple import config
from sqlalchemy.orm import Session
from bcrypt import gensalt, hashpw

from app.crud.base_crud import Crud
from app.models import User as UserOrm
from app.utils.app_utils import to_title_case
from app.schema.user import UserCreate, UserAllInfo
from app.utils.error_utils import RaiseHttpException


class UserCrud(Crud):
    orm_model = UserOrm

    @classmethod
    def __hash_password(cls, password: str) -> bytes:
        password_bytes = password.encode(config("ENCODE_FMT"))
        return hashpw(password_bytes, gensalt())

    @classmethod
    def __process(cls, user: UserCreate):
        user.first_name = to_title_case(user.first_name)
        user.middle_name = to_title_case(user.middle_name) if user.middle_name else None
        user.last_name = to_title_case(user.last_name)

        if user.password:
            user.password = cls.__hash_password(user.password)

        if user.email_address:
            user.email_address = user.email_address.lower()

        return user

    @classmethod
    def create(cls, db: Session, user: UserCreate) -> UserAllInfo:
        processed_user = cls.__process(user)
        new_user = cls.orm_model(**processed_user.dict())
        return cls.commit_data_to_db(db=db, data=new_user)

    @classmethod
    def __get_user_by_phone_query(cls, db: Session, phone: str):
        return db.query(cls.orm_model).filter(cls.orm_model.phone_number == phone)

    @classmethod
    def get_user_by_phone(cls, db: Session, phone: str):
        return cls.__get_user_by_phone_query(db, phone).first()

    @classmethod
    def get_user_by_email(cls, db: Session, email: str):
        return (
            db.query(cls.orm_model)
            .filter(cls.orm_model.email_address == email.lower())
            .first()
        )

    @classmethod
    def get_user_by_otp(cls, db: Session, otp: str):
        return db.query(cls.orm_model).filter(cls.orm_model.mobile_otp == otp).first()

    @classmethod
    def update_user_by_phone(cls, db: Session, phone: str, update_data: dict):
        cls.__get_user_by_phone_query(db, phone).update(update_data)
        db.commit()

    @classmethod
    def handle_user_if_exists(cls, db: Session, phone: str):
        if cls.get_user_by_phone(db, phone) is not None:
            RaiseHttpException.bad_request(msg="The user already exists")

    @classmethod
    def update_user_password(cls, db: Session, user_id: int, new_password: str):
        hashed_password = cls.__hash_password(password=new_password)
        cls.get_by_id_query(db=db, id=user_id).update({"password": hashed_password})
        db.commit()
