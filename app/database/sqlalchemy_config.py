from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.database.config import user, password, db


db_url = f"postgresql://{user}:{password}@localhost:5432/{db}"

engine = create_engine(url)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()
