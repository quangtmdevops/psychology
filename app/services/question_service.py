from docx import Document
import re
from sqlalchemy.orm import Session
from app.models.models import Test, Group, Option
from typing import List, Dict, Any


class QuestionService:
    @staticmethod
    def read_questions_from_docx(file_path: str) -> List[Dict[str, Any]]:
        print(f"Đang đọc file: {file_path}")
        questions = []
        doc = Document(file_path)
        lines = [p.text for p in doc.paragraphs]
        for result in QuestionService.parse_questionnaire(lines, type="DASS" if 'DASS' in file_path else 'RADS'):
            questions.append(result)

        return questions

    @staticmethod
    def import_questions_to_db(file_path: str, group_name: str, db: Session) -> None:
        try:
            # Đọc câu hỏi từ file
            questions = QuestionService.read_questions_from_docx(file_path)
            # Lấy hoặc tạo group
            group = db.query(Group).filter_by(name=group_name).first()
            if not group:
                group = Group(name=group_name)
                db.add(group)
                db.flush()

            for q in questions:
                existing_test = db.query(Test).filter_by(content=q['content'], group_id=group.id).first()
                if existing_test:
                    continue
                test = Test(content=q['content'], group_id=group.id, code=q.get('code'))
                db.add(test)
                db.flush()
                for level, content in q['options'].items():
                    existing_option = db.query(Option).filter_by(test_id=test.id, content=content,
                                                                 level=level).first()
                    if existing_option:
                        continue
                    option = Option(test_id=test.id, content=content, level=level)
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
            'DASS': 'app/data/questions/DASS21.docx',
            'RADS': 'app/data/questions/RADS30.docx',
        }

        for test_type, file_path in file_paths.items():
            print(f"\nĐang import file {file_path} vào nhóm {test_type}...")
            QuestionService.import_questions_to_db(file_path, test_type, db)

    @staticmethod
    def parse_questionnaire(lines, type="DASS"):
        results = []

        if type == "DASS":
            options = {
                0: "Không đúng với tôi chút nào cả",
                1: "Đúng với tôi phần nào hoặc thỉnh thoảng mới đúng",
                2: "Đúng với tôi khá nhiều, hoặc hầu hết thời gian",
                3: "Đúng với tôi hầu hết thời gian, hoặc rất đúng với tôi"
            }

            # Mapping mã code
            depression = {3, 5, 10, 13, 16, 17, 21}
            anxiety = {2, 4, 7, 9, 15, 19, 20}
            stress = {1, 6, 8, 11, 12, 14, 18}

        elif type == "RADS":
            options = {
                0: "Hầu như không",
                1: "Thỉnh thoảng",
                2: "Phần lớn thời gian",
                3: "Hầu hết hoặc tất cả thời gian"
            }

            # RADS không có code
            depression = set()
            anxiety = set()
            stress = set()

        else:
            raise ValueError("mode phải là 'dass' hoặc 'rads'")

        # ========================
        # 2) Xử lý từng dòng
        # ========================
        for line in lines:
            line = line.strip()

            # Tìm dòng dạng "Đề mục X: Nội dung"
            match = re.match(r"Đề mục\s+(\d+)\s*:\s*(.*)", line)
            if match:
                num = int(match.group(1))
                content = match.group(2).strip()

                # Xác định code
                if num in depression:
                    code_value = "D"
                elif num in anxiety:
                    code_value = "A"
                elif num in stress:
                    code_value = "S"
                else:
                    code_value = None

                # Đẩy item vào list
                results.append({
                    'content': content,
                    'code': code_value,
                    'options': options
                })

        return results
