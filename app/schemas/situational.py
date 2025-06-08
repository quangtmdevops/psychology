from pydantic import BaseModel
from typing import List, Optional

class ProgressOut(BaseModel):
    level: int
    current: int
    total: int

class AnswerOut(BaseModel):
    id: str
    content: str
    isCorrect: bool

class SituationOut(BaseModel):
    id: str
    content: str
    explanation: str
    answers: List[AnswerOut]

class SubmitAnswerIn(BaseModel):
    situationalId: str
    answerId: str

class StarsOut(BaseModel):
    stars: int