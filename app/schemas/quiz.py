from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class QuizResponse(BaseModel):
    id: uuid.UUID
    exam_id: uuid.UUID
    owner_user_id: uuid.UUID
    title: str
    description: Optional[str] = None
    quiz_type: str
    status: str
    config: Dict[str, Any]
    generated_from_template_id: Optional[uuid.UUID] = None
    total_questions: int
    time_limit_minutes: Optional[int] = None
    passing_score_percentage: float
    negative_marking: bool
    negative_mark_value: str
    is_randomized: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class QuizCreate(BaseModel):
    exam_id: uuid.UUID
    title: str
    description: Optional[str] = None
    quiz_type: str = "practice"
    config: Dict[str, Any] = Field(default_factory=dict)
    time_limit_minutes: Optional[int] = None
    passing_score_percentage: float = 60.0
    negative_marking: bool = False
    negative_mark_value: str = "0.25"
    is_randomized: bool = True

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    quiz_type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    time_limit_minutes: Optional[int] = None
    passing_score_percentage: Optional[float] = None
    negative_marking: Optional[bool] = None
    negative_mark_value: Optional[str] = None
    is_randomized: Optional[bool] = None
