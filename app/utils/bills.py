from sqlalchemy.exc import IntegrityError

from app.schema import bill_payment as bp, response as r
from app.crud.bills import BillCrud
from app.utils.database import dbSession
from app.utils import error_utils as eu


def handle_make_bill(db: dbSession, bill: dict):
    try:
        new_bill = BillCrud.create(db, bill=bp.BillCreate(**bill))
    except IntegrityError as e:
        eu.handle_bills_integrity_exception((str(e)))
    else:
        return r.DefaultResponse(data=bp.BillOut.from_orm(new_bill))
