from sqlalchemy.orm import Session
from myapp.schema.user import UserCreate
from myapp.crud.base_crud import Crud
from myapp.models import User as UserOrm
from myapp.crud.utils import hash


class UserCrud(Crud):
    orm_model = UserOrm

    @classmethod
    def __process(cls, user: UserCreate):
        user.first_name = user.first_name.title()
        user.middle_name = user.middle_name.title() if user.middle_name else None
        user.last_name = user.last_name.title()

        if user.password:
            user.password = hash(user.password)

        return user

    @classmethod
    def create(cls, db: Session, user: UserCreate):
        processed_user = cls.__process(user)
        new_user = cls.orm_model(**processed_user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @classmethod
    def get_user_by_phone(cls, db: Session, phone: str):
        return db.query(cls.orm_model).filter(cls.orm_model.phone == phone).first()

    @classmethod
    def get_user_by_email(cls, db: Session, email: str):
        return db.query(cls.orm_model).filter(cls.orm_model.email == email).first()
