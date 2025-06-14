from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Post

router = APIRouter(prefix="/post", tags=["post"])

@router.get("/")
def get_posts(
    page: int = Query(1, description="Page number", ge=1),
    db: Session = Depends(get_db)
):
    page_size = 10
    total_posts = db.query(Post).count()
    max_page = (total_posts + page_size - 1) // page_size
    posts = (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    post_list = [
        {
            "id": str(p.id),
            "title": p.title,
            "image": p.image,
            "content": p.content,
        }
        for p in posts
    ]
    return {"post": post_list, "maxPage": max_page}