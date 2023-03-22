from sqlalchemy.orm import Session


class Crud:
    model = None

    @classmethod
    def get_by_id(cls, db: Session, id: int):
        return db.query(cls.model).filter(cls.model.id == id).first()

    @classmethod
    def get_records(cls, db: Session, skip: int, limit: int):
        return db.query(cls.model).offset(skip).limit(limit).all()
