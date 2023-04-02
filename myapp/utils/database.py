from myapp.database.sqlalchemy_config import SessionLocal


def db_init():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
