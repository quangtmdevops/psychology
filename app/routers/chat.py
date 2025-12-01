from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.models import User
from app.services.chat_service import send_chat_message, use_chat_credit, get_remaining_chats

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None  # For tracking conversation history if needed

@router.post("/send")
async def send_chat(
        chat_message: ChatMessage,
        db: Session = Depends(get_db),
        current_user: User = Security(get_current_user, scopes=["users:read"])
) -> Dict[str, Any]:
    """
    Send a chat message to the AI assistant.
    - Deducts one chat credit from the user's daily limit
    - Returns the AI's response
    """
    # Đảm bảo user nằm trong session hiện tại
    user = db.merge(current_user)
    db.refresh(user)

    # Deduct chat credit
    if not use_chat_credit(user, db):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily chat limit reached. Please try again tomorrow or upgrade to premium for unlimited chats."
        )

    # Sau khi trừ, refresh lại user
    db.refresh(user)

    try:
        # Send message to external chat API
        response = await send_chat_message(chat_message.message)

        ai_response = response.get('choices', [{}])[0].get('message', {}).get('content', 'No response')

        return {
            "status": "success",
            "message": ai_response,
            "remaining_chats": max(0, user.free_chat),
            "is_premium": getattr(user, 'is_premium', False),
            "conversation_id": chat_message.conversation_id
        }

    except HTTPException as e:
        # Nếu gọi API lỗi → hoàn lại 1 credit
        user.free_chat += 1
        db.commit()
        db.refresh(user)
        raise e


@router.get("/status")
async def get_chat_status(
        db: Session = Depends(get_db),
        current_user: User = Security(get_current_user, scopes=["users:read"])
) -> Dict[str, Any]:
    """
    Get the current chat status for the user.
    - Returns remaining chats, premium status, and other relevant information
    """

    # Luôn reload user từ DB để dữ liệu chính xác
    user = db.merge(current_user)
    db.refresh(user)

    status = get_remaining_chats(user, db)

    return {
        "remaining_chats": status["remaining_chats"],
        "can_chat": status["can_chat"],
        "is_premium": status["is_premium"],
        "last_chat_date": status["last_chat_date"],
        "daily_limit": 3,
        "unlimited": getattr(user, 'is_premium', False)
    }
