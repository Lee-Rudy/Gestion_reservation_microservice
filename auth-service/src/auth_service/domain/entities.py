from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


@dataclass
class User:
    email: str
    password_hash: str
    role: UserRole
    name: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class AuthToken:
    access_token: str
    token_type: str = "bearer"
