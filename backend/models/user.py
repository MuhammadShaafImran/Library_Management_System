from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import date

class UserType(str, Enum):
    student = "student"
    teacher = "teacher"
    librarian = "librarian"
    guest = "guest"

class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    banned = "banned"

class User(BaseModel):
    id: int
    name: str
    email: str
    type: UserType
    phone: Optional[str]
    status: UserStatus
    last_login: Optional[date]
    joining_date: date
