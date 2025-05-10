from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: Optional[str] = None
    audio: Optional[str] = None
    image: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    title: Optional[str] = None

class PostInDB(PostBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 