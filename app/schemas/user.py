from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    is_premium: Optional[bool] = Field(False, example=False)


class UserCreate(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=8, example="password123")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=8, example="password123")


class User(UserBase):
    id: int = Field(..., example=1)
    reward: int = Field(0, example=0)
    is_active: bool = Field(True, example=True)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "isPremium": False,
                "reward": 0,
                "is_active": True
            }
        }


class UserUpdate(BaseModel):
    
    displayName: Optional[str] = Field(None, example="John Doe")
    dob: Optional[str] = Field(None, example="01/01/2000")
    image: Optional[str] = Field(None, example="https://example.com/image.jpg")
    isPremium: Optional[bool] = Field(None, example=True)

    class Config:
        json_schema_extra = {
            "example": {
                "displayName": "John Doe",
                "dob": "01/01/2000",
                "image": "https://example.com/image.jpg",
                "isPremium": True
            }
        }


class UserInDB(User):
    pass


class Token(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field("bearer", example="bearer")
    scopes: List[str] = Field(..., example=["users:read"])

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "scopes": ["users:read"]
            }
        }


class TokenData(BaseModel):
    email: Optional[str] = None
    scopes: List[str] = []
