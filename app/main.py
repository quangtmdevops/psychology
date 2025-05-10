from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.routers import users, groups
from app.core.auth import get_current_user
from app.models.models import User

# Create database tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Psychology API",
    description="API for Psychology Application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with authentication
app.include_router(users.router, prefix="/api/v1")
app.include_router(groups.router, prefix="/api/v1", dependencies=[Depends(get_current_user)])

@app.get("/")
async def root():
    return {"message": "Welcome to Psychology API"} 