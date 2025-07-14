from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import date

class StorageType(str, Enum):
    online = "online"
    offline = "offline"

class Category(BaseModel):
    id: int
    name: str
    description: str
    created_at: date

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: date
    book_count: int

class Book(BaseModel):
    id: int
    title: str
    author: str
    category_id: int
    storage_type: str
    isbn: Optional[str]
    publisher: str
    published_year: int
    language: str
    cover_image: Optional[str]
    quantity: Optional[int] = None
    access_url: Optional[str] = None
    platform_name: Optional[str] = None

class BookOnline(BaseModel):
    id: int
    address: str
    platform_name: str
    access_url: str
    format: str

class BookOffline(BaseModel):
    id: int
    quantity: int
    address: str
    shelf_no: str
    room: str