from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class AttemptResponse(BaseModel):
    id: uuid.UUID
    quiz_id: uuid.UUID
    user_id: uuid.UUID
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    score_raw: float
    score_percentage: float
    total_possible_score: float
    duration_seconds: int
    time_limit_seconds: Optional[int] = None
    breakdown: Dict[str, Any]
    meta_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AttemptCreate(BaseModel):
    quiz_id: uuid.UUID

class AttemptAnswerCreate(BaseModel):
    question_id: uuid.UUID
    selected_option_id: Optional[uuid.UUID] = None
    answer_text: Optional[str] = None
    time_spent_seconds: int = 0
