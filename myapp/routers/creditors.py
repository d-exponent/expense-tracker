from fastapi import APIRouter

router = APIRouter()


@router.get("/creditors", tags=["creditors"])
def get_users():
    return "Creditors Routes"
