from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlalchemy.orm import Session

from myapp.models import Base
from myapp.database.sqlalchemy_config import engine
from myapp.utils import database, error_utils
from myapp.schema.payment import PaymentAllInfo
from myapp.crud.payments import PaymentCrud


Base.metadata.create_all(bind=engine)
db_instance = database.db_dependency


router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/", status_code=200, response_model=list[PaymentAllInfo])
def get_payments(
    db: Session = Depends(db_instance),
    skip: int = Query(default=0),
    limit: int = Query(default=100),
):
    try:
        payments = PaymentCrud.get_records(db=db, skip=skip, limit=limit)
    except Exception as e:
        print("🧰 Error", e)
        error_utils.raise_server_error()
    else:
        if len(payments) == 0:
            raise HTTPException(
                status_code=404, detail="There are no payments at this time"
            )

        return payments


@router.get("/{payment_id}", status_code=200, response_model=PaymentAllInfo)
def get_payment(payment_id: int = Path(), db: Session = Depends(db_instance)):
    try:
        payment = PaymentCrud.get_by_id(db=db, id=payment_id)
    except Exception as e:
        print("Error 🧰", e)
        error_utils.raise_server_error()
    else:
        return payment
