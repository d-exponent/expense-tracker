from psycopg2 import connect
from app.settings import settings


def get_connection():
    return connect(
        database=settings.db_name,
        user=settings.db_username,
        password=settings.db_password,
        port=settings.db_port,
        host=settings.db_host,
    )
