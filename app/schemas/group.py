from pydantic import BaseModel
from typing import Optional, List


class SubGroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class SubGroupCreate(SubGroupBase):
    group_id: int


class SubGroupUpdate(SubGroupBase):
    pass


class SubGroupInDB(SubGroupBase):
    id: int
    group_id: int

    class Config:
        from_attributes = True


class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    name: Optional[str] = None


class Group(GroupBase):
    id: int

    class Config:
        from_attributes = True


class GroupInDB(GroupBase):
    id: int
    sub_groups: List[SubGroupInDB] = []

    class Config:
        from_attributes = True
