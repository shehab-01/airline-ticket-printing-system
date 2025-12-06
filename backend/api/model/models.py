from fastapi import status
from typing import Union, Optional, List
from pydantic import BaseModel, ValidationError

class ResData(BaseModel):
    status: int = status.HTTP_200_OK
    msg: Optional[str] = None