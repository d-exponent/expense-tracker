from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

user = config("DB_USERNAME")
password = config("DB_PASSWORD")
db = "expense-tracker-test"


engine = create_engine(f"postgresql://{user}:{password}@localhost:5432/{db}")

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()
