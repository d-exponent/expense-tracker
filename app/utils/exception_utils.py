from fastapi import HTTPException


def raise_500_exception(message: str = "Something went wrong"):
    raise HTTPException(status_code=500, detail=message)


def raise_400_exception(message: str = "Bad request"):
    raise HTTPException(status_code=400, detail=message)


def raise_404_exception(message: str = "Not Found"):
    raise HTTPException(status_code=404, detail=message)


def handle_empty_records(records, table_name: str):
    if len(records) == 0:
        raise_404_exception(message=f"There are no {table_name} at this time.")
