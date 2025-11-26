from app.services.question_service import QuestionService
from docx import Document

if __name__ == "__main__":
    file_paths = {
        'DASS': r'E:\quangtm\AS_IT\Projects\AS_product_project\psychology\app\data\questions\DASS21.docx',
        'RADS': r'E:\quangtm\AS_IT\Projects\AS_product_project\psychology\app\data\questions\RADS30.docx',
    }
    output = None
    for test_type, file_path in file_paths.items():
        output = QuestionService.   read_questions_from_docx(self=QuestionService(),file_path=file_path)
        print(output)
