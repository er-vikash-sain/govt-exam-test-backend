from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class QuestionOptionCreate(BaseModel):
    text: str
    is_correct: bool
    order_idx: int = 0
    explanation: Optional[str] = None

class QuestionOptionUpdate(BaseModel):
    text: Optional[str] = None
    is_correct: Optional[bool] = None
    order_idx: Optional[int] = None
    explanation: Optional[str] = None

class QuestionOptionResponse(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    text: str
    is_correct: bool
    order_idx: int
    explanation: Optional[str] = None
    meta_data: dict
    created_at: datetime
    
    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    id: uuid.UUID
    exam_id: uuid.UUID
    topic_id: uuid.UUID
    question_type: str
    stem: str
    explanation: Optional[str] = None
    difficulty: str
    source: str
    language: str
    status: str
    checksum: Optional[str] = None
    version: str
    meta_data: Dict[str, Any]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class QuestionCreate(BaseModel):
    exam_id: uuid.UUID
    topic_id: uuid.UUID
    question_type: str
    stem: str
    explanation: Optional[str] = None
    difficulty: str = "medium"
    source: str = "manual"
    language: str = "en"
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

class QuestionUpdate(BaseModel):
    stem: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: Optional[str] = None
    status: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
