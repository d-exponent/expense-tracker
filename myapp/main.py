from fastapi import FastAPI
from myapp.routers import users, bills, creditors, payments, auth

app = FastAPI()

app.include_router(users.router)
app.include_router(bills.router)
app.include_router(creditors.router)
app.include_router(payments.router)
app.include_router(auth.router)
