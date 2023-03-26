from myapp.crud.base_crud import Crud

# from sqlalchemy.orm import Session
from myapp.models import Bill as BillOrm
from myapp.schema.bill import BillCreate
from myapp.database.psycopg_config import connection


class BillCrud(Crud):
    orm_model = BillOrm

    @classmethod
    def create(cls, bill: BillCreate):
        new_bill_params = (
            bill.user_id,
            bill.creditor_id,
            bill.starting_amount,
            bill.paid_amount,
            bill.description,
        )

        # Start the bill payment transaction
        try:
            connection.autocommit = False
            cursor = connection.cursor()

            # Create a new Bill
            insert_bill = """
                        INSERT INTO bills (user_id, creditor_id, starting_amount, paid_amount, description)
                        VALUES (%s, %s, %s, %s, %s);
                    """
            cursor.execute(insert_bill, new_bill_params)

            # Get the bill information for new Payment
            get_bill_query = (
                "Select id, paid_amount from bills Order by created_at desc limit 1;"
            )
            cursor.execute(get_bill_query)
            new_bill = cursor.fetchone()
            bill_id = new_bill[0]
            amount = new_bill[1]

            # Insert a new payment for this bill
            insert_payment_query = (
                " INSERT INTO payments (bill_id, amount) VALUES (%s,%s);"
            )
            cursor.execute(insert_payment_query, (bill_id, amount))
            connection.commit()

        except Exception:
            connection.rollback()
        finally:
            cursor.close()
            connection.close()
