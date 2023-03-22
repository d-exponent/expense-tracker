import bcrypt
from decouple import config
from sqlalchemy.orm import Session
from myapp.schema.user import UserCreate
from myapp.crud.base_crud import Crud
from myapp.models import User


def generate_hash(password):
    encoded = password.encode(config("ENCODE_FMT"))
    salt = bcrypt.gensalt(int(config("SALT")))
    return bcrypt.hashpw(encoded, salt)


class UserCrud(Crud):
    model = User

    @classmethod
    def create_user(cls, db: Session, user: UserCreate):
        if user.password:
            user.password = generate_hash(user.password)
        db_user = User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @classmethod
    def get_user_by_phone(cls, db: Session, phone: str):
        return db.query(cls.model).filter(cls.model.phone == phone).first()

    @classmethod
    def get_user_by_email(cls, db: Session, email: str):
        return db.query(cls.model).filter(cls.model.email == email).first()
