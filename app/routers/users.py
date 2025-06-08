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


@router.put(
    "/",
    responses={
        200: {"description": "User updated successfully"},
        401: {"description": "Not authenticated"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"}
    }
)
async def update_user(
        user: UserUpdate,  # user is the user object from the request body
        current_user: User = Security(get_current_user, scopes=["users:read"]), # current_user is the user object from token was passed in the header 
        db: Session = Depends(get_db)
):
    """
    Update current user's information.
    
    - **user**: Updated user information
    """
    print("Received update data:", user.model_dump())
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert the update data to match database field names
    update_data = {}
    if user.displayName:
        update_data["displayName"] = user.displayName
    if user.dob is not None:
        update_data["dob"] = user.dob
    if user.image is not None:
        update_data["image"] = user.image
    if user.isPremium is not None:
        update_data["isPremium"] = user.isPremium

    print("Processed update data:", update_data)
    
    # Update the user object with new values
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return {"user": update_data}


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

