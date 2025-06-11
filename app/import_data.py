from app.services.question_service import QuestionService
from app.core.database import SessionLocal

def import_data():
    db = SessionLocal()
    try:
        # Import tất cả câu hỏi
        QuestionService.import_all_questions(db)
        print("Import dữ liệu thành công!")
    except Exception as e:
        print(f"Lỗi khi import dữ liệu: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    import_data() 