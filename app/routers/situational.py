from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.auth import get_current_user
from app.models.models import User, SituationalAnswer, SituationalQuestion
from pydantic import BaseModel
from app.core.database import get_db
from app.models.models import SituationalQuestion, SituationalUserAnswer
from sqlalchemy.orm import Session

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
    
class SubmitAnswerIn(BaseModel):
    situationalId: str
    answerId: str

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
@router.get("/progress", response_model=List[ProgressOut])
def get_progress(
    group: Optional[List[int]] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not group:
        group = [0, 1, 2, 3]
    result = []
    for g in group:
        # Total questions in this group
        total = db.query(SituationalQuestion).filter(SituationalQuestion.group == g).count()
        # Answered questions in this group by the user
        answered = (
            db.query(SituationalUserAnswer)
            .join(SituationalQuestion, SituationalUserAnswer.question_id == SituationalQuestion.id)
            .filter(
                SituationalUserAnswer.user_id == current_user.id,
                SituationalQuestion.group == g
            )
            .count()
        )
        result.append(ProgressOut(level=g, current=answered, total=total))
    return result

# 2. GET /?group=0/1/2/3&level=0/1/2
@router.get("/", response_model=List[SituationOut])
def get_situations(
    group: Optional[List[int]] = Query(None),
    level: Optional[List[int]] = Query(None),
    current_user: User = Depends(get_current_user)
):
    # In real code, filter situations by group and level from DB
    # Here, return all dummy situations
    return SITUATIONS

# 3. POST /
@router.post("/", response_model=StarsOut)
def submit_answers(
    answers: List[SubmitAnswerIn],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stars_earned = 0
    for ans in answers:
        # Fetch the correct answer from the DB
        correct_answer = db.query(SituationalAnswer).filter(
            SituationalAnswer.question_id == ans.situationalId,
            SituationalAnswer.id == ans.answerId,
            SituationalAnswer.is_correct == True
        ).first()
        if correct_answer:
            stars_earned += 1

    # Update user's stars in DB
    current_user.stars = (current_user.stars or 0) + stars_earned
    db.commit()
    return {"stars": current_user.stars}