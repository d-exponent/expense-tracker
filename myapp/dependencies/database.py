from myapp.database import SessionLocal


def db_dependency():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
