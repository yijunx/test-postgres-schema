from typing import Optional
from pydantic import BaseModel


class QueryPagination(BaseModel):
    page: Optional[int]
    size: Optional[int]


class ResponsePagination(BaseModel):
    total: int
    page_size: int
    current_page: int
    total_pages: int
