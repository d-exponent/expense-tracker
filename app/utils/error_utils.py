from fastapi import HTTPException


class RaiseHttpException:
    @classmethod
    def server_error(cls, msg: str = "Something went wrong!"):
        raise HTTPException(status_code=500, detail=msg)

    @classmethod
    def bad_request(cls, msg: str = "Bad Request!"):
        raise HTTPException(status_code=400, detail=msg)

    @classmethod
    def not_found(cls, msg: str = "Not Found!"):
        raise HTTPException(status_code=404, detail=msg)

    @classmethod
    def forbidden(cls, msg: str = "Forbidden!"):
        raise HTTPException(status_code=403, detail=msg)

    @classmethod
    def unauthorized(cls, msg: str = "Unauthorized!"):
        raise HTTPException(status_code=401, detail=msg)

    @classmethod
    def unauthorized_with_headers(
        cls,
        msg: str = "Unauthorized",
        headers=None,
    ):
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}
        raise HTTPException(status_code=401, detail=msg, headers=headers)


def ensure_positive_int(num: int):
    """Throws an HTTPException if the number is not a positive integer"""
    if num < 1:
        RaiseHttpException.bad_request("Provide a positive integer")


def handle_records(*, records=None, table_name: str):
    if records is None:
        records = []

    if len(records) == 0:
        raise HTTPException(
            status_code=404, detail=f"There are no {table_name} at this time."
        )

    return records


def handle_create_user_integrity_exception(error_message: str):
    if "users_password_email_ck" in error_message:
        RaiseHttpException.bad_request("Provide the email and password")

    if "users_phone_email_key" in error_message:
        RaiseHttpException.bad_request(
            "The phone number and email address are already in use"
        )

    if "users_email_key" in error_message:
        RaiseHttpException.bad_request("The email address is already in use")

    if "users_phone_key" in error_message:
        RaiseHttpException.bad_request("The phone number is already in use")

    RaiseHttpException.server_error()


def handle_create_bill_integrity_exception(error_message: str):
    if 'is not present in table "creditors"' in error_message:
        RaiseHttpException.bad_request("The creditor doesn't exist.")

    if 'is not present in table "users"' in error_message:
        RaiseHttpException.bad_request("The user does not exist")

    if "bills_user_id_creditor_id_key" in error_message:
        RaiseHttpException.bad_request(
            "A bill already exist between this user and the creditor"
        )

    RaiseHttpException.server_error()


def handle_create_creditor_integrity_exception(error_message: str):
    print("🛑🛑", error_message)
    if "creditors_name_key" in error_message:
        RaiseHttpException.bad_request("The creditor with this name already exists")

    if "creditors_account_number_bank_ck" in error_message:
        RaiseHttpException.bad_request(
            "Please provide an account number and a bank name."
        )

    if "account_number_key" in error_message:
        RaiseHttpException.bad_request(
            "The account number is already associated with a creditor"
        )

    if "creditors_email_key" in error_message:
        RaiseHttpException.bad_request(
            "This email is already associated with a creditor"
        )

    if "creditors_phone_key" in error_message:
        RaiseHttpException.bad_request(
            "This phone is already associated with a creditor"
        )

    if "creditors_phone_account_number_key" in error_message:
        RaiseHttpException.bad_request(
            "An account number can only be linked with one phone number"
        )

    RaiseHttpException.server_error()
