from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum, ForeignKey, Integer, JSON, Float
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base
import uuid

class AIJobType(str, enum.Enum):
    GENERATE_QUESTIONS = "generate_questions"
    GENERATE_EXPLANATIONS = "generate_explanations"
    GENERATE_QUIZ = "generate_quiz"
    CONTENT_MODERATION = "content_moderation"
    DIFFICULTY_ANALYSIS = "difficulty_analysis"

class AIJobStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AIProvider(str, enum.Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGING_FACE = "hugging_face"
    LOCAL = "local"

class AIJob(Base):
    __tablename__ = "ai_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(ENUM(AIJobType), nullable=False)
    status = Column(ENUM(AIJobStatus), default=AIJobStatus.PENDING, nullable=False)
    provider = Column(ENUM(AIProvider), default=AIProvider.OPENAI, nullable=False)
    payload = Column(JSON, nullable=False)  # Job parameters and configuration
    result = Column(JSON, nullable=True)  # Job result/output
    error_message = Column(Text, nullable=True)  # Error details if failed
    token_usage = Column(JSON, nullable=True)  # Token usage statistics
    cost_usd = Column(Float, default=0.0)  # Cost in USD
    processing_time_seconds = Column(Float, nullable=True)  # Time taken to process
    priority = Column(Integer, default=1)  # Job priority (1=highest)
    retry_count = Column(Integer, default=0)  # Number of retry attempts
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    content = relationship("AIContent", back_populates="ai_job", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        # Index on job_type for filtering
        # Index on status for filtering
        # Index on provider for filtering
        # Index on priority for job queue ordering
        # Index on created_at for sorting
    )

class AIContent(Base):
    __tablename__ = "ai_content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_job_id = Column(UUID(as_uuid=True), ForeignKey("ai_jobs.id", ondelete="CASCADE"), nullable=False)
    content_type = Column(String(50), nullable=False)  # questions, explanations, etc.
    content = Column(JSON, nullable=False)  # Generated content
    checksum = Column(String(64), nullable=True, index=True)  # For duplicate detection
    quality_score = Column(Float, nullable=True)  # AI-generated quality score
    meta_data = Column(JSON, default={})  # Additional content metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ai_job = relationship("AIJob", back_populates="content")
    
    # Indexes for performance
    __table_args__ = (
        # Index on ai_job_id for filtering
        # Index on content_type for filtering
        # Index on quality_score for filtering
    )
