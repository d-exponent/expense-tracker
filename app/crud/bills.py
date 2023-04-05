from psycopg2 import connect

from app.crud.base_crud import Crud
from app.database.config import user, password, db
from app.models import Bill as BillOrm
from app.schema.bill import BillCreate, CustomBillOut
from app.crud.utils.bills_utils import (
    BILL_TYPES,
    map_record_to_dict,
    handle_transaction_exceptions,
    TransactionQueries,
    BillTransactionError,  # Just so the bill router can accessed from this module
)


class BillCrud(Crud):
    orm_model = BillOrm

    @classmethod
    def create(cls, bill: BillCreate):
        bill_data_dict: dict[str, BILL_TYPES] = {
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

            # 1. Insert a new bill
            cursor.execute(TransactionQueries.insert_bill, bill_data_dict)

            # 2.  Get the new bill information
            cursor.execute(TransactionQueries.get_new_bill)
            new_bill_record = cursor.fetchone()

            insert_payment_params = {
                "bill_id": new_bill_record[0],
                "amount": new_bill_record[1],
                "first_payment": True,
            }

            # 3. Insert a new payment with the new bill information
            cursor.execute(TransactionQueries.insert_payment, insert_payment_params)

        except Exception as e:
            connection.rollback()
            handle_transaction_exceptions(str(e))
        else:
            connection.commit()

            # Return some information to the user with a join
            cursor.execute(
                TransactionQueries.get_bills_user_creditor_join,
                {
                    "user_id": bill_data_dict["user_id"],
                    "creditor_id": bill_data_dict["creditor_id"],
                    "bill_id": new_bill_record[0],
                },
            )

            joined_data = cursor.fetchone()
            cursor.close()
            return CustomBillOut(**map_record_to_dict(joined_data))
        finally:
            connection.close()
