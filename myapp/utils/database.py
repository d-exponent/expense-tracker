from myapp.database.sqlalchemy_config import SessionLocal


def db_dependency():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
