from pydantic import BaseModel
from app.models.pagination import QueryPagination
from typing import Optional


class ItemCreate(BaseModel):

    name: str
    desc: str
    content: str


class ItemPatch(ItemCreate):
    pass


class ItemQuery(QueryPagination):
    name: Optional[str]
