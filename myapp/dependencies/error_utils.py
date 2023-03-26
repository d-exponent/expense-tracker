from fastapi import HTTPException


def raise_server_error():
    raise HTTPException(status_code=500, detail="Something went wrong")
