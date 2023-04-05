from fastapi import FastAPI
from app.routers import api_v1


app = FastAPI()

app.include_router(api_v1.router)
