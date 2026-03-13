from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "citizen"
    city: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    city: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
