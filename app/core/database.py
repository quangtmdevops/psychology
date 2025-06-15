import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

DATABASE_URL = settings.get_database_url()

# Print database connection URL
print("="*50)
print("Database Connection URL:", DATABASE_URL)
print("="*50)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Add this function:
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()