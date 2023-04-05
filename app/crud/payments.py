from app.crud.base_crud import Crud
from app.models import Payment as PaymentOrm


class PaymentCrud(Crud):
    orm_model = PaymentOrm
