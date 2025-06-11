from docx import Document
import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import Test, Group, SubGroup

def read_docx_file(file_path):
    doc = Document(file_path)
    questions = []
    current_question = None
    
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
            
        # Check if this is a question (starts with a number)
        if text[0].isdigit() and '.' in text[:5]:
            if current_question:
                questions.append(current_question)
            current_question = {
                'content': text,
                'order': len(questions) + 1
            }
        elif current_question:
            # This is part of the current question
            current_question['content'] += f"\n{text}"
    
    if current_question:
        questions.append(current_question)
    
    return questions

def import_questions():
    db = SessionLocal()
    try:
        # Get the directory containing the question files
        questions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'questions')
        
        # Create a group for psychological tests
        group = Group(
            name="Psychological Tests",
            description="Collection of psychological assessment tests"
        )
        db.add(group)
        db.flush()
        
        # Create subgroups for each test type
        subgroups = {
            'anxiety_depression': SubGroup(
                name="Anxiety and Depression Assessment",
                description="Tests for anxiety, depression, and stress levels",
                group_id=group.id
            ),
            'youth_depression': SubGroup(
                name="Youth Depression Assessment",
                description="Tests specifically for youth depression",
                group_id=group.id
            ),
            'bipolar': SubGroup(
                name="Bipolar Disorder Screening",
                description="Tests for bipolar disorder screening",
                group_id=group.id
            )
        }
        
        for subgroup in subgroups.values():
            db.add(subgroup)
        db.flush()
        
        # Process each file
        file_mapping = {
            'TRẮC-NGHIỆM-LO-ÂU-TRẦM-CẢM.-STRESS-DASS.docx': 'anxiety_depression',
            'TRẮC-NGHIỆM-ĐÁNH-GIÁ-TRẦM-CẢM-THANH-THIẾU-NIÊN-RADS.docx': 'youth_depression',
            'TRẮC-NGHIỆM-SÀNG-LỌC-RỐI-LOẠN-CẢM-XÚC-LƯỠNG-CỰC.docx': 'bipolar'
        }
        
        for filename, subgroup_key in file_mapping.items():
            file_path = os.path.join(questions_dir, filename)
            questions = read_docx_file(file_path)
            
            for question_data in questions:
                test = Test(
                    content=question_data['content'],
                    order=question_data['order']
                )
                db.add(test)
            
            db.flush()
        
        db.commit()
        print("Successfully imported all questions!")
        
    except Exception as e:
        db.rollback()
        print(f"Error importing questions: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    import_questions()