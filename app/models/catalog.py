from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base
import uuid

class ExamScope(str, enum.Enum):
    NATIONAL = "national"
    STATE = "state"
    REGIONAL = "regional"
    INTERNATIONAL = "international"

class ExamLevel(str, enum.Enum):
    ENTRY_LEVEL = "entry_level"
    MID_LEVEL = "mid_level"
    SENIOR_LEVEL = "senior_level"
    EXPERT_LEVEL = "expert_level"

class TopicDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class State(Base):
    __tablename__ = "states"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    code = Column(String(10), unique=True, nullable=False, index=True)
    country_code = Column(String(3), default="IND")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    exam_bodies = relationship("ExamBody", back_populates="state")
    user_profiles = relationship("UserProfile", back_populates="state")

class ExamBody(Base):
    __tablename__ = "exam_bodies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    state_id = Column(UUID(as_uuid=True), ForeignKey("states.id"), nullable=True)
    scope = Column(ENUM(ExamScope), default=ExamScope.NATIONAL, nullable=False)
    website_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    state = relationship("State", back_populates="exam_bodies")
    exams = relationship("Exam", back_populates="exam_body")

class Exam(Base):
    __tablename__ = "exams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_body_id = Column(UUID(as_uuid=True), ForeignKey("exam_bodies.id"), nullable=False)
    name = Column(String(200), nullable=False)
    level = Column(ENUM(ExamLevel), default=ExamLevel.ENTRY_LEVEL, nullable=False)
    languages = Column(JSON, default=["en", "hi"])  # Array of language codes
    description = Column(Text, nullable=True)
    exam_pattern = Column(JSON, nullable=True)  # Exam structure and timing
    negative_marking = Column(Boolean, default=False)
    negative_mark_value = Column(String(10), default="0.25")  # e.g., "0.25", "0.5"
    total_marks = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    exam_body = relationship("ExamBody", back_populates="exams")
    syllabi = relationship("Syllabus", back_populates="exam")
    topics = relationship("Topic", back_populates="exam")
    quizzes = relationship("Quiz", back_populates="exam")
    questions = relationship("Question", back_populates="exam")

class Syllabus(Base):
    __tablename__ = "syllabi"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False)
    version = Column(String(20), nullable=False, default="1.0")
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    subjects = Column(JSON, nullable=True)  # Array of subject objects
    total_topics = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    exam = relationship("Exam", back_populates="syllabi")
    topics = relationship("Topic", back_populates="syllabus")
    
    # Composite unique constraint
    __table_args__ = (
        # Ensure unique version per exam
        # This will be handled in the application layer
    )

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    syllabus_id = Column(UUID(as_uuid=True), ForeignKey("syllabi.id"), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=True)  # For hierarchical topics
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    difficulty_band = Column(ENUM(TopicDifficulty), default=TopicDifficulty.MEDIUM, nullable=False)
    weightage = Column(Integer, default=1)  # Relative importance in exam
    estimated_questions = Column(Integer, default=0)  # Expected number of questions
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    syllabus = relationship("Syllabus", back_populates="topics")
    parent = relationship("Topic", remote_side=[id], backref="children")
    questions = relationship("Question", back_populates="topic")
    
    # Indexes for performance
    __table_args__ = (
        # Index on parent_id for hierarchical queries
        # Index on difficulty_band for filtering
    )
