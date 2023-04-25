from pydantic import BaseModel
from typing import Any


class DefaultResponse(BaseModel):
    success: bool = True
    message: str = "Success!"
    data: Any = None
