from docx import Document
import re
from sqlalchemy.orm import Session
from app.models.models import Test, Entity, Group, TestAnswer, Option
from typing import List, Dict, Any

class QuestionService:
    @staticmethod
    def read_questions_from_docx(file_path: str) -> List[Dict[str, Any]]:
        doc = Document(file_path)
        questions = []
        
        print(f"Đang đọc file: {file_path}")
        print(f"Số bảng trong file: {len(doc.tables)}")
        
        # Đọc từ bảng đầu tiên
        if len(doc.tables) > 0:
            table = doc.tables[0]
            print(f"Số hàng trong bảng: {len(table.rows)}")
            
            # In ra header để kiểm tra
            if len(table.rows) > 0:
                header = [cell.text.strip() for cell in table.rows[0].cells]
                print(f"Header của bảng: {header}")
            
            # Bỏ qua hàng header
            for row_idx, row in enumerate(table.rows[1:], 1):
                cells = row.cells
                print(f"\nĐang đọc hàng {row_idx}:")
                for cell_idx, cell in enumerate(cells):
                    print(f"Cột {cell_idx}: {cell.text.strip()}")
                
                if len(cells) >= 2:  # Cần ít nhất 2 cột: số thứ tự và nội dung
                    # Lấy nội dung từ cột 1 (cột "Câu hỏi")
                    statement_text = cells[1].text.strip()
                    print(f"Text câu tự sự: {statement_text}")
                    
                    if statement_text:  # Kiểm tra nếu có nội dung
                        questions.append({
                            'content': statement_text,
                            'options': [
                                {'level': 0, 'content': 'Không đúng với tôi chút nào cả'},
                                {'level': 1, 'content': 'Đúng với tôi phần nào, hoặc thỉnh thoảng mới đúng'},
                                {'level': 2, 'content': 'Đúng với tôi phần nhiều, hoặc phần lớn thời gian là đúng'},
                                {'level': 3, 'content': 'Hoàn toàn đúng với tôi, hoặc hầu hết thời gian là đúng'}
                            ]
                        })
                        print(f"Đã thêm câu tự sự: {statement_text}")
                    else:
                        print(f"Bỏ qua hàng {row_idx} vì không có nội dung")
        
        print(f"\nTổng số câu tự sự đọc được: {len(questions)}")
        return questions

    @staticmethod
    def import_questions_to_db(file_path: str, group_name: str, db: Session) -> None:
        try:
            # Lấy hoặc tạo group
            group = db.query(Group).filter_by(name=group_name).first()
            if not group:
                group = Group(name=group_name)
                db.add(group)
                db.flush()
            # Đọc câu hỏi từ file
            questions = QuestionService.read_questions_from_docx(file_path)
            for q in questions:
                # Kiểm tra đã tồn tại Test này chưa (dựa vào content và group_id)
                existing_test = db.query(Test).filter_by(content=q['content'], group_id=group.id).first()
                if existing_test:
                    continue
                test = Test(content=q['content'], group_id=group.id)
                db.add(test)
                db.flush()
                for opt in q['options']:
                     # Kiểm tra đã tồn tại Option này chưa (dựa vào test_id, content, level)
                    existing_option = db.query(Option).filter_by(test_id=test.id, content=opt['content'], level=opt['level']).first()
                    if existing_option:
                        continue
                    option = Option(test_id=test.id, content=opt['content'], level=opt['level'])
                    db.add(option)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Lỗi khi import vào database: {str(e)}")
            raise

    @staticmethod
    def import_all_questions(db: Session) -> None:
        # Đường dẫn tới các file câu hỏi và tên nhóm tương ứng
        file_paths = {
            'DASS': 'app/data/questions/TRẮC-NGHIỆM-LO-ÂU-TRẦM-CẢM.-STRESS-DASS.docx',
            'RADS': 'app/data/questions/TRẮC-NGHIỆM-ĐÁNH-GIÁ-TRẦM-CẢM-THANH-THIẾU-NIÊN-RADS.docx',
            'MDQ': 'app/data/questions/TRẮC-NGHIỆM-SÀNG-LỌC-RỐI-LOẠN-CẢM-XÚC-LƯỠNG-CỰC.docx'
        }
        
        for test_type, file_path in file_paths.items():
            print(f"\nĐang import file {file_path} vào nhóm {test_type}...")
            QuestionService.import_questions_to_db(file_path, test_type, db) 