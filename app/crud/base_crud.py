from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError, OperationalError

from app.utils import error_utils as eu
from app.utils.general import remove_none_props_from_dict_recursive as rnd


class Crud:
    orm_model = None

    @classmethod
    def create(cls, db: Session, data):
        new_data = cls.orm_model(**data.__dict__)
        return cls.commit_data_to_db(db=db, data=new_data)

    @classmethod
    def get_by_id_query(cls, db: Session, id: int):
        return db.query(cls.orm_model).filter(cls.orm_model.id == id)

    @classmethod
    def get_by_phone_query(cls, db: Session, phone: str):
        return db.query(cls.orm_model).filter(cls.orm_model.phone == phone)

    @classmethod
    def get_by_id(cls, db: Session, id: int):
        return cls.get_by_id_query(db, id).first()

    @classmethod
    def get_by_phone(cls, db: Session, phone: str):
        return cls.get_by_phone_query(db, phone).first()

    @classmethod
    def get_by_email(cls, db: Session, email: str):
        return (
            db.query(cls.orm_model).filter(cls.orm_model.email == email.lower()).first()
        )

    @classmethod
    def commit_data_to_db(cls, db: Session, data):
        db.add(data)
        db.commit()
        db.refresh(data)
        return data

    @classmethod
    def get_records(cls, db: Session, skip: int, limit: int):
        return db.query(cls.orm_model).offset(skip).limit(limit).all()

    @classmethod
    def update_by_id(cls, db: Session, id: int, data: dict, table: str):
        query = cls.get_by_id_query(db, id)

        if query.first() is None:
            message = f"There is no {table.rstrip('s')} with an id {id}"
            eu.RaiseHttpException.bad_request(message)

        try:
            query.update(rnd(data), synchronize_session=False)

        except IntegrityError as e:
            if 'users_' in str(e):  # An error in updating users table
                eu.handle_users_integrity_exception(str(e))
            else:
                msg = 'The data violates set constraints. Check the data and try again'
                eu.RaiseHttpException.bad_request(msg)

        except (DataError, OperationalError):
            msg = "Could not perform the update operation. Please try again!"
            eu.RaiseHttpException.server_error(msg)

        else:
            db.commit()
            return cls.get_by_id(db, id)

    @classmethod
    def delete_by_id(cls, db: Session, id: int, table: str = "record"):
        query = cls.get_by_id_query(db, id)

        if query.first() is None:
            msg = f"This {table.rstrip('s')} doesn't exist."
            eu.RaiseHttpException.bad_request(msg)

        query.delete()
        db.commit()
