from pydantic import BaseModel
from datetime import date

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: date
    book_count: int