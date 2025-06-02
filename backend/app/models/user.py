from typing import Optional
from sqlmodel import SQLModel, Field
from fastapi_users.db import SQLAlchemyBaseUserTable
from pydantic import EmailStr
from datetime import datetime
from fastapi_users import schemas

class UserBase(SQLModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    full_name: Optional[str] = None

class User(SQLAlchemyBaseUserTable[int], SQLModel, table=True):
    __tablename__ = "users"
    
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
    full_name: Optional[str] = None

    def create_update_dict(self):
        return {
            "email": self.email,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "is_verified": self.is_verified,
            "full_name": self.full_name,
        }

    def create_update_dict_superuser(self):
        return {
            "email": self.email,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "is_verified": self.is_verified,
            "full_name": self.full_name,
            "hashed_password": self.hashed_password,
        }

class UserCreate(schemas.CreateUpdateDictModel):
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    full_name: Optional[str] = None

class UserUpdate(schemas.CreateUpdateDictModel):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
    full_name: Optional[str] = None

class UserDB(User):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime 