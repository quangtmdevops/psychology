from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Literal
from pydantic import BaseModel
from app.core.database import get_db
from app.models.models import Test, Entity, Group
from app.models.models import TestAnswer, User
from app.core.auth import get_current_user
from app.models.models import Test, Option, Group

router = APIRouter(prefix="/tests", tags=["tests"])


class OptionOut(BaseModel):
    id: str
    content: str
    level: int


class TestOut(BaseModel):
    id: str
    content: str
    options: List[OptionOut]


class GroupedTestOut(BaseModel):
    group: str
    test: List[TestOut]


@router.get("/", response_model=List[GroupedTestOut])
def get_tests(
    type: Literal["RADS", "DASS", "MDQ"] = Query(..., description="Test type"),
    db: Session = Depends(get_db),
):
    group = db.query(Group).filter(Group.name == type).first()
    if not group:
        return []
    tests = db.query(Test).filter(Test.group_id == group.id).all()
    if not tests:
        return []

    test_list = []
    for test in tests:
        options = db.query(Option).filter(Option.test_id == test.id).all()
        option_list = [
            OptionOut(id=str(option.id), content=option.content, level=option.level)
            for option in options
        ]
        test_list.append(
            TestOut(id=str(test.id), content=test.content, options=option_list)
        )

    return [GroupedTestOut(group=type, test=test_list)]


class TestAnswerIn(BaseModel):
    testId: str
    optionId: str


@router.post("/")
def submit_test_answers(
    answers: List[TestAnswerIn],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    saved_answers = []
    for ans in answers:
        answer = TestAnswer(test_id=int(ans.testId), option_id=ans.optionId)
        db.add(answer)
        saved_answers.append({"testId": ans.testId, "optionId": ans.optionId})
    db.commit()
    return {"status": "success", "saved": saved_answers}
