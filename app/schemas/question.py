from pydantic import BaseModel, conint
from typing import Optional, List

from app.models.models import SituationGroup, SituationalAnswer


class SituationalQuestionBase(BaseModel):
    content: str
    order: int
    situation_group_id: int
    level: int

    class Config:
        from_attributes = True


class SituationalQuestionCreate(SituationalQuestionBase):
    pass


class SituationalQuestionUpdate(BaseModel):
    content: Optional[str] = None
    order: Optional[int] = None
    situation_group_id: Optional[int] = None
    level: Optional[int] = None


class SituationalQuestion(SituationalQuestionBase):
    id: int
    situation_group: SituationGroup
    answers: List[SituationalAnswer]

    class Config:
        from_attributes = True
