from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserLogin, UserCreate, Token
from app.models.models import User
from app.core.database import get_db
from app.core.auth import verify_password, get_password_hash, create_user_token
from typing import Any
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


def build_user_response(user):
    import json
    return {
        "id": user.id,
        "username": user.username,
        "displayName": user.display_name,
        "dob": user.dob,
        "attendances": json.loads(user.attendances) if user.attendances else [0, 0, 0, 0, 0, 0, 0],
        "image": user.image,
        "stars": user.stars,
        "isPremium": user.is_premium,
        "freeChat": user.free_chat
    }


@router.post("/login")
def login(user_login: UserLogin, db: Session = Depends(get_db)) -> Any:
    user = db.query(User).filter(User.email == user_login.email).first()

    if not user or not verify_password(user_login.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    token = create_user_token(user)

    print("Login request body:", user_login.model_dump())
    print("User.email: ", user.email)
    print("User.password: ", user.password)
    print("user_login.email: ", user_login.email)
    print("user_login.password: ", user_login.password)

    return {
        "accessToken": token["access_token"],
        "user": build_user_response(user)
    }


@router.post("/signup")
def signup(user_create: UserCreate, db: Session = Depends(get_db)) -> Any:
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed_password = get_password_hash(user_create.password)
    user = User(email=user_create.email, password=hashed_password)
    try:
        db.add(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    token = create_user_token(user)
    return {
        "accessToken": token["access_token"],
        "user": build_user_response(user)
    }


from pydantic import BaseModel


class PasswordChange(BaseModel):
    email: str
    oldPassword: str
    newPassword: str


@router.post("/password")
def change_password(data: PasswordChange, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.oldPassword, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    user.password = get_password_hash(data.newPassword)
    db.commit()
    return {"msg": "Password updated successfully"}
