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


raise_400_exception = RaiseHttpException.bad_request


def ensure_positive_int(num: int):
    """Throws an HTTPException if the number is not a positive integer"""
    if num < 1:
        raise_400_exception("Provide a positive integer")


def handle_records(*, records=[], table_name: str):
    if len(records) == 0:
        RaiseHttpException.not_found(f"There are no {table_name} at this time.")

    return records


def handle_users_integrity_exception(error_message: str):
    if "users_password_email_ck" in error_message:
        raise_400_exception("Provide the email and password")

    if "users_phone_email_key" in error_message:
        raise_400_exception("The phone number and email address are already in use")

    if "users_email_key" in error_message:
        raise_400_exception("The email address is already in use")

    if "users_phone_key" in error_message:
        raise_400_exception("The phone number is already in use")

    RaiseHttpException.server_error()


def handle_bills_integrity_exception(error_message: str):
    if 'is not present in table "creditors"' in error_message:
        raise_400_exception("The creditor doesn't exist.")

    if 'is not present in table "users"' in error_message:
        raise_400_exception("The user does not exist")

    if "bills_user_id_creditor_id_key" in error_message:
        raise_400_exception("A bill already exist between this user and the creditor")

    RaiseHttpException.server_error()


def handle_creditors_integrity_exception(error_message: str):
    if "creditors_name_key" in error_message:
        raise_400_exception("The creditor with this name already exists")

    if "creditors_account_number_bank_ck" in error_message:
        raise_400_exception("Please provide an account number and a bank name.")

    if "creditors_owner_id_fkey" in error_message:
        raise_400_exception("The owner_id does not reference a valid user")

    if "account_number_key" in error_message:
        raise_400_exception("The account number is already associated with a creditor")

    if "creditors_email_key" in error_message:
        raise_400_exception("This email is already associated with a creditor")

    if "creditors_phone_key" in error_message:
        raise_400_exception("This phone is already associated with a creditor")

    if "creditors_phone_account_number_key" in error_message:
        raise_400_exception(
            "An account number can only be linked with one phone number"
        )
    # Unlikely to be needed as createCreditor pydantic schema ensures an owner_id value
    #   if "null value in column \"owner_id\"" in error_message:
    #       raise_400_exception("Provide the owner_id (user id) for this creditor")

    RaiseHttpException.server_error()
