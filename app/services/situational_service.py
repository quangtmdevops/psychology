from docx import Document
import re

from app.models.models import (
    SituationalQuestion,
    SituationalAnswer,
    User,
    SituationalUserAnswer,

)
from sqlalchemy.orm import Session


class SituationalService:
    # ... các hàm khác ...

    @staticmethod
    def read_situations_from_docs():
        filename = 'app/data/situation/situation_ques.docx'
        doc = Document(filename)
        situations = []

        current_level = None

        for table in doc.tables:
            for row in table.rows:
                # Lấy text từ các cell, loại bỏ khoảng trắng thừa
                cells = [cell.text.strip() for cell in row.cells]
                cell_text = row.cells[0].text.strip()
                # Bỏ qua hàng tiêu đề
                if not cells or cells[0] in ['STT', '']:
                    continue

                # Phát hiện dòng Level (nằm ngoài bảng hoặc trong cell đầu tiên)
                if cells[0].startswith('LEVEL') or 'LEVEL' in cells[0]:
                    # Lấy tên level, bỏ emoji
                    if re.search(r'level', cell_text, re.IGNORECASE):
                        match = re.search(r'\d+', cell_text)
                        if match:
                            current_level = int(match.group())  # ← chỉ lấy số, kiểu int
                    continue

                # Chỉ xử lý các hàng có STT là số
                if not cells or not cells[0].isdigit():
                    continue

                stt = cells[0]

                # Một số file ghi tình huống ở cột 1, phương án ở cột 2, giải thích ở cột 3
                # Nhưng trong file của bạn có cấu trúc: STT | Tình huống | Phương án | Giải thích
                if len(cells) < 4:
                    continue

                tinh_huong = cells[1]
                phuong_an_raw = cells[2]
                giai_thich_raw = cells[3]

                # Xử lý phần đáp án đúng (in đậm trong file gốc)
                # Trong python-docx, text in đậm vẫn chỉ là text thường, nhưng thường có dòng:
                # "Đáp án đúng là C. ..." hoặc không có
                dap_an_giai_thich = giai_thich_raw

                # Nếu có dòng riêng "Đáp án đúng là...", ưu tiên lấy nó + giải thích
                if "Đáp án đúng là" in giai_thich_raw:
                    dap_an_giai_thich = giai_thich_raw
                # Nếu không, tìm trong phương án hoặc giải thích dòng bắt đầu bằng "Đáp án đúng"
                elif "Đáp án đúng" in phuong_an_raw:
                    dap_an_giai_thich = phuong_an_raw.split("Đáp án đúng")[1] + "\n" + giai_thich_raw
                elif giai_thich_raw:
                    # Một số tình huống Level 3 không có "Đáp án đúng là" mà giải thích luôn mang tính khẩn cấp
                    dap_an_giai_thich = giai_thich_raw

                situations.append({
                    "level": current_level or "Unknown",
                    "question_content": tinh_huong.strip(),
                    "options": phuong_an_raw.strip(),
                    "answer_content": dap_an_giai_thich.strip()
                })

        return situations

    @staticmethod
    def import_situational_from_files(db: Session) -> None:
        data = SituationalService.read_situations_from_docs()
        imported = 0

        for item in data:
            level = item["level"]
            question_raw = item["question_content"].strip()
            options_raw = item["options"].strip()
            answer_raw = item["answer_content"].strip()

            if not question_raw:
                continue

            # === 1. Xử lý đáp án & giải thích ===
            explanation = ""
            answer_main = answer_raw

            if "Giải thích chuyên gia:" in answer_raw:
                parts = answer_raw.split("Giải thích chuyên gia:", 1)
                answer_main = parts[0].strip()
                explanation = "Giải thích chuyên gia:" + parts[1].strip()

            # Lấy đáp án đúng (A/B/C/D)
            correct_letter = None
            text = answer_main.lower()
            for keyword in ["đáp án đúng", "đáp án", "đúng là", "correct", "answer"]:
                if keyword in text:
                    match = re.search(f"{keyword}[:\s]*([a-d])", text)
                    if match:
                        correct_letter = match.group(1).upper()
                        break
            if not correct_letter:
                print(f"[KHÔNG TÌM THẤY Đáp án đúng] {answer_main}")

            # === 2. Tạo nội dung câu hỏi đầy đủ ===
            full_content = question_raw
            if answer_main:
                full_content += "\n" + answer_main
            if explanation:
                full_content += "\n" + explanation

            # Kiểm tra trùng (content + level)
            if db.query(SituationalQuestion).filter_by(
                    content=full_content,
                    level=level
            ).first():
                continue

            # === 3. Tạo câu hỏi ===
            question = SituationalQuestion(
                content=full_content,
                level=level
            )
            db.add(question)
            db.flush()

            # === 4. Tách và xử lý các phương án (QUAN TRỌNG NHẤT) ===
            option_lines = [
                line.strip() for line in options_raw.replace("\r", "\n").split("\n")
                if line.strip()
            ]

            for line in option_lines:
                # Bỏ khoảng trắng đầu/cuối, chuẩn hóa dấu chấm
                line = line.strip()
                if not line:
                    continue

                # Tìm chữ cái đầu tiên (A, B, C, D) theo sau là dấu chấm hoặc khoảng trắng
                opt_match = re.match(r"^([A-D])[.\)\s]+(.*)", line, re.IGNORECASE)
                if not opt_match:
                    # Một số file viết kiểu "A Làm gì đó" (không có dấu .)
                    opt_match = re.match(r"^([A-D])\s+(.*)", line, re.IGNORECASE)

                if not opt_match:
                    print(f"[SKIP] Không parse được phương án: {line}")
                    continue

                letter = opt_match.group(1).upper()
                content = opt_match.group(2).strip()

                # Loại bỏ dấu chấm thừa ở đầu nội dung nếu có
                if content.startswith(('.', ')', ':', '-')):
                    content = content[1:].strip()

                is_correct = (letter == correct_letter)

                answer = SituationalAnswer(
                    question_id=question.id,
                    content=content,        # ← chỉ lấy nội dung, KHÔNG có A. B. nữa
                    is_correct=is_correct
                )
                db.add(answer)

            db.flush()
            imported += 1
            print(f"✓ Đã thêm câu hỏi Level {level} - ID: {question.id} | Đáp án đúng: {correct_letter}")

        db.commit()
        print(f"\n=== HOÀN TẤT: Đã import {imported} câu hỏi tình huống ===")

    @staticmethod
    def get_progress(db: Session, current_user: User):
        user_id = current_user.id
        questions = (
            db.query(SituationalQuestion)
            .filter()
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
    def get_situational_questions(level: int, db: Session, current_user: User):
        questions = db.query(SituationalQuestion) \
            .filter(SituationalQuestion.level == level) \
            .all()

        result = []
        for q in questions:
            q_content = q.content
            explanation = ""

            if "Giải thích chuyên gia:" in q.content:
                parts = q.content.split("Giải thích chuyên gia:", 1)
                q_content = parts[0].strip()
                explanation = parts[1].strip()

            answers = db.query(SituationalAnswer) \
                .filter(SituationalAnswer.question_id == q.id) \
                .all()

            answer_list = [
                {"id": a.id, "content": a.content, "isCorrect": bool(a.is_correct)}
                for a in answers
            ]

            result.append({
                "id": q.id,
                "content": q_content,
                "explanation": explanation,
                "answers": answer_list,
            })

        return result

    @staticmethod
    def check_and_update_stars(answers: list, user_id: int, db: Session) -> int:
        stars_earned = 0
        for ans in answers:
            answer_id = int(ans["answerId"])
            situ_answer = db.query(SituationalAnswer).get(answer_id)
            if situ_answer and situ_answer.is_correct:
                stars_earned += 1

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
            user_answer = SituationalUserAnswer(
                user_id=user_id,
                question_id=int(ans["situationalId"]),
                answer_id=int(ans["answerId"]),
            )
            db.add(user_answer)

            situ_answer = db.query(SituationalAnswer).get(int(ans["answerId"]))
            if situ_answer and situ_answer.is_correct:
                correct_count += 1

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.stars = (user.stars or 0) + correct_count
            db.commit()
            db.refresh(user)
            return {"stars": user.stars}

        db.commit()
        return {"stars": 0}
