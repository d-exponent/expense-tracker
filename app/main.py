import os
from fastapi import FastAPI
from app.routers import api_v1
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="My Expense tracker application",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1.router)


"""
Alternatively, RUN uvicorn app.main:app from CLI to start server at port 8000
For Debugging, RUN uvicorn app.main:app --reload from CLI
"""


if __name__ == "__main__":
    os.system("uvicorn app.main:app --reload")
