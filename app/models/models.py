from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # Store hashed password
    is_premium = Column(Boolean, default=False)
    reward = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    posts = relationship("Post", back_populates="author")
    test_answers = relationship("TestAnswer", back_populates="user")
    entities = relationship("Entity", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', is_premium={self.is_premium})>"

    def __str__(self):
        return f"User {self.email}"


class Group(Base):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    sub_groups = relationship("SubGroup", back_populates="group")
    situational_questions = relationship("SituationalQuestion", back_populates="group")

    def __repr__(self):
        return f"<Group(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return f"Group: {self.name}"


class SubGroup(Base):
    __tablename__ = 'sub_group'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('group.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    group = relationship("Group", back_populates="sub_groups")

    def __repr__(self):
        return f"<SubGroup(id={self.id}, name='{self.name}', group_id={self.group_id})>"

    def __str__(self):
        return f"SubGroup: {self.name}"


class SituationalQuestion(Base):
    __tablename__ = 'situational_question'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('group.id', ondelete='CASCADE'), nullable=False)
    content = Column(Text, nullable=False)
    level = Column(Integer)

    group = relationship("Group", back_populates="situational_questions")

    __table_args__ = (
        CheckConstraint('level IN (1, 2, 3)', name='check_level_values'),
    )

    def __repr__(self):
        return f"<SituationalQuestion(id={self.id}, level={self.level})>"

    def __str__(self):
        return f"Question Level {self.level}"


class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    audio = Column(Text)
    image = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    author_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Relationship
    author = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}')>"

    def __str__(self):
        return f"Post: {self.title}"


class Test(Base):
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    order = Column(Integer)

    answers = relationship("TestAnswer", back_populates="test")
    entities = relationship("Entity", back_populates="test")

    def __repr__(self):
        return f"<Test(id={self.id}, order={self.order})>"

    def __str__(self):
        return f"Test #{self.order}"


class TestAnswer(Base):
    __tablename__ = 'test_answer'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('test.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    level = Column(Integer)

    test = relationship("Test", back_populates="answers")
    user = relationship("User", back_populates="test_answers")

    __table_args__ = (
        CheckConstraint('level >= 1 AND level <= 3', name='check_answer_level_range'),
    )

    def __repr__(self):
        return f"<TestAnswer(id={self.id}, level={self.level})>"

    def __str__(self):
        return f"Answer Level {self.level}"


class Entity(Base):
    __tablename__ = 'entity'

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('test.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = Column(Text, nullable=False)
    reward = Column(Integer, default=0)

    test = relationship("Test", back_populates="entities")
    user = relationship("User", back_populates="entities")

    def __repr__(self):
        return f"<Entity(id={self.id}, reward={self.reward})>"

    def __str__(self):
        return f"Entity: {self.content[:30]}..."
