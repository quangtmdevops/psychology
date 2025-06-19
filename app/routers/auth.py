from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from app.schemas.user import UserLogin, UserCreate, Token
from app.models.models import User
from app.core.database import get_db
from app.core.auth import verify_password, get_password_hash, create_user_token, get_current_user
from typing import Any
from sqlalchemy.exc import IntegrityError
from app.services.auth_service import AuthService
from pydantic import BaseModel

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
    return AuthService.login(user_login, db)


@router.post("/signup")
def signup(user_create: UserCreate, db: Session = Depends(get_db)) -> Any:
    return AuthService.signup(user_create, db)


class PasswordChange(BaseModel):
    email: str
    oldPassword: str
    newPassword: str


@router.post("/password")
def change_password(
    data: PasswordChange, 
    current_user: User = Security(get_current_user, scopes=["users:read"]),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    
    Requires authentication token with 'users:read' scope.
    """
    return AuthService.change_password(data.email, data.oldPassword, data.newPassword, db)


class RefreshTokenRequest(BaseModel):
    refreshToken: str

class RefreshTokenResponse(BaseModel):
    accessToken: str
    refreshToken: str

@router.post("/refresh-token", response_model=RefreshTokenResponse)
def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using a valid refresh token.
    """
    return AuthService.refresh_access_token(data.refreshToken, db)
