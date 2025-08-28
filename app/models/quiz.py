from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum, ForeignKey, Integer, JSON, Float
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base
import uuid

class QuizStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class QuizType(str, enum.Enum):
    PRACTICE = "practice"
    MOCK_TEST = "mock_test"
    ASSIGNMENT = "assignment"
    CUSTOM = "custom"

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False)
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    quiz_type = Column(ENUM(QuizType), default=QuizType.PRACTICE, nullable=False)
    status = Column(ENUM(QuizStatus), default=QuizStatus.DRAFT, nullable=False)
    config = Column(JSON, default={})  # Quiz configuration (timing, rules, etc.)
    generated_from_template_id = Column(UUID(as_uuid=True), ForeignKey("quiz_templates.id"), nullable=True)
    total_questions = Column(Integer, default=0)
    time_limit_minutes = Column(Integer, nullable=True)  # NULL means no time limit
    passing_score_percentage = Column(Float, default=60.0)
    negative_marking = Column(Boolean, default=False)
    negative_mark_value = Column(String(10), default="0.25")
    is_randomized = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    exam = relationship("Exam", back_populates="quizzes")
    owner = relationship("User")
    template = relationship("QuizTemplate")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="quiz")
    
    # Indexes for performance
    __table_args__ = (
        # Index on exam_id for filtering
        # Index on owner_user_id for filtering
        # Index on status for filtering
        # Index on quiz_type for filtering
    )

class QuizTemplate(Base):
    __tablename__ = "quiz_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    config = Column(JSON, nullable=False)  # Template configuration
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    exam = relationship("Exam")
    quizzes = relationship("Quiz", back_populates="template")
    
    # Indexes for performance
    __table_args__ = (
        # Index on exam_id for filtering
        # Index on is_active for filtering
    )

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    order_idx = Column(Integer, default=0, nullable=False)  # Question order in quiz
    points = Column(Float, default=1.0)  # Points for this question
    is_required = Column(Boolean, default=True)  # Whether question is mandatory
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    question = relationship("Question", back_populates="quiz_questions")
    
    # Indexes for performance
    __table_args__ = (
        # Index on quiz_id for filtering
        # Index on order_idx for ordering
        # Unique constraint on quiz_id and question_id
        # This will be handled in the application layer
    )
