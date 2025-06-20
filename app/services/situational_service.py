import os
import re

from fastapi import Depends, Query
from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.models import (
    SituationalQuestion,
    SituationalAnswer,
    User,
    SituationalUserAnswer,
    SituationGroup,
)
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from docx import Document


class SituationalService:
    # ... các hàm khác ...

    @staticmethod
    def read_situational_from_files() -> List[Dict[str, Any]]:
        """
        Đọc các file docx trong thư mục mặc định, trích xuất dữ liệu và trả về list dict.
        """
        data = []
        # Đường dẫn mặc định tới thư mục chứa file situational
        directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'situation')
        if not os.path.exists(directory):
            return data  # hoặc raise Exception nếu muốn báo lỗi
        for filename in os.listdir(directory):
            if not filename.endswith(".docx"):
                continue
            # Lấy level từ tên file
            doc = Document(os.path.join(directory, filename))
            content = "\n".join([p.text for p in doc.paragraphs])
            match = re.search(r"(\d+)", filename)
            level = int(match.group(1)) if match else None

            # Xác định situation_group_id dựa trên tên của file
            situation_group_id = None
            lowered_filename = filename.lower()
            if "bạn bè" in lowered_filename:
                situation_group_id = 1  # Bạn bè
            elif "thầy cô" in lowered_filename:
                situation_group_id = 2  # Thầy cô
            elif "cha mẹ" in lowered_filename:
                situation_group_id = 3  # Cha mẹ
            elif "anh em" in lowered_filename:
                situation_group_id = 4  # Anh em

            # Tách các block tình huống
            blocks = re.split(r"(Tình huống.*?\?)", content, flags=re.DOTALL)
            for i in range(1, len(blocks), 2):
                question_block = blocks[i] + (
                    blocks[i + 1] if i + 1 < len(blocks) else ""
                )
                # Lấy content câu hỏi
                question_match = re.search(
                    r"(Tình huống.*?\?)", question_block, flags=re.DOTALL
                )
                question_content = (
                    question_match.group(1).strip() if question_match else None
                )

                # Lấy các lựa chọn
                options_match = re.search(
                    r"(A\..*?D\..*?)(?=\n|$)", question_block, flags=re.DOTALL
                )
                options_content = (
                    options_match.group(1).strip() if options_match else None
                )
                options = []
                options_content = options_content.strip() if options_content else ""
                if options_content:
                    current_option = ""
                    for line in options_content.splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        if re.match(r"^[A-D]\.", line):
                            if current_option:
                                options.append(current_option.strip())
                            current_option = line
                        else:
                            current_option += " " + line
                    if current_option:
                        options.append(current_option.strip())

                # Lấy đáp án
                answer_match = re.search(
                    r"(Đáp án đúng.*?)(?=Tình huống|$)", question_block, flags=re.DOTALL
                )
                answer_content = answer_match.group(1).strip() if answer_match else None

                data.append(
                    {
                        "level": level,
                        "situation_group_id": situation_group_id,
                        "question_content": question_content,
                        "options": options,
                        "answer_content": answer_content,
                    }
                )
        return data

    @staticmethod
    def import_situational_from_files(db: Session) -> None:
        """
        Đọc các file docx trong thư mục, trích xuất dữ liệu và import vào DB.
        """
        # Tạo các nhóm tình huống nếu chưa tồn tại
        situation_groups = {
            1: {"name": "Bạn bè", "description": "Các tình huống liên quan đến bạn bè"},
            2: {"name": "Thầy cô", "description": "Các tình huống liên quan đến thầy cô"},
            3: {"name": "Cha mẹ", "description": "Các tình huống liên quan đến cha mẹ"},
            4: {"name": "Anh em", "description": "Các tình huống liên quan đến anh em"},
        }
        
        for group_id, group_data in situation_groups.items():
            group = db.query(SituationGroup).filter(SituationGroup.id == group_id).first()
            if not group:
                group = SituationGroup(
                    id=group_id,
                    name=group_data["name"],
                    description=group_data["description"]
                )
                db.add(group)
        db.commit()

        data = SituationalService.read_situational_from_files()
        for item in data:
            # Nếu đáp án đúng có phần 'Giải thích chuyên gia:', tách phần này ra khỏi answer_content và nối vào content của câu hỏi
            explanation = ""
            answer_content = item["answer_content"] or ""
            if "Giải thích chuyên gia:" in answer_content:
                parts = answer_content.split("Giải thích chuyên gia:", 1)
                answer_content_main = parts[0].strip()
                explanation = "Giải thích chuyên gia:" + parts[1].strip()
            else:
                answer_content_main = answer_content
            # Nối answer_content_main vào content câu hỏi nếu có
            full_content = item["question_content"]
            if answer_content_main:
                full_content += "\n" + answer_content_main
            if explanation:
                full_content += "\n" + explanation
            # Kiểm tra đã tồn tại câu hỏi này chưa (dựa vào content, level, situation_group_id)
            existing_question = db.query(SituationalQuestion).filter_by(
                content=full_content,
                level=item["level"],
                situation_group_id=item["situation_group_id"]
            ).first()
            if existing_question:
                continue
            situ_question = SituationalQuestion(
                content=full_content,
                level=item["level"],
                situation_group_id=item["situation_group_id"],
            )
            db.add(situ_question)
            db.flush()  # để lấy id
            # Lấy ký tự đáp án đúng từ answer_content_main
            correct_letter = None
            if answer_content_main:
                match = re.search(r"Đáp án đúng[:：]? ?([A-D])", answer_content_main)
                if match:
                    correct_letter = match.group(1)
            # Tạo các lựa chọn
            for opt in item["options"]:
                is_correct = False
                answer_text = opt
                if correct_letter and opt.startswith(f"{correct_letter}."):
                    is_correct = True
                situ_answer = SituationalAnswer(
                    question_id=situ_question.id,
                    content=answer_text,
                    is_correct=is_correct,
                )
                db.add(situ_answer)
            db.flush()
            print("Đã thêm câu hỏi:", situ_question.content)
        db.commit()

    @staticmethod
    def get_progress(group: int, db: Session, current_user: User):
        user_id = current_user.id
        questions = (
            db.query(SituationalQuestion)
            .filter(SituationalQuestion.situation_group_id == group)
            .all()
        )
        # Đếm tổng số câu hỏi theo level
        level_count = {}
        for q in questions:
            level_count.setdefault(q.level, 0)
            level_count[q.level] += 1
        # Đếm số câu đã trả lời của user theo level
        user_answers = (
            db.query(SituationalUserAnswer)
            .filter(SituationalUserAnswer.user_id == user_id)
            .all()
        )
        answered_count = {}
        for ans in user_answers:
            q = (
                db.query(SituationalQuestion)
                .filter(SituationalQuestion.id == ans.question_id)
                .first()
            )
            if q:
                answered_count.setdefault(q.level, set())
                answered_count[q.level].add(q.id)
        result = []
        for level in sorted(level_count.keys()):
            result.append(
                {
                    "level": level,
                    "current": len(answered_count.get(level, set())),
                    "total": level_count[level],
                }
            )
        return result

    @staticmethod
    def get_situational_questions(group: int, level: int, db: Session, current_user: User):
        questions = (
            db.query(SituationalQuestion)
            .filter(
                SituationalQuestion.situation_group_id == group,
                SituationalQuestion.level == level,
            )
            .all()
        )
        result = []
        for q in questions:
            explanation = ""
            if "Giải thích chuyên gia:" in q.content:
                parts = q.content.split("Giải thích chuyên gia:", 1)
                q_content = parts[0].strip()
                explanation = parts[1].strip()
            else:
                q_content = q.content
            answers = (
                db.query(SituationalAnswer)
                .filter(SituationalAnswer.question_id == q.id)
                .all()
            )
            answer_list = [
                {"id": a.id, "content": a.content, "isCorrect": bool(a.is_correct)}
                for a in answers
            ]
            result.append(
                {
                    "id": q.id,
                    "content": q_content,
                    "explanation": explanation,
                    "answers": answer_list,
                }
            )
        return result

    @staticmethod
    def check_and_update_stars(answers: list, user_id: int, db: Session) -> int:
        """
        Kiểm tra các đáp án, cộng 1 sao cho mỗi đáp án đúng, cập nhật vào user và trả về số sao mới.
        """
        stars_earned = 0
        for ans in answers:
            answer_id = int(ans["answerId"])
            # Kiểm tra đáp án đúng
            situ_answer = db.query(SituationalAnswer).filter(SituationalAnswer.id == answer_id).first()
            if situ_answer and situ_answer.is_correct:
                stars_earned += 1
        # Cộng sao cho user
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.stars = (user.stars or 0) + stars_earned
            db.commit()
            db.refresh(user)
            return user.stars
        return 0

    @staticmethod
    def submit_situational_answers(answers: list, user_id: int, db: Session):
        correct_count = 0
        for ans in answers:
            # Lưu đáp án của user
            user_answer = SituationalUserAnswer(
                user_id=user_id,
                question_id=int(ans["situationalId"]),
                answer_id=int(ans["answerId"]),
            )
            db.add(user_answer)
            # Kiểm tra đáp án đúng
            situ_answer = db.query(SituationalAnswer).filter(SituationalAnswer.id == int(ans["answerId"])).first()
            if situ_answer and situ_answer.is_correct:
                correct_count += 1
        # Cộng sao cho user
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.stars = (user.stars or 0) + correct_count
            db.commit()
            db.refresh(user)
            return {"stars": user.stars}
        db.commit()
        return {"stars": 0}
