from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    is_premium: Optional[bool] = False


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    reward: Optional[int] = None


class User(UserBase):
    id: int
    reward: int = 0

    class Config:
        from_attributes = True


class UserInDB(User):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
