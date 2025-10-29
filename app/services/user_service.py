from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.models import User
from app.schemas.user import UserUpdate
from typing import List, Dict, Any
import json

class UserService:
    @staticmethod
    def build_user_response(user: User) -> Dict[str, Any]:
        return {
            "id": user.id,
            "username": user.username or user.email,
            "displayName": user.display_name or (user.email.split("@")[0] if user.email else None),
            "dob": user.dob,
            "attendances": json.loads(user.attendances) if user.attendances else [0, 0, 0, 0, 0, 0, 0],
            "image": user.image,
            "stars": user.stars if hasattr(user, "stars") else 0,
            "isPremium": user.is_premium,
            "freeChat": user.free_chat if hasattr(user, "free_chat") else 3
        }

    @staticmethod
    def get_users(skip: int, limit: int, db: Session) -> Dict[str, List[Dict[str, Any]]]:
        users = db.query(User).offset(skip).limit(limit).all()
        return {"users": [UserService.build_user_response(u) for u in users]}

    @staticmethod
    def get_user(user_id: int, db: Session) -> Dict[str, Dict[str, Any]]:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user": UserService.build_user_response(db_user)}

    @staticmethod
    def update_user(user: UserUpdate, current_user: User, db: Session) -> Dict[str, Dict[str, Any]]:
        db_user = db.query(User).filter(User.id == current_user.id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = {}
        if user.displayName:
            update_data["displayName"] = user.displayName
        if user.dob is not None:
            update_data["dob"] = user.dob
        if user.image is not None:
            update_data["image"] = user.image
        if user.isPremium is not None:
            update_data["isPremium"] = user.isPremium

        for key, value in update_data.items():
            setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)
        return {"user": update_data}

    @staticmethod
    def delete_user(current_user: User, db: Session) -> Dict[str, str]:
        db_user = db.query(User).filter(User.id == current_user.id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if current_user.id != db_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this user")

        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"} 