from pydantic import BaseModel, conint
from typing import Optional, List

class TestAnswerBase(BaseModel):
    level: conint(ge=1, le=3)

class TestAnswerCreate(TestAnswerBase):
    question_id: int

class TestAnswerUpdate(TestAnswerBase):
    pass

class TestAnswerInDB(TestAnswerBase):
    id: int
    question_id: int

    class Config:
        from_attributes = True

class EntityBase(BaseModel):
    content: str
    reward: int = 0

class EntityCreate(EntityBase):
    question_id: int

class EntityUpdate(EntityBase):
    content: Optional[str] = None
    reward: Optional[int] = None

class EntityInDB(EntityBase):
    id: int
    question_id: int

    class Config:
        from_attributes = True

class TestBase(BaseModel):
    content: str
    order: Optional[int] = None

class TestCreate(TestBase):
    pass

class TestUpdate(TestBase):
    content: Optional[str] = None

class TestInDB(TestBase):
    id: int
    answers: List[TestAnswerInDB] = []
    entities: List[EntityInDB] = []

    class Config:
        from_attributes = True 