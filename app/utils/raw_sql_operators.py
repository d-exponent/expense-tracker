from typing import Callable
from psycopg2.errors import OperationalError, DatabaseError

from app.database.psycopg_config import get_connection
from app.schema.creditor import CreditorOut
from app.schema.bill_payment import PaymentOut
from app.utils.custom_exceptions import QueryExecError


def map_to_creditor(result: tuple):
    return CreditorOut(
        id=result[0],
        name=result[1],
        description=result[2],
        street_address=result[3],
        city=result[4],
        state=result[5],
        country=result[6],
        phone=result[7],
        email=result[8],
        bank_name=result[9],
        account_number=result[10],
    )


def map_to_payment(result: tuple):
    return PaymentOut(
        id=result[0],
        bill_id=result[1],
        note=result[2],
        issuer=result[3],
        amount=result[4],
        created_at=result[5],
    )


def execute_query(query, params, mapper: Callable):
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(query, params)
            records = cur.fetchall()
            if len(records) == 0:
                yield records
            else:
                results = []
                for record in records:
                    results.append(mapper(record))
                yield results
    except (DatabaseError, OperationalError):
        raise QueryExecError
    finally:
        conn.close()
