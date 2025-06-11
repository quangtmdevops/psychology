from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.models import Test, Entity, TestAnswer, User, Option, Group
from typing import List, Dict, Any, Literal
from pydantic import BaseModel

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

class TestAnswerIn(BaseModel):
    testId: str
    optionId: str

class TestService:
    @staticmethod
    def get_tests(type: Literal["RADS", "DASS", "MDQ"], db: Session) -> List[GroupedTestOut]:
        group = db.query(Group).filter(Group.name == type).first()
        if not group:
            return []
        tests = db.query(Test).filter(Test.group_id == group.id).all()
        test_list = []
        for test in tests:
            options = db.query(Option).filter(Option.test_id == test.id).all()
            option_list = [
                OptionOut(
                    id=str(option.id),
                    content=option.content,
                    level=option.level
                )
                for option in options
            ]
            test_list.append(
                TestOut(
                    id=str(test.id),
                    content=test.content,
                    options=option_list
                )
            )
        return [GroupedTestOut(group=type, test=test_list)]

    @staticmethod
    def submit_test_answers(answers: List[TestAnswerIn], current_user: User, db: Session) -> Dict[str, Any]:
        saved_answers = []
        for ans in answers:
            answer = TestAnswer(
                user_id=current_user.id,
                test_id=int(ans.testId),
                option_id=ans.optionId
            )
            db.add(answer)
            saved_answers.append({
                "testId": ans.testId,
                "optionId": ans.optionId
            })
        db.commit()
        return {"status": "success", "saved": saved_answers} 