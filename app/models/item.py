from typing import List
from pydantic import BaseModel
from app.models.pagination import ResponsePagination


class Item(BaseModel):

    id: str
    name: str
    content: str
    created_by: str

    class Config:
        orm_mode = True


class ItemWithPaging(BaseModel):
    data: List[Item]
    paging: ResponsePagination
