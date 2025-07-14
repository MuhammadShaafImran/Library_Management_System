from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import date


class BorrowStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Borrow(BaseModel):
    id: int
    user_id: int
    book_id: int
    request_description: Optional[str]
    request_date: date
    return_date: Optional[date]
    fine: float = 0
    approved_by: Optional[int]
    approved_date: Optional[date]
    return_condition: Optional[str]
    status: BorrowStatus = BorrowStatus.pending
    reminder_sent: bool = False

class Fine(BaseModel):
    id: int
    borrow_id: int
    amount: float
    paid: bool = False
    paid_date: Optional[date]
    payment_method: Optional[str]
    reason: Optional[str]
    created_at: date

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