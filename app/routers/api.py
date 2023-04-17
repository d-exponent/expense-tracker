from fastapi import APIRouter
from app.routers import users, bills, creditors, payments, auth, login

router = APIRouter(prefix="/api")


router.include_router(users.router)
router.include_router(bills.router)
router.include_router(creditors.router)
router.include_router(payments.router)
router.include_router(login.router)
router.include_router(auth.router)
