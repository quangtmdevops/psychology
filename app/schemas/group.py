from pydantic import BaseModel
from typing import Optional

class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None

class GroupCreate(GroupBase):
    pass

class GroupUpdate(GroupBase):
    pass

class GroupInDBBase(GroupBase):
    id: int

    class Config:
        orm_mode = True

class Group(GroupInDBBase):
    pass 