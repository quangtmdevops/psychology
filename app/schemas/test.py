from pydantic import BaseModel
from typing import Optional

class TestBase(BaseModel):
    content: str
    order: Optional[int] = None

class TestCreate(TestBase):
    pass

class TestUpdate(TestBase):
    pass

class TestInDBBase(TestBase):
    id: int

    class Config:
        orm_mode = True

class TestInDB(TestInDBBase):
    pass

class TestAnswerBase(BaseModel):
    level: int

class TestAnswerCreate(TestAnswerBase):
    pass

class TestAnswerInDBBase(TestAnswerBase):
    id: int
    question_id: int
    user_id: int

    class Config:
        orm_mode = True

class TestAnswerInDB(TestAnswerInDBBase):
    pass

class EntityBase(BaseModel):
    content: str
    reward: Optional[int] = 0

class EntityCreate(EntityBase):
    pass

class EntityInDBBase(EntityBase):
    id: int
    question_id: int
    user_id: int

    class Config:
        orm_mode = True

class EntityInDB(EntityInDBBase):
    pass 