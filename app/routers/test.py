from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Test, TestAnswer, Entity, User
from app.schemas.test import TestInDB, TestAnswerCreate, EntityInDB
from app.routers import users
from app.core.auth import get_current_user
from typing import List

router = APIRouter(prefix="/tests", tags=["tests"])

@router.get("/", response_model=List[TestInDB])
def list_tests(db: Session = Depends(get_db)):
    return db.query(Test).all()

@router.get("/{test_id}", response_model=TestInDB)
def get_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

@router.post("/{test_id}/answer")
def answer_test(test_id: int, answer: TestAnswerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Example logic: check answer, update reward
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    # Here you would check the answer and update the user's reward
    # For now, just return a dummy response
    return {"result": "checked", "test_id": test_id, "user_id": current_user.id}

@router.get("/{test_id}/entities", response_model=List[EntityInDB])
def get_entities(test_id: int, db: Session = Depends(get_db)):
    return db.query(Entity).filter(Entity.question_id == test_id).all() 