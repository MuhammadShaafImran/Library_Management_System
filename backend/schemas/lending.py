from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import date

class BorrowStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class BorrowerResponse(BaseModel):
    id: int
    name: str
    email: str
    user_type: str
    phone: Optional[str]
    status: str
    last_login: Optional[date]
    joining_date: date
    books_borrowed: int
    department: Optional[str] = None
    rollno: Optional[int] = None
    batch: Optional[int] = None
    semester: Optional[int] = None
    designation: Optional[str] = None
    # Borrow-specific fields
    book_id: Optional[int] = None
    request_description: Optional[str] = None
    request_date: Optional[date] = None
    return_date: Optional[date] = None
    fine: Optional[float] = None
    approved_by: Optional[str] = None
    approved_date: Optional[date] = None
    return_condition: Optional[str] = None
    borrow_status: Optional[str] = None
    reminder_sent: Optional[bool] = None

class FineResponse(BaseModel):
    id: int
    borrower_name: str
    book_title: str
    amount: float
    paid: bool
    paid_date: Optional[date]
    payment_method: Optional[str]
    reason: Optional[str]
    created_at: date
    borrow_id: int
