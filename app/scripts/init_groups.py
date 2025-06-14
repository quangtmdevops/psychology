from app.core.database import SessionLocal
from app.models.models import Group

def init_groups():
    db = SessionLocal()
    try:
        # Check if groups already exist
        existing_groups = db.query(Group).all()
        if existing_groups:
            print("Groups already exist in the database")
            return

        # Create groups
        groups = [
            Group(id=1, name="Bạn bè", description="Các tình huống liên quan đến bạn bè"),
            Group(id=2, name="Thầy cô", description="Các tình huống liên quan đến thầy cô"),
            Group(id=3, name="Cha mẹ", description="Các tình huống liên quan đến cha mẹ"),
            Group(id=4, name="Anh em", description="Các tình huống liên quan đến anh em"),
        ]

        for group in groups:
            db.add(group)
        
        db.commit()
        print("Successfully initialized groups in the database")
    except Exception as e:
        print(f"Error initializing groups: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_groups() 