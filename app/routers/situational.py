from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.auth import get_current_user
from app.models.models import User, SituationalAnswer, SituationalQuestion
from pydantic import BaseModel
from app.core.database import get_db
from app.models.models import SituationalQuestion, SituationalUserAnswer
from sqlalchemy.orm import Session
from app.services.situational_service import SituationalService, SubmitAnswerIn

router = APIRouter(prefix="/situational", tags=["situational"])



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
    
class StarsOut(BaseModel):
    stars: int
    

# Dummy data for demonstration
SITUATIONS = [
    {
        "id": "1",
        "content": "What would you do if you saw someone drop their wallet?",
        "explanation": "Returning lost property is the correct action.",
        "answers": [
            {"id": "a", "content": "Pick it up and keep it", "isCorrect": False},
            {"id": "b", "content": "Return it to the owner", "isCorrect": True}
        ]
    },
    # ... more situations
]

# USER_PROGRESS = {
#     0: {"level": 0, "current": 2, "total": 5},
#     1: {"level": 1, "current": 1, "total": 5},
#     2: {"level": 2, "current": 0, "total": 5},
#     3: {"level": 3, "current": 0, "total": 5},
# }

USER_STARS = {
    # user_id: stars
}

# 1. GET /progress?group=0/1/2/3
@router.get("/progress", response_model=List[SituationalService.ProgressOut])
def get_progress(
    group: Optional[List[int]] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return SituationalService.get_progress(group, current_user, db)

# 2. GET /?group=0/1/2/3&level=0/1/2
@router.get("/", response_model=List[SituationalService.SituationOut])
def get_situations(
    group: Optional[List[int]] = Query(None),
    level: Optional[List[int]] = Query(None),
    current_user: User = Depends(get_current_user)
):
    return SituationalService.get_situations(group, level, current_user)

# 3. POST /
@router.post("/", response_model=SituationalService.StarsOut)
def submit_answers(
    answers: List[SubmitAnswerIn],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return SituationalService.submit_answers(answers, current_user, db)