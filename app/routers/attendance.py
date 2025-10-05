from fastapi import APIRouter, Depends, status, Security, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User
from app.core.auth import get_current_user
import datetime
import json
from typing import Tuple, List

router = APIRouter(prefix="/attendance", tags=["attendance"])

def calculate_streak(attendances: List[int]) -> int:
    """Tính số ngày điểm danh liên tiếp gần nhất"""
    streak = 0
    for day in reversed(attendances):
        if day == 1:
            streak += 1
        else:
            break
    return streak

def calculate_reward(streak: int) -> int:
    """Tính số sao thưởng dựa trên số ngày điểm danh liên tiếp"""
    if 1 <= streak <= 3:
        return 1
    elif 4 <= streak <= 5:
        return 2
    elif streak >= 6:
        return 3
    return 0

@router.get("/", status_code=status.HTTP_200_OK)
def mark_attendance(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["users:read"])
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Lấy ngày hiện tại
    today = datetime.datetime.now()
    
    # Khởi tạo hoặc lấy dữ liệu điểm danh
    try:
        attendances = json.loads(user.attendances)
        last_updated = datetime.datetime.fromisoformat(user.updated_at.isoformat())
    except Exception:
        attendances = [0, 0, 0, 0, 0, 0, 0]
        last_updated = today

    # Tính số ngày đã trôi qua kể từ lần cập nhật cuối cùng
    days_since_last_update = (today.date() - last_updated.date()).days
    
    # Nếu đã từng điểm danh trước đó
    if user.updated_at:
        # Nếu đã điểm danh trong ngày hôm nay rồi
        if today.date() == last_updated.date():
            raise HTTPException(status_code=400, detail="Bạn đã điểm danh hôm nay rồi")
        
        # Nếu bỏ lỡ 1 ngày trở lên, reset streak
        if days_since_last_update > 1:
            attendances = [0, 0, 0, 0, 0, 0, 0]
        # Nếu điểm danh vào ngày hôm sau, kiểm tra nếu không phải ngày tiếp theo thì reset
        elif days_since_last_update == 1:
            # Kiểm tra nếu ngày trước đó chưa điểm danh
            prev_day = (today.weekday() - 1) % 7
            if attendances[prev_day] == 0:
                attendances = [0, 0, 0, 0, 0, 0, 0]
    
    # Đánh dấu điểm danh hôm nay
    weekday = today.weekday()
    
    # Nếu đã điểm danh ngày hôm nay rồi
    if attendances[weekday] == 1:
        raise HTTPException(status_code=400, detail="Bạn đã điểm danh hôm nay rồi")
    
    # Đánh dấu đã điểm danh
    attendances[weekday] = 1
    
    # Tính streak mới
    streak = calculate_streak(attendances)
    
    # Tính số sao thưởng
    stars_to_add = calculate_reward(streak)
    
    # Cập nhật thông tin user
    user.attendances = json.dumps(attendances)
    user.stars = (user.stars or 0) + stars_to_add
    user.updated_at = today
    db.commit()
    db.refresh(user)

    return {
        "message": "Điểm danh thành công!",
        "streak": streak,
        "stars_earned": stars_to_add,
        "total_stars": user.stars,
        "attendances": attendances
    }
