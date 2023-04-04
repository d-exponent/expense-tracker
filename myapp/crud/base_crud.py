from sqlalchemy.orm import Session
from pydantic import BaseModel

from myapp.utils.error_utils import raise_bad_request_http_error
from myapp.utils.app_utils import remove_none_props_from_dict_recursive


class Crud:
    orm_model = None
    create_schema = None

    @classmethod
    def assert_item_schema(cls, item):
        assert isinstance(
            item, cls.create_schema
        ), f"{item} is not an instance of {cls.create_schema}"

    @classmethod
    def _get_by_id_query(cls, db: Session, id: int):
        return db.query(cls.orm_model).filter(cls.orm_model.id == id)

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
