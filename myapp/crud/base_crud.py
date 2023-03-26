from sqlalchemy.orm import Session


class Crud:
    orm_model = None

    @classmethod
    def __process(cls, item):
        pass

    @classmethod
    def create(cls, db: Session, item):
        pass

    @classmethod
    def get_by_id(cls, db: Session, id: int):
        return db.query(cls.orm_model).filter(cls.orm_model.id == id).first()

    @classmethod
    def get_records(cls, db: Session, skip: int, limit: int):
        return db.query(cls.orm_model).offset(skip).limit(limit).all()
