from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User
from app.core.auth import get_current_user
import datetime
import json

router = APIRouter(prefix="/attendance", tags=["attendance"])

@router.post("/", status_code=status.HTTP_200_OK)
def mark_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        return {"error": "User not found"}

    # Lấy ngày hiện tại và thứ trong tuần (0=Monday, 6=Sunday)
    today = datetime.datetime.now()
    weekday = today.weekday()

    # Lấy mảng attendance, nếu chưa có thì khởi tạo
    try:
        attendances = json.loads(user.attendances)
    except Exception:
        attendances = [0, 0, 0, 0, 0, 0, 0]

    # Kiểm tra tuần hiện tại (dựa vào ngày cập nhật gần nhất)
    last_update = user.updated_at or user.created_at or today
    last_week = last_update.isocalendar()[1]
    this_week = today.isocalendar()[1]
    if this_week != last_week:
        attendances = [0, 0, 0, 0, 0, 0, 0]

    # Đánh dấu điểm danh hôm nay
    attendances[weekday] = 1

    # Cộng sao nếu điểm danh lần đầu trong ngày
    stars = user.stars or 0
    if user.attendances is None or json.loads(user.attendances)[weekday] == 0:
        stars += 1

    # Cập nhật user
    user.attendances = json.dumps(attendances)
    user.stars = stars
    user.updated_at = today
    db.commit()
    db.refresh(user)

    return {
        "stars": user.stars,
        "attendances": attendances
    }
