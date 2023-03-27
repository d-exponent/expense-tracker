from psycopg2 import connect

from myapp.crud.base_crud import Crud
from myapp.database.config import user, password, db
from myapp.models import Bill as BillOrm
from myapp.schema.bill import BillCreate, CustomBillOut
from myapp.crud.utils.bills_utils import (
    BILLTYPES,
    map_record_to_dict,
    handle_exceptions,
    TransactionQueries,
    BillTransactionError,  # Just so the bill router can access from this module
)


class BillCrud(Crud):
    orm_model = BillOrm

    @classmethod
    def create(cls, bill: BillCreate):
        bill_data_dict: dict[str, BILLTYPES] = {
            "user_id": bill.user_id,
            "creditor_id": bill.creditor_id,
            "starting_amount": bill.starting_amount,
            "paid_amount": bill.paid_amount,
            "description": bill.description,
        }

        # Start the bill payment transaction
        try:
            connection = connect(
                database=db, user=user, password=password, port="5432", host="localhost"
            )
            connection.autocommit = False
            cursor = connection.cursor()

            cursor.execute(TransactionQueries.insert_bill, bill_data_dict)

            # Get the new bill information
            cursor.execute(TransactionQueries.get_new_bill)
            new_bill_record = cursor.fetchone()

            # Insert a new payment with the new bill information
            cursor.execute(
                TransactionQueries.insert_payment,
                {"bill_id": new_bill_record[0], "amount": new_bill_record[1]},
            )

            # Lets return some information to the user with a join
            join_params = {
                "user_id": bill_data_dict["user_id"],
                "creditor_id": bill_data_dict["creditor_id"],
                "bill_id": new_bill_record[0],
            }

            cursor.execute(TransactionQueries.get_bills_user_creditor_join, join_params)
            joined_data = cursor.fetchone()
        except Exception as e:
            connection.rollback()
            handle_exceptions(str(e))
        else:
            cursor.close()
            connection.commit()
            return CustomBillOut(**map_record_to_dict(joined_data))
        finally:
            connection.close()
