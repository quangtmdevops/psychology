from app.core.database import Base, engine
from app.models.models import User, TestAnswer

def drop_tables():
    # Drop tables in reverse order of dependencies
    TestAnswer.__table__.drop(engine, checkfirst=True)
    User.__table__.drop(engine, checkfirst=True)
    print("Tables dropped successfully!")

if __name__ == "__main__":
    drop_tables() 