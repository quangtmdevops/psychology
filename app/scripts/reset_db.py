from app.core.database import Base, engine
from app.models.models import User, Group, SubGroup, Test, TestAnswer, Post, Entity, SituationalQuestion, SituationalAnswer
from sqlalchemy import inspect

def reset_database():
    # Get inspector to check existing tables
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if existing_tables:
        print("Found existing tables, dropping them...")
        # Drop all tables in reverse order of dependencies
        Base.metadata.drop_all(bind=engine)
        print("✓ Dropped all existing tables")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Created all tables")
    
    print("Database has been reset successfully!")

if __name__ == "__main__":
    reset_database() 