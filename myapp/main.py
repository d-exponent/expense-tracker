from fastapi import FastAPI
from myapp.routers import api_v1
import uvicorn


app = FastAPI(
    title="My Expense tracker application",
    version="0.1.0",
)

app.include_router(api_v1.router)


"""
Alternatively, RUN uvicorn myapp.main:app from CLI to start server at port 8000
For Debugging, RUN uvicorn myapp.main:app --reload from CLI
"""
if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000)
