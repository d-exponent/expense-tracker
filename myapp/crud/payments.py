from myapp.crud.base_crud import Crud
from myapp.models import Payment as PaymentOrm


class PaymentCrud(Crud):
    orm_model = PaymentOrm
