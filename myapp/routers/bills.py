from fastapi import APIRouter, Body, Depends, Query, Path, HTTPException
from sqlalchemy.orm import Session

from myapp.crud.bills import BillCrud, CustomBillOut, BillTransactionError
from myapp.models import Base
from myapp.database.sqlalchemy_config import engine
from myapp.utils import database
from myapp.schema.bill import BillCreate, BillOut
from myapp.utils.error_utils import raise_server_error

Base.metadata.create_all(bind=engine)
db_instance = database.db_dependency

router = APIRouter(prefix="/bills", tags=["bills", "debts"])


@router.post("/", response_model=CustomBillOut, status_code=201)
def make_bill(bill: BillCreate = Body()):
    try:
        return BillCrud.create(bill=bill)
    except BillTransactionError as e:
        raise_server_error(str(e))
    except Exception:
        raise_server_error()


@router.get("/", response_model=list[BillOut], status_code=200)
def get_bills(
    db: Session = Depends(db_instance),
    skip: int = Query(default=0),
    limit: int = Query(default=100),
):
    try:
        bills = BillCrud.get_records(db, skip, limit)
    except Exception as e:
        print("🧰 Error", e)
        raise_server_error()
    else:
        if len(bills) == 0:
            raise HTTPException(
                status_code=404, detail="There are no bills at this time"
            )
        return bills


@router.get("/{bill_id}", response_model=BillOut, status_code=200)
def get_bill(bill_id: int = Path(), db: Session = Depends(db_instance)):
    try:
        bill = BillCrud.get_by_id(db=db, id=bill_id)
    except Exception as e:
        print("🧰 Error", e)
        raise_server_error()
    else:
        return bill
