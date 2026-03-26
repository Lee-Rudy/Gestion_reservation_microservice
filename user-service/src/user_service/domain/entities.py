from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


@dataclass
class User:
    name: str
    email: str
    password_hash: str
    role: UserRole
    id: Optional[int] = None
    created_at: Optional[datetime] = None
