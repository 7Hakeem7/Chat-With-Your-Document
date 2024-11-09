# app/db/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class UserResponseWithToken(BaseModel):
    id: int
    username: str
    token: str

class UserLogin(BaseModel):
    username: str
    password: str

# Document Schemas
class DocumentCreate(BaseModel):
    title: str
    content: str

class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str
    uploaded_at: Optional[str]  # Optional field for datetime string
    user_id: int

    class Config:
        orm_mode = True