from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class AIJobResponse(BaseModel):
    id: uuid.UUID
    job_type: str
    status: str
    provider: str
    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    token_usage: Optional[Dict[str, Any]] = None
    cost_usd: float
    processing_time_seconds: Optional[float] = None
    priority: int
    retry_count: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AIContentResponse(BaseModel):
    id: uuid.UUID
    ai_job_id: uuid.UUID
    content_type: str
    content: Dict[str, Any]
    checksum: Optional[str] = None
    quality_score: Optional[float] = None
    meta_data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AIJobCreate(BaseModel):
    job_type: str
    provider: str = "openai"
    payload: Dict[str, Any]
    priority: int = 1

class AIJobUpdate(BaseModel):
    status: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    token_usage: Optional[Dict[str, Any]] = None
    cost_usd: Optional[float] = None
    processing_time_seconds: Optional[float] = None
    retry_count: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
