from fastapi import HTTPException


def raise_server_error(message: str = "Something went wrong"):
    raise HTTPException(status_code=500, detail=message)
