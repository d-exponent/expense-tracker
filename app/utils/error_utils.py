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
        headers: dict = {"WWW-Authenticate": "Bearer"},
    ):
        raise HTTPException(status_code=401, detail=msg, headers=headers)


def handle_empty_records(records, records_name: str):
    if len(records) == 0:
        raise HTTPException(
            status_code=404, detail=f"There are no {records_name} at this time."
        )
