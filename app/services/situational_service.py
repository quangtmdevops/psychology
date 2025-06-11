from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.models import User, SituationalAnswer, SituationalQuestion, SituationalUserAnswer
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

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

class SituationalService:
    @staticmethod
    def get_progress(group: Optional[List[int]], current_user: User, db: Session) -> List[ProgressOut]:
        if not group:
            group = [0, 1, 2, 3]
        result = []
        for g in group:
            total = db.query(SituationalQuestion).filter(SituationalQuestion.group == g).count()
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

    @staticmethod
    def get_situations(group: Optional[List[int]], level: Optional[List[int]], current_user: User) -> List[SituationOut]:
        # TODO: Implement actual database query instead of dummy data
        return [
            {
                "id": "1",
                "content": "What would you do if you saw someone drop their wallet?",
                "explanation": "Returning lost property is the correct action.",
                "answers": [
                    {"id": "a", "content": "Pick it up and keep it", "isCorrect": False},
                    {"id": "b", "content": "Return it to the owner", "isCorrect": True}
                ]
            }
        ]

    @staticmethod
    def submit_answers(answers: List[SubmitAnswerIn], current_user: User, db: Session) -> StarsOut:
        stars_earned = 0
        for ans in answers:
            correct_answer = db.query(SituationalAnswer).filter(
                SituationalAnswer.question_id == ans.situationalId,
                SituationalAnswer.id == ans.answerId,
                SituationalAnswer.is_correct == True
            ).first()
            if correct_answer:
                stars_earned += 1

        current_user.stars = (current_user.stars or 0) + stars_earned
        db.commit()
        return StarsOut(stars=current_user.stars) 