from typing import Optional
from sqlmodel import SQLModel, Field
from fastapi_users.db import SQLAlchemyBaseUserTable
from pydantic import EmailStr
from datetime import datetime

class UserBase(SQLModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    full_name: Optional[str] = None

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    verification_token: Optional[str] = None
    reset_token: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserDB(User, SQLAlchemyBaseUserTable):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime 