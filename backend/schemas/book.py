from pydantic import BaseModel
from typing import Optional
from enum import Enum

class StorageType(str, Enum):
    online = "online"
    offline = "offline"

class DashboardStats(BaseModel):
    total_books: int
    total_books_last_month: int
    active_borrowers: int
    active_borrowers_last_month: int
    total_categories: int
    total_categories_last_month: int
    pending_fines: float
    pending_fines_last_month: float

class BookCreate(BaseModel):
    title: str
    author: str
    publisher: str
    published_year: int
    language: str
    isbn: Optional[str]
    cover_image: Optional[str]
    category_id: int
    tags: Optional[str]
    storage_type: str
    online_address: Optional[str]
    platform_name: Optional[str]
    access_url: Optional[str]
    format: Optional[str]
    quantity: Optional[int]
    offline_address: Optional[str]
    shelf_no: Optional[str]
    room: Optional[str]
    added_by: Optional[str]

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    category: str
    storage_type: str
    isbn: Optional[str]
    publisher: str
    published_year: int
    language: str
    cover_image: Optional[str]
    rating: int
    quantity: Optional[int] = None
    access_url: Optional[str] = None
    platform_name: Optional[str] = None
