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
        - Mặc định Level = 1 cho tới khi gặp dòng "Level X" thì chuyển level hiện hành.
        - Mỗi câu hỏi bắt đầu bằng "Tình huống" và kết thúc trước tiêu đề "Tình huống" tiếp theo hoặc "Level".
        """
        data = []
        # Đường dẫn mặc định tới thư mục chứa file situational
        directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'situation')
        if not os.path.exists(directory):
            return data  # hoặc raise Exception nếu muốn báo lỗi
        for filename in os.listdir(directory):
            if not filename.endswith(".docx"):
                continue
            doc = Document(os.path.join(directory, filename))

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

            # Duyệt theo từng đoạn văn để cập nhật level và gom block câu hỏi
            current_level = 1
            i = 0
            paragraphs = [p.text.strip() for p in doc.paragraphs]
            total = len(paragraphs)
            while i < total:
                line = paragraphs[i]
                if not line:
                    i += 1
                    continue
                # Cập nhật level khi gặp dòng Level X
                # level_m = re.match(r"^Level\s*(\d+)", line, flags=re.IGNORECASE)
                level_m = re.match(r"^\s*Level\s*(\d+)", line, flags=re.IGNORECASE)
                if level_m:
                    try:
                        current_level = int(level_m.group(1))
                    except Exception:
                        current_level = 1
                    i += 1
                    continue

                # Bắt đầu một câu hỏi
                if re.match(r"^Tình huống", line, flags=re.IGNORECASE):
                    buffer_lines = [line]
                    j = i + 1
                    while j < total:
                        next_line = paragraphs[j]
                        # Ngắt khi gặp tiêu đề Level hoặc tiêu đề câu hỏi tiếp theo
                        if re.match(r"^Level\s*\d+", next_line, flags=re.IGNORECASE) or \
                           re.match(r"^Tình huống", next_line, flags=re.IGNORECASE):
                            break
                        buffer_lines.append(next_line)
                        j += 1

                    question_block = "\n".join([l for l in buffer_lines if l is not None])

                    # Phân tách block theo dòng để xác định phần câu hỏi, lựa chọn và đáp án
                    lines = [ln.strip() for ln in question_block.splitlines()]
                    # Tìm vị trí bắt đầu options và đáp án
                    opt_idx = None
                    ans_idx = None
                    for idx, ln in enumerate(lines):
                        if opt_idx is None and re.match(r"^[A-E][\.)]?\s", ln):
                            opt_idx = idx
                        if ans_idx is None and (ln.startswith("Đáp án") or ln.startswith("Đáp án đúng")):
                            ans_idx = idx
                        if opt_idx is not None and ans_idx is not None:
                            break

                    # Xác định ranh giới các phần
                    cut_idx_candidates = []
                    if opt_idx is not None:
                        cut_idx_candidates.append(opt_idx)
                    if ans_idx is not None:
                        cut_idx_candidates.append(ans_idx)
                    end_question_idx = min(cut_idx_candidates) if cut_idx_candidates else len(lines)

                    # Gom phần câu hỏi từ đầu block tới trước options/đáp án
                    question_part = lines[:end_question_idx]
                    # Loại bỏ dòng trống đầu/cuối
                    while question_part and not question_part[0]:
                        question_part.pop(0)
                    while question_part and not question_part[-1]:
                        question_part.pop()
                    question_content = "\n".join(question_part) if question_part else None

                    # Lấy các lựa chọn: từ opt_idx tới trước ans_idx
                    options: List[str] = []
                    if opt_idx is not None:
                        end_opt_idx = ans_idx if ans_idx is not None else len(lines)
                        option_lines = lines[opt_idx:end_opt_idx]
                        current_option = ""
                        for opt_line in option_lines:
                            if re.match(r"^[A-E][\.)]?\s", opt_line):
                                if current_option:
                                    options.append(current_option.strip())
                                current_option = opt_line
                            else:
                                current_option = (current_option + " " + opt_line).strip()
                        if current_option:
                            options.append(current_option.strip())

                    # Lấy đáp án: từ ans_idx đến hết block
                    answer_content = None
                    if ans_idx is not None:
                        answer_content = "\n".join(lines[ans_idx:]).strip() or None

                    data.append(
                        {
                            "level": current_level,
                            "situation_group_id": situation_group_id,
                            "question_content": question_content,
                            "options": options,
                            "answer_content": answer_content,
                        }
                    )
                    i = j
                    continue

                i += 1
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
            # Bỏ qua nếu không có content câu hỏi hợp lệ hoặc thiếu group
            if not item.get("question_content"):
                continue
            if not item.get("situation_group_id"):
                continue
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
