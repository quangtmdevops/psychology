from app.core.database import SessionLocal
from app.services.question_service import QuestionService
from app.services.situational_service import SituationalService

def main():
    db = SessionLocal()
    # try:
    #     QuestionService.import_all_questions(db)
    #     print("Import questions completed successfully!")
    # except Exception as e:
    #     print(f"Error importing questions: {str(e)}")
        
    try: 
        SituationalService.import_situational_from_files(db)
        print("Import situational questions completed successfully!")
    except Exception as e:
        print(f"Error importing situational questions: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
