from . import  posts, test, users
from . import auth  # noqa: F401
from .users import router as users
from .posts import router as posts
from .test import router as test