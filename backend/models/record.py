from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import date


class Record(BaseModel):
    id: int
    user_id: int
    action: str
    book_id: Optional[int]
    borrow_id: Optional[int]
    timestamp: date
    ip_address: Optional[str]
    device_info: Optional[str]
    created_by: Optional[int]
    action_details: Optional[str]

class NotificationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    read = "read"

class Notification(BaseModel):
    id: int
    user_id: int
    book_id: Optional[int]
    type: str
    message: str
    status: NotificationStatus = NotificationStatus.pending
    created_at: date