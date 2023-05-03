from sqlalchemy.orm import Session

from app.utils.error_utils import RaiseHttpException
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
    def get_by_id(cls, db: Session, id: int):
        return cls.get_by_id_query(db, id).first()

    @classmethod
    def get_by_phone_query(cls, db: Session, phone: str):
        return db.query(cls.orm_model).filter(cls.orm_model.phone == phone)

    @classmethod
    def get_by_phone(cls, db: Session, phone: str):
        return cls.get_by_phone_query(db, phone).first()

    @classmethod
    def get_by_email(cls, db: Session, email: str):
        return db.query(cls.orm_model).filter(cls.orm_model.email == email.lower()).first()

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
    def update_by_id(cls, db: Session, id: int, data: dict, table_name: str):
        query = cls.get_by_id_query(db, id)

        if query.first() is None:
            message = f"There is no {table_name.rstrip('s')} with an id {id}"
            RaiseHttpException.bad_request(message)

        query.update(rnd(data), synchronize_session=False)
        db.commit()
        return query.first()

    @classmethod
    def delete_by_id(cls, db: Session, id: int, record_name: str = "record"):
        query = cls.get_by_id_query(db, id)

        if query.first() is None:
            RaiseHttpException.bad_request(msg=f"This {record_name} doesn't exist.")

        query.delete()
        db.commit()
