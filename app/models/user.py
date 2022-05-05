from typing import Optional, List
from pydantic import BaseModel
from app.models.pagination import ResponsePagination


class User(BaseModel):
    id: str
    name: str
    email: str

    class Config:
        orm_mode = True
