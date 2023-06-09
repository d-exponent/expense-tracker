from bcrypt import gensalt, hashpw
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError, OperationalError

from app.crud.base_crud import Crud
from app.models import User as UserOrm
from app.utils.general import title_case_words
from app.schema.user import UserCreate
from app.utils.error_utils import RaiseHttpException
from app.utils.error_utils import handle_users_integrity_exception


class UserCrud(Crud):
    orm_model = UserOrm

    @classmethod
    def __hash_password(cls, password: str) -> bytes:
        password_bytes = password.encode("utf-8")
        return hashpw(password_bytes, gensalt())

    @classmethod
    def process(cls, user: UserCreate):
        user.first_name = title_case_words(user.first_name)
        user.middle_name = (
            title_case_words(user.middle_name) if user.middle_name else None
        )
        user.last_name = title_case_words(user.last_name)

        if user.password:
            user.password = cls.__hash_password(user.password)

        if user.email:
            user.email = user.email.lower()
        return user

    @classmethod
    def create(cls, db: Session, user: UserCreate) -> UserOrm:
        return super().create(db, data=cls.process(user))

    @classmethod
    def get_user_by_otp(cls, db: Session, otp: str) -> UserOrm:
        model = cls.orm_model
        return db.query(model).filter(model.otp == otp).first()

    @classmethod
    def update_user_by_phone(cls, db: Session, phone: str, update_data: dict):
        query = super().get_by_phone_query(db, phone)

        try:
            query.update(update_data)
        except IntegrityError as e:
            handle_users_integrity_exception(str(e))
        except (DataError, OperationalError):
            RaiseHttpException.server_error()
        else:
            db.commit()
            return super().get_by_phone(db, phone)

    @classmethod
    def update_user_password(cls, db: Session, user_id: int, new_password: str):
        hashed_password = cls.__hash_password(password=new_password)
        super().get_by_id_query(db=db, id=user_id).update({"password": hashed_password})
        db.commit()

    @classmethod
    def delete_me(cls, db: Session, id: int):
        query = super().get_by_id_query(db=db, id=id)
        query.update({"is_active": False})
        db.commit()
