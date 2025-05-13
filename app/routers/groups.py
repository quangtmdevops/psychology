from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.models import Group
from app.schemas.group import Group, GroupCreate, GroupUpdate
from app.core.database import get_db

router = APIRouter()

@router.post("/groups/", response_model=Group)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    db_group = Group(**group.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@router.get("/groups/", response_model=List[Group])
def read_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Group).offset(skip).limit(limit).all()

@router.get("/groups/{group_id}", response_model=Group)
def read_group(group_id: int, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return db_group

@router.put("/groups/{group_id}", response_model=Group)
def update_group(group_id: int, group: GroupUpdate, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    for key, value in group.dict(exclude_unset=True).items():
        setattr(db_group, key, value)
    db.commit()
    db.refresh(db_group)
    return db_group

@router.delete("/groups/{group_id}", response_model=Group)
def delete_group(group_id: int, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    db.delete(db_group)
    db.commit()
    return db_group 