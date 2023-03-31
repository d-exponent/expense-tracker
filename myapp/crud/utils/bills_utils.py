from datetime import datetime

BILL_TYPES = int | str | float | datetime


# UTILITY CLASSES
class BillTransactionError(Exception):
    pass


class TransactionQueries:
    insert_bill = """
            INSERT INTO bills
                (user_id, creditor_id, starting_amount, paid_amount, description)
            VALUES
                (%(user_id)s, %(creditor_id)s, %(starting_amount)s, %(paid_amount)s, %(description)s);
            """

    insert_payment = """
                    INSERT INTO payments (bill_id, amount, first_payment)
                    VALUES (%(bill_id)s,%(amount)s, %(first_payment)s);
                    """

    get_new_bill = "SELECT id, paid_amount FROM bills ORDER BY created_at DESC LIMIT 1;"

    get_bills_user_creditor_join = """
                    SELECT
                        b.id, b.user_id, CONCAT(u.first_name, ' ', u.last_name),
                        b.creditor_id, c.name,b.starting_amount, b.paid_amount, b.paid,
                        b.description, b.current_balance, b.created_at, b.updated_at, p.id
                    FROM bills AS b
                    JOIN users AS u ON u.id = %(user_id)s
                    JOIN creditors as c ON c.id = %(creditor_id)s
                    JOIN payments AS p ON p.bill_id = b.id
                    ORDER BY created_at DESC
                    LIMIT 1;
                    """


# UTILITY FUNCTIONS
def describe_balance(balance: int | int, user_names: str, creditor_name: str) -> str:
    if balance == 0:
        return f"There is no debt between {user_names} and {creditor_name}"

    if balance > 0:
        return f"{creditor_name} owes {user_names} {balance}"

    if balance < 0:
        return f"{user_names} owes {creditor_name} {balance * -1}"


def map_record_to_dict(sql_recored: tuple) -> dict[str, BILL_TYPES]:
    return {
        "bill_id": sql_recored[0],
        "user": {
            "user_id": sql_recored[1],
            "user_names": sql_recored[2],
        },
        "creditor": {
            "creditor_id": sql_recored[3],
            "creditor_name": sql_recored[4],
        },
        "starting_amount": sql_recored[5],
        "paid_amount": sql_recored[6],
        "balance_detail": describe_balance(
            balance=sql_recored[9],
            user_names=sql_recored[2],
            creditor_name=sql_recored[4],
        ),
        "paid": sql_recored[7],
        "description": sql_recored[8],
        "current_balance": sql_recored[9],
        "created_at": sql_recored[10],
        "last_updated": sql_recored[11],
        "payment_record_id": sql_recored[12],
    }


def handle_transaction_exceptions(error_message) -> None:
    if "bills_creditor_id_fkey" in error_message:
        raise BillTransactionError("The Creditor ID is invalid")

    if "bills_user_id_creditor_id_key" in error_message:
        raise BillTransactionError(
            "There is an existing bill for this user and the creditor"
        )

    if "bills_user_id_fkey" in error_message:
        raise BillTransactionError("The user ID is invalid")

    raise Exception
