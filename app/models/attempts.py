from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum, ForeignKey, Integer, JSON, Float
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base
import uuid

class AttemptStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    TIMED_OUT = "timed_out"

class Attempt(Base):
    __tablename__ = "attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(ENUM(AttemptStatus), default=AttemptStatus.IN_PROGRESS, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    score_raw = Column(Float, default=0.0)  # Raw score (points earned)
    score_percentage = Column(Float, default=0.0)  # Percentage score
    total_possible_score = Column(Float, default=0.0)  # Total possible points
    duration_seconds = Column(Integer, default=0)  # Time taken in seconds
    time_limit_seconds = Column(Integer, nullable=True)  # Time limit if any
    breakdown = Column(JSON, default={})  # Detailed breakdown (topic-wise, difficulty-wise)
    meta_data = Column(JSON, default={})  # Additional attempt metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User", back_populates="attempts")
    answers = relationship("AttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        # Index on quiz_id for filtering
        # Index on user_id for filtering
        # Index on status for filtering
        # Index on started_at for sorting
    )

class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    selected_option_id = Column(UUID(as_uuid=True), ForeignKey("question_options.id"), nullable=True)
    is_correct = Column(Boolean, nullable=True)  # NULL if not answered
    points_earned = Column(Float, default=0.0)  # Points earned for this question
    time_spent_seconds = Column(Integer, default=0)  # Time spent on this question
    answer_text = Column(Text, nullable=True)  # For text/numeric answers
    meta_data = Column(JSON, default={})  # Additional answer metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    attempt = relationship("Attempt", back_populates="answers")
    question = relationship("Question", back_populates="attempt_answers")
    selected_option = relationship("QuestionOption", back_populates="attempt_answers")
    
    # Indexes for performance
    __table_args__ = (
        # Index on attempt_id for filtering
        # Index on question_id for filtering
        # Index on is_correct for filtering
        # Unique constraint on attempt_id and question_id
        # This will be handled in the application layer
    )
