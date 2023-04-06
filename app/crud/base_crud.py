from sqlalchemy.orm import Session

from app.utils.error_utils import raise_bad_request_http_error
from app.utils.app_utils import remove_none_props_from_dict_recursive


class Crud:
    orm_model = None
    create_schema = None

    @classmethod
    def __process(cls, item):
        pass

    @classmethod
    def create(cls, db: Session, item):
        pass

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
            raise_bad_request_http_error(
                message=f"There is no {model_name_repr} with an id = {id}"
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
            raise_bad_request_http_error(message="This record doesn't exist.")

        query.delete()
        db.commit()
