from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from myapp.database.config import user, password, db


engine = create_engine(f"postgresql://{user}:{password}@localhost:5432/{db}")

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()
