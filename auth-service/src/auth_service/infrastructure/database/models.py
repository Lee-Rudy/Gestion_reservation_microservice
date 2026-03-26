from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, String

from auth_service.infrastructure.database.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("USER", "ADMIN", name="user_role"), default="USER")
    created_at = Column(DateTime, default=datetime.utcnow)
