from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum, ForeignKey, Integer, JSON, Float
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base
import uuid

class QuestionType(str, enum.Enum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    NUMERIC = "numeric"
    ASSERTION_REASON = "assertion_reason"
    PASSAGE_BASED = "passage_based"

class QuestionStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"

class QuestionSource(str, enum.Enum):
    AI_GENERATED = "ai_generated"
    MANUAL = "manual"
    IMPORTED = "imported"

class QuestionDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=False)
    question_type = Column(ENUM(QuestionType), default=QuestionType.SINGLE_CHOICE, nullable=False)
    stem = Column(Text, nullable=False)  # Main question text
    explanation = Column(Text, nullable=True)  # Detailed explanation
    difficulty = Column(ENUM(QuestionDifficulty), default=QuestionDifficulty.MEDIUM, nullable=False)
    source = Column(ENUM(QuestionSource), default=QuestionSource.MANUAL, nullable=False)
    language = Column(String(10), default="en", nullable=False)
    status = Column(ENUM(QuestionStatus), default=QuestionStatus.DRAFT, nullable=False)
    checksum = Column(String(64), nullable=True, index=True)  # For duplicate detection
    version = Column(String(20), default="1.0", nullable=False)
    meta_data = Column(JSON, default={})  # Additional question metadata
    tags = Column(JSON, default=[])  # Array of tags
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    exam = relationship("Exam", back_populates="questions")
    topic = relationship("Topic", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    quiz_questions = relationship("QuizQuestion", back_populates="question")
    attempt_answers = relationship("AttemptAnswer", back_populates="question")
    
    # Indexes for performance
    __table_args__ = (
        # Index on exam_id, topic_id for filtering
        # Index on difficulty for filtering
        # Index on status for filtering
        # Index on language for filtering
    )

class QuestionOption(Base):
    __tablename__ = "question_options"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)  # Option text
    is_correct = Column(Boolean, default=False, nullable=False)
    order_idx = Column(Integer, default=0, nullable=False)  # For option ordering
    explanation = Column(Text, nullable=True)  # Why this option is correct/incorrect
    meta_data = Column(JSON, default={})  # Additional option metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    question = relationship("Question", back_populates="options")
    attempt_answers = relationship("AttemptAnswer", back_populates="selected_option")
    
    # Indexes for performance
    __table_args__ = (
        # Index on question_id for filtering
        # Index on is_correct for filtering
    )

class QuestionBank(Base):
    __tablename__ = "question_banks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False)
    topic_ids = Column(JSON, default=[])  # Array of topic IDs
    difficulty_distribution = Column(JSON, default={"easy": 0.3, "medium": 0.5, "hard": 0.2})
    total_questions = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    exam = relationship("Exam")
    
    # Indexes for performance
    __table_args__ = (
        # Index on exam_id for filtering
        # Index on is_active for filtering
    )
