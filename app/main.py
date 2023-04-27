from fastapi import FastAPI
from app.routers import api_v1
import os


app = FastAPI(
    title="My Expense tracker application",
    version="1.0",
)

app.include_router(api_v1.router)


def run():
    os.system("uvicorn app.main:app --reload")


"""
Alternatively, RUN uvicorn app.main:app from CLI to start server at port 8000
For Debugging, RUN uvicorn app.main:app --reload from CLI
"""
if __name__ == "__main__":
    run()
