from fastapi import APIRouter

router = APIRouter()


@router.get("/users", tags=["users"])
def get_users():
    return "Users Routes"
