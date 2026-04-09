from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)
