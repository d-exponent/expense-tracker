from fastapi import APIRouter


router = APIRouter()


@router.get("/bills", tags=["bills"])
def get_users():
    return "Bills Routes"
