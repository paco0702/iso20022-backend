from typing import Optional

from pydantic import BaseModel


class Pagination(BaseModel):
    page_size: int
    count: int
    next_page_state: Optional[str]
    has_next: bool