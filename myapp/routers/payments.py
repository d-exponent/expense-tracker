from fastapi import APIRouter

router = APIRouter()


@router.get("/payments", tags=["payments"])
def get_users():
    return "Payments Routes"
