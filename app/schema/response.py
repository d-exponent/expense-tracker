from typing import Any
from pydantic import BaseModel


class DefaultResponse(BaseModel):
    success: bool = True
    message: str = "Success!"
    data: Any = None
