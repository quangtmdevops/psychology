from fastapi import APIRouter, Depends, HTTPException, status, Security, Form
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
        200: {"description": "Current user information"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough permissions"},
    }
)
async def read_current_user(
        current_user: User = Security(get_current_user, scopes=["users:read"]),
):
    """
    Get current user's information.
    Requires authentication token with 'users:read' scope.
    """
    return {"user": build_user_response(current_user)}




@router.put("/", response_model=dict)
def update_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["users:read"])
):
    """
    Update current user's information.
    
    Requires authentication token with 'users:readread' scope.
    
    - **user_update**: User information to update
    """
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
    
    Requires authentication token with 'users:read' scope.
    """
    
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

