from fastapi import HTTPException


def raise_server_error(message: str = "Something went wrong"):
    raise HTTPException(status_code=500, detail=message)


def raise_bad_request_http_error(message: str = "Bad request"):
    raise HTTPException(status_code=400, detail=message)


def handle_empty_records(records, records_name: str):
    if len(records) == 0:
        raise HTTPException(
            status_code=404, detail=f"There are no {records_name} at this time."
        )
