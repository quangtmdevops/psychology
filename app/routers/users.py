from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import (
    get_password_hash,
    verify_password,
    create_user_token,
    get_current_user,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.models import User
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema, Token, UserLogin
from datetime import timedelta
import json
from pydantic import BaseModel

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


def build_user_response(user):
    return {
        "id": str(user.id),
        "username": user.username or user.email,
        "displayName": user.display_name or (user.email.split("@")[0] if user.email else None),
        "dob": user.dob,
        "attendances": json.loads(user.attendances) if user.attendances else [0, 0, 0, 0, 0, 0, 0],
        "image": user.image,
        "stars": user.stars if hasattr(user, "stars") else 0,
        "isPremium": user.is_premium,
        "freeChat": user.free_chat if hasattr(user, "free_chat") else 0
    }

@router.get(
    "/",
    responses={
        200: {"description": "List of users"},
    }
)
async def read_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """
    Get list of users.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return {"users": [build_user_response(u) for u in users]}


@router.get(
    "/{user_id}",
    responses={
        200: {"description": "User information"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough permissions"},
        404: {"description": "User not found"}
    }
)
async def read_user(
        user_id: int,
        current_user: User = Security(get_current_user, scopes=["users:read"]),
        db: Session = Depends(get_db)
):
    """
    Get user by ID.
    
    Requires authentication token with 'users:read' scope.
    
    - **user_id**: ID of the user to retrieve
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": build_user_response(db_user)}


class UserUpdateIn(BaseModel):
    displayName: str = None
    dob: str = None
    image: str = None
    isPremium: bool = None

@router.put("/", response_model=dict)
def update_user(
    user_update: UserUpdateIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.displayName is not None:
        user.display_name = user_update.displayName
    if user_update.dob is not None:
        user.dob = user_update.dob
    if user_update.image is not None:
        user.image = user_update.image
    if user_update.isPremium is not None:
        user.is_premium = user_update.isPremium
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "displayName": user.display_name,
        "dob": user.dob,
        "image": user.image,
        "isPremium": user.is_premium
    }


@router.delete(
    "/",
    responses={
        200: {"description": "User deleted successfully"},
        401: {"description": "Not authenticated"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"}
    }
)
async def delete_user(
        current_user: User = Security(get_current_user, scopes=["users:read"]),
        db: Session = Depends(get_db)
):
    """
    Delete current user's information.
    
    - **user**: Updated user information
    """
    
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    

    if current_user.id != db_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

