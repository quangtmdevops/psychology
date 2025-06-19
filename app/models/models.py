from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# models for design schema of database


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # Store hashed password
    is_premium = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    reward = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # New fields for API response compatibility
    username = Column(
        String, unique=True, index=True, nullable=True
    )  # Username for login/display
    display_name = Column(String, nullable=True)  # Display name
    dob = Column(String, nullable=True)  # Date of birth (format: dd/mm/yyyy)
    attendances = Column(
        String, default="[0,0,0,0,0,0,0]"
    )  # JSON string for attendance array
    image = Column(String, nullable=True)  # Profile image URL
    stars = Column(Integer, default=0)  # Total stars earned
    free_chat = Column(Integer, default=0)  # Free chat count

    # Relationships
    posts = relationship("Post", back_populates="author")
    entities = relationship("Entity", back_populates="user")
    situational_progress = relationship("UserSituationalProgress", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}', display_name='{self.display_name}', dob='{self.dob}', attendances='{self.attendances}', image='{self.image}', stars={self.stars}, is_premium={self.is_premium}, free_chat={self.free_chat})>"

    def __str__(self):
        return f"User {self.email}"


class Group(Base):
    __tablename__ = "group"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    code = Column(String(255), nullable=True)

    sub_groups = relationship("SubGroup", back_populates="group")
    tests = relationship("Test", back_populates="group")

    def __repr__(self):
        return f"<Group(id={self.id}, name='{self.name}', code='{self.code}')>"

    def __str__(self):
        return f"Group: {self.name}"


class SubGroup(Base):
    __tablename__ = "sub_group"

    id = Column(Integer, primary_key=True)
    group_id = Column(
        Integer, ForeignKey("group.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    description = Column(Text)

    group = relationship("Group", back_populates="sub_groups")

    def __repr__(self):
        return f"<SubGroup(id={self.id}, name='{self.name}', group_id={self.group_id})>"

    def __str__(self):
        return f"SubGroup: {self.name}"


class SituationGroup(Base):
    __tablename__ = "situation_group"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    situational_questions = relationship("SituationalQuestion", back_populates="situation_group")

    def __repr__(self):
        return f"<SituationGroup(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return f"Situation Group: {self.name}"


class SituationalQuestion(Base):
    __tablename__ = "situational_question"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    order = Column(Integer)
    situation_group_id = Column(Integer, ForeignKey("situation_group.id"), nullable=False)
    level = Column(Integer, nullable=False)

    situation_group = relationship("SituationGroup", back_populates="situational_questions")
    answers = relationship("SituationalAnswer", back_populates="question")
    user_progress = relationship("UserSituationalProgress", back_populates="question")

    def __repr__(self):
        return f"<SituationalQuestion(id={self.id}, order={self.order}, level={self.level})>"

    def __str__(self):
        return f"Situational Question #{self.order} (Level {self.level})"


class SituationalAnswer(Base):
    __tablename__ = "situational_answer"

    id = Column(Integer, primary_key=True)
    question_id = Column(
        Integer,
        ForeignKey("situational_question.id", ondelete="CASCADE"),
        nullable=False,
    )
    content = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)

    question = relationship("SituationalQuestion", back_populates="answers")

    def __repr__(self):
        return f"<SituationalAnswer(id={self.id}, question_id={self.question_id}, is_correct={self.is_correct})>"

    def __str__(self):
        return f"Answer: {self.content[:30]}..."


class UserSituationalProgress(Base):
    __tablename__ = "user_situational_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("situational_question.id", ondelete="CASCADE"), nullable=False)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="situational_progress")
    question = relationship("SituationalQuestion", back_populates="user_progress")

    def __repr__(self):
        return f"<UserSituationalProgress(id={self.id}, user_id={self.user_id}, question_id={self.question_id}, is_completed={self.is_completed})>"

    def __str__(self):
        return f"Progress: User {self.user_id} - Question {self.question_id}"


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    audio = Column(Text)
    image = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    author_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Relationship
    author = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}')>"

    def __str__(self):
        return f"Post: {self.title}"


class Test(Base):
    __tablename__ = "test"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    order = Column(Integer)
    group_id = Column(Integer, ForeignKey("group.id"), nullable=False)
    code = Column(String(255), nullable=True)

    group = relationship("Group", back_populates="tests")
    options = relationship("Option", back_populates="test")
    answers = relationship("TestAnswer", back_populates="test")
    entities = relationship("Entity", back_populates="test")

    def __repr__(self):
        return f"<Test(id={self.id}, order={self.order}, code={self.code})>"

    def __str__(self):
        return f"Test #{self.order}"


class TestAnswer(Base):
    __tablename__ = "test_answer"

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("test.id", ondelete="CASCADE"), nullable=False)
    option_id = Column(Integer, ForeignKey("option.id", ondelete="CASCADE"), nullable=False)

    test = relationship("Test", back_populates="answers")
    option = relationship("Option")

    def __repr__(self):
        return f"<TestAnswer(id={self.id}, test_id={self.test_id}, option_id={self.option_id})>"

    def __str__(self):
        return f"TestAnswer: test_id={self.test_id}, option_id={self.option_id}"


class Entity(Base):
    __tablename__ = "entity"

    id = Column(Integer, primary_key=True)
    question_id = Column(
        Integer, ForeignKey("test.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(Text, nullable=False)
    reward = Column(Integer, default=0)

    test = relationship("Test", back_populates="entities")
    user = relationship("User", back_populates="entities")

    def __repr__(self):
        return f"<Entity(id={self.id}, reward={self.reward})>"

    def __str__(self):
        return f"Entity: {self.content[:30]}..."


class Option(Base):
    __tablename__ = "option"

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("test.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    level = Column(Integer, nullable=False)

    test = relationship("Test", back_populates="options")

    def __repr__(self):
        return f"<Option(id={self.id}, test_id={self.test_id}, level={self.level})>"

    def __str__(self):
        return f"Option: {self.content[:30]}..."


class SituationalUserAnswer(Base):
    __tablename__ = "situational_user_answer"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("situational_question.id", ondelete="CASCADE"), nullable=False)
    answer_id = Column(Integer, ForeignKey("situational_answer.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"<SituationalUserAnswer(id={self.id}, user_id={self.user_id}, question_id={self.question_id}, answer_id={self.answer_id})>"

    def __str__(self):
        return f"SituationalUserAnswer: user_id={self.user_id}, question_id={self.question_id}, answer_id={self.answer_id}"
