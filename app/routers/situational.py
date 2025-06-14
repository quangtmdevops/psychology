from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.models import User
from app.services.situational_service import SituationalService
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/situational", tags=["situational"])


@router.get("/progress")
def get_progress(
    group: int = Query(..., description="Group id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SituationalService.get_progress(group, db, current_user)


@router.get("/")
def get_situational_questions(
    group: int = Query(..., description="Group id"),
    level: int = Query(..., description="Level"),
    db: Session = Depends(get_db),
):
    return SituationalService.get_situational_questions(group, level, db)


class UserAnswerIn(BaseModel):
    situationalId: str
    answerId: str


@router.post("/")
def submit_situational_answers(
    answers: List[UserAnswerIn],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    answer_dicts = [a.dict() for a in answers]
    return SituationalService.submit_situational_answers(answer_dicts, current_user.id, db)
