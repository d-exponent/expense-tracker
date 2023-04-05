from psycopg2 import connect
from app.database.config import user, password, db


connection = connect(
    database=db, user=user, password=password, port="5432", host="localhost"
)
