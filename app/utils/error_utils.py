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


def handle_records(*, records=None, table_name: str):
    if records is None:
        records = []

    if len(records) == 0:
        raise HTTPException(
            status_code=404, detail=f"There are no {table_name} at this time."
        )

    return records


def handle_users_integrity_exceptions(error_message: str):
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
