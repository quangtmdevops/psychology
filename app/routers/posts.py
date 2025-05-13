from fastapi import APIRouter

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/")
def list_posts():
    return []