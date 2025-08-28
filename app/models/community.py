from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base
import uuid

class ThreadStatus(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    MODERATED = "moderated"
    ARCHIVED = "archived"

class PostStatus(str, enum.Enum):
    ACTIVE = "active"
    MODERATED = "moderated"
    DELETED = "deleted"

class InstituteRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class Thread(Base):
    __tablename__ = "threads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False)  # question, quiz, general
    entity_id = Column(UUID(as_uuid=True), nullable=True)  # ID of related entity
    title = Column(String(200), nullable=True)  # Optional title for general threads
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(ENUM(ThreadStatus), default=ThreadStatus.ACTIVE, nullable=False)
    is_pinned = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    created_by_user = relationship("User", back_populates="threads")
    posts = relationship("Post", back_populates="thread", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        # Index on entity_type for filtering
        # Index on entity_id for filtering
        # Index on created_by for filtering
        # Index on status for filtering
        # Index on created_at for sorting
    )

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("threads.id", ondelete="CASCADE"), nullable=False)
    body = Column(Text, nullable=False)  # Post content
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    parent_post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=True)  # For replies
    status = Column(ENUM(PostStatus), default=PostStatus.ACTIVE, nullable=False)
    is_solution = Column(Boolean, default=False)  # Whether this post is marked as solution
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    thread = relationship("Thread", back_populates="posts")
    created_by_user = relationship("User", back_populates="posts")
    parent_post = relationship("Post", remote_side=[id], backref="replies")
    
    # Indexes for performance
    __table_args__ = (
        # Index on thread_id for filtering
        # Index on created_by for filtering
        # Index on parent_post_id for filtering
        # Index on status for filtering
        # Index on created_at for sorting
    )

class Institute(Base):
    __tablename__ = "institutes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    website_url = Column(String(500), nullable=True)
    logo_url = Column(String(500), nullable=True)
    branding_json = Column(JSON, default={})  # Custom branding configuration
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    subscription_plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User")
    subscription_plan = relationship("Plan")
    batches = relationship("Batch", back_populates="institute")
    
    # Indexes for performance
    __table_args__ = (
        # Index on owner_user_id for filtering
        # Index on is_active for filtering
        # Index on subscription_plan_id for filtering
    )

class Batch(Base):
    __tablename__ = "batches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institute_id = Column(UUID(as_uuid=True), ForeignKey("institutes.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    max_students = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    institute = relationship("Institute", back_populates="batches")
    enrollments = relationship("Enrollment", back_populates="batch")
    
    # Indexes for performance
    __table_args__ = (
        # Index on institute_id for filtering
        # Index on is_active for filtering
        # Index on start_date for filtering
    )

class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(ENUM(InstituteRole), default=InstituteRole.STUDENT, nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    meta_data = Column(JSON, default={})  # Additional enrollment metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    batch = relationship("Batch", back_populates="enrollments")
    user = relationship("User", back_populates="enrollments")
    
    # Indexes for performance
    __table_args__ = (
        # Index on batch_id for filtering
        # Index on user_id for filtering
        # Index on role for filtering
        # Index on is_active for filtering
        # Unique constraint on batch_id and user_id
        # This will be handled in the application layer
    )
