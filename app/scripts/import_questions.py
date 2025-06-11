from app.core.database import SessionLocal
from app.services.question_service import QuestionService

def main():
    db = SessionLocal()
    try:
        QuestionService.import_all_questions(db)
        print("Import questions completed successfully!")
    except Exception as e:
        print(f"Error importing questions: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
