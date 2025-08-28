from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class StateResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    country_code: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ExamBodyResponse(BaseModel):
    id: uuid.UUID
    name: str
    state_id: Optional[uuid.UUID] = None
    scope: str
    website_url: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ExamResponse(BaseModel):
    id: uuid.UUID
    exam_body_id: uuid.UUID
    name: str
    level: str
    languages: List[str]
    description: Optional[str] = None
    exam_pattern: Optional[Dict[str, Any]] = None
    negative_marking: bool
    negative_mark_value: str
    total_marks: Optional[int] = None
    duration_minutes: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SyllabusResponse(BaseModel):
    id: uuid.UUID
    exam_id: uuid.UUID
    version: str
    title: str
    description: Optional[str] = None
    subjects: Optional[List[Dict[str, Any]]] = None
    total_topics: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TopicResponse(BaseModel):
    id: uuid.UUID
    syllabus_id: uuid.UUID
    parent_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    difficulty_band: str
    weightage: int
    estimated_questions: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
