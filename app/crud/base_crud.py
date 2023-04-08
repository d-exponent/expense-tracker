from sqlalchemy.orm import Session

from app.utils.error_utils import RaiseHttpException
from app.utils.app_utils import remove_none_props_from_dict_recursive


class Crud:
    orm_model = None

    @classmethod
    def commit_data_to_db(cls, db: Session, data):
        db.add(data)
        db.commit()
        db.refresh(data)
        return data

    @classmethod
    def get_by_id(cls, db: Session, id: int):
        return cls._get_by_id_query(db, id).first()

    @classmethod
    def get_records(cls, db: Session, skip: int, limit: int):
        return db.query(cls.orm_model).offset(skip).limit(limit).all()

    @classmethod
    def update_by_id(cls, db: Session, id: int, data: dict, model_name_repr: str):
        query = cls._get_by_id_query(db, id)

        if query.first() is None:
            RaiseHttpException.bad_request(
                f"There is no {model_name_repr} with an id = {id}"
            )

        query.update(
            remove_none_props_from_dict_recursive(data),
            synchronize_session=False,
        )

        db.commit()
        return query.first()

    @classmethod
    def delete_by_id(cls, db: Session, id: int):
        query = cls._get_by_id_query(db, id)

        if query.first() is None:
            RaiseHttpException.bad_request(msg="This record doesn't exist.")

        query.delete()
        db.commit()
