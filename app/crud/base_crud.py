from sqlalchemy.orm import Session


class Crud:
    orm_model = None

    @classmethod
    def __process(cls, item):
        print("🧰🧰")
        pass

    @classmethod
    def create(cls, db: Session, item):
        processed_item = cls.__process(item)
        new_item = cls.orm_model(**processed_item.dict())

        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        return new_item

    @classmethod
    def get_by_id(cls, db: Session, id: int):
        return db.query(cls.orm_model).filter(cls.orm_model.id == id).first()

    @classmethod
    def get_records(cls, db: Session, skip: int, limit: int):
        return db.query(cls.orm_model).offset(skip).limit(limit).all()
