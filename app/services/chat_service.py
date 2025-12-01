from datetime import datetime, date
import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.models import User
from typing import Dict, Any, Optional
from app.core.config import Settings


settings = Settings()
CHAT_API_URL = settings.CHAT_API_URL
CHAT_API_KEY = settings.CHAT_API_KEY
DEFAULT_CHAT_MODEL = settings.DEFAULT_CHAT_MODEL

def can_send_chat(user: User, db: Session) -> bool:
    """
    Check if user can send a chat message.
    Resets the chat count if it's a new day.
    """
    today = date.today()

    # If it's a new day, reset the chat count
    if user.last_chat_date is None or user.last_chat_date.date() < today:
        user.free_chat = 3  # Reset to 3 messages per day
        user.last_chat_date = datetime.utcnow()
        db.commit()

    # Check if user has remaining chats
    if user.free_chat <= 0:
        return False

    return True


async def send_chat_message(message: str) -> Dict[str, Any]:
    """
    Send a chat message to the external API.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHAT_API_KEY}"
    }

    payload = {
        "model": DEFAULT_CHAT_MODEL,
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 2048,
        "stream": False
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                CHAT_API_URL,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Chat API error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to chat service: {str(e)}"
            )


import datetime


def use_chat_credit(user: User, db: Session) -> bool:
    """
    Deduct one chat credit from the user.
    Returns True if credit was used, False if no credits left.
    """
    # Đảm bảo user nằm trong session đúng
    user = db.merge(user)
    db.refresh(user)

    if user.free_chat <= 0:
        return False

    user.free_chat -= 1
    user.last_chat_date = datetime.datetime.now(datetime.UTC)
    db.commit()
    db.refresh(user)
    return True


def get_remaining_chats(user: User, db: Session) -> dict:
    """
    Get the remaining number of chats for the user today.
    """
    # This will reset the count if it's a new day
    can_send = can_send_chat(user, db)

    return {
        "remaining_chats": max(0, user.free_chat),  # Ensure non-negative
        "can_chat": can_send,
        "is_premium": getattr(user, 'is_premium', False),
        "last_chat_date": user.last_chat_date
    }
