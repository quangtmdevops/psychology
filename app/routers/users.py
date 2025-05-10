from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.models import User
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema, Token, UserLogin
from datetime import timedelta

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/register", response_model=UserSchema)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
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
        reward=0
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/token", response_model=Token)
def login_for_access_token(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[UserSchema])
def read_users(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserSchema)
def read_user(
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
        user_id: int,
        user: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
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


@router.delete("/{user_id}")
def delete_user(
        user_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
