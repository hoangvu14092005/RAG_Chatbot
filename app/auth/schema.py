from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str

class TokenModel(BaseModel):
    access_token: str
    token_type: str

class UserModel(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    role: str
