from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.models import User
from app.schemas.user import UserLogin, UserCreate
from app.core.auth import verify_password, get_password_hash, create_user_token
from typing import Any, Dict
import json

class AuthService:
    @staticmethod
    def build_user_response(user: User) -> Dict[str, Any]:
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

    @staticmethod
    def login(user_login: UserLogin, db: Session) -> Dict[str, Any]:
        user = db.query(User).filter(User.email == user_login.email).first()

        if not user or not verify_password(user_login.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        token = create_user_token(user)
        return {
            "accessToken": token["access_token"],
            "user": AuthService.build_user_response(user)
        }

    @staticmethod
    def signup(user_create: UserCreate, db: Session) -> Dict[str, Any]:
        existing_user = db.query(User).filter(User.email == user_create.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        hashed_password = get_password_hash(user_create.password)
        user = User(email=user_create.email, password=hashed_password)
        
        try:
            db.add(user)
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        token = create_user_token(user)
        return {
            "accessToken": token["access_token"],
            "user": AuthService.build_user_response(user)
        }

    @staticmethod
    def change_password(email: str, old_password: str, new_password: str, db: Session) -> Dict[str, str]:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        user.password = get_password_hash(new_password)
        db.commit()
        return {"msg": "Password updated successfully"} 