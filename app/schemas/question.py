from pydantic import BaseModel, conint
from typing import Optional

class SituationalQuestionBase(BaseModel):
    content: str
    level: conint(ge=1, le=3)
    group_id: int

class SituationalQuestionCreate(SituationalQuestionBase):
    pass

class SituationalQuestionUpdate(SituationalQuestionBase):
    content: Optional[str] = None
    level: Optional[conint(ge=1, le=3)] = None
    group_id: Optional[int] = None

class SituationalQuestionInDB(SituationalQuestionBase):
    id: int

    class Config:
        from_attributes = True 