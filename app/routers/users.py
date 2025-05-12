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

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post(
    "/register",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User created successfully", "model": UserSchema},
        400: {"description": "Email already registered"},
        422: {"description": "Validation error"}
    }
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: User's email address
    - **password**: User's password (minimum 8 characters)
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password=hashed_password,
        is_premium=False,
        reward=0,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post(
    "/token",
    response_model=Token,
    tags=["authentication"],
    responses={
        200: {"description": "Token generated successfully", "model": Token},
        401: {"description": "Invalid credentials"},
        422: {"description": "Validation error"}
    }
)
def login_for_access_token(user: UserLogin, db: Session = Depends(get_db)):
    """
    Get access token for authentication.
    
    Use this endpoint to get a JWT token that you can use to authenticate other API requests.
    The token should be included in the Authorization header as: `Bearer <token>`
    
    - **email**: User's email address
    - **password**: User's password (minimum 8 characters)
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create token with appropriate scopes
    scopes = ["users:read"]
    if db_user.is_premium:
        scopes.extend(["users:write", "users:delete"])
    
    return create_user_token(db_user, scopes)


@router.get(
    "/me",
    response_model=UserSchema,
    responses={
        200: {"description": "Current user information", "model": UserSchema},
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough permissions"}
    }
)
async def read_users_me(
    current_user: User = Security(get_current_user, scopes=["users:read"])
):
    """
    Get current user's information.
    
    Requires authentication token with 'users:read' scope.
    """
    return current_user


@router.get(
    "/",
    response_model=List[UserSchema],
    responses={
        200: {"description": "List of users", "model": List[UserSchema]},
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough permissions"}
    }
)
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Security(get_current_user, scopes=["users:read"]),
    db: Session = Depends(get_db)
):
    """
    Get list of users.
    
    Requires authentication token with 'users:read' scope.
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get(
    "/{user_id}",
    response_model=UserSchema,
    responses={
        200: {"description": "User information", "model": UserSchema},
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
    return db_user


@router.put(
    "/{user_id}",
    response_model=UserSchema,
    responses={
        200: {"description": "User updated successfully", "model": UserSchema},
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough permissions or not authorized to update this user"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"}
    }
)
async def update_user(
    user_id: int,
    user: UserUpdate,
    current_user: User = Security(get_current_user, scopes=["users:write"]),
    db: Session = Depends(get_db)
):
    """
    Update user information.
    
    Requires authentication token with 'users:write' scope.
    Users can only update their own information.
    
    - **user_id**: ID of the user to update
    - **user**: Updated user information
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    update_data = user.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete(
    "/{user_id}",
    responses={
        200: {"description": "User deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough permissions or not authorized to delete this user"},
        404: {"description": "User not found"}
    }
)
async def delete_user(
    user_id: int,
    current_user: User = Security(get_current_user, scopes=["users:delete"]),
    db: Session = Depends(get_db)
):
    """
    Delete a user.
    
    Requires authentication token with 'users:delete' scope.
    Users can only delete their own account.
    
    - **user_id**: ID of the user to delete
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
