from fastapi import APIRouter

from myapp.models import Base
from myapp.database.sqlalchemy_config import engine
from myapp.routers import users, bills, creditors, payments, auth

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/api/v1")

router.include_router(users.router)
router.include_router(bills.router)
router.include_router(creditors.router)
router.include_router(payments.router)
router.include_router(auth.router)
