from app.services.question_service import QuestionService
import json
import os
from app.services.situational_service import SituationalService

def test_read_questions():
    # # Đường dẫn tới file cần test
    # file_path = 'app/data/questions/TRẮC-NGHIỆM-LO-ÂU-TRẦM-CẢM.-STRESS-DASS.docx'
    
    # try:
    #     # Đọc câu hỏi từ file
    #     questions = QuestionService.read_questions_from_docx(file_path)
        
    #     # In thông tin tổng quan
    #     print(f"\nTổng số câu tự sự đọc được: {len(questions)}")
        
    #     # In chi tiết từng câu tự sự
    #     for i, question in enumerate(questions, 1):
    #         print(f"\nCâu tự sự {i}:")
    #         print(f"Nội dung: {question['content']}")
    #         print("Các lựa chọn trả lời:")
    #         for option in question['options']:
    #             print(f"  - Level {option['level']}: {option['content']}")
        
    #     # Tạo thư mục output nếu chưa tồn tại
    #     output_dir = 'output'
    #     if not os.path.exists(output_dir):
    #         os.makedirs(output_dir)
        
    #     # Lưu kết quả vào file JSON với định dạng đẹp
    #     output_file = os.path.join(output_dir, 'test_questions_output.json')
    #     with open(output_file, 'w', encoding='utf-8') as f:
    #         json.dump({
    #             'total_questions': len(questions),
    #             'questions': questions
    #         }, f, ensure_ascii=False, indent=2)
            
    #     print(f"\nĐã lưu kết quả vào file {output_file}")
    #     print(f"Tổng số câu tự sự: {len(questions)}")
            
    # except Exception as e:
    #     print(f"Lỗi khi đọc file: {str(e)}")
    
    data = SituationalService.read_situational_from_files(r"E:\quangtm\AS_IT\Projects\AS_product_project\psychology\app\data\situation")
    for item in data:
        print(item)

if __name__ == "__main__":
    test_read_questions() 