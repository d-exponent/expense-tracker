from fastapi import APIRouter

from app.models import Base
from app.database.sqlalchemy_config import engine
from app.routers import users, bills, creditors, payments, auth

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/api/v1")

router.include_router(users.router)
router.include_router(bills.router)
router.include_router(creditors.router)
router.include_router(payments.router)
router.include_router(auth.router)
