from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import Group, User
from app.schemas.group import GroupCreate, GroupUpdate, Group as GroupSchema
from app.core.auth import get_current_user

router = APIRouter(
    prefix="/groups",
    tags=["groups"]
)

@router.post("/", response_model=GroupSchema)
def create_group(
    group: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_group = Group(**group.model_dump())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@router.get("/", response_model=List[GroupSchema])
def read_groups(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    groups = db.query(Group).offset(skip).limit(limit).all()
    return groups

@router.get("/{group_id}", response_model=GroupSchema)
def read_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return db_group

@router.put("/{group_id}", response_model=GroupSchema)
def update_group(
    group_id: int,
    group: GroupUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    for key, value in group.model_dump(exclude_unset=True).items():
        setattr(db_group, key, value)
    
    db.commit()
    db.refresh(db_group)
    return db_group

@router.delete("/{group_id}")
def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    db.delete(db_group)
    db.commit()
    return {"message": "Group deleted successfully"} 