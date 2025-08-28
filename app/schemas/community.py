from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class ThreadResponse(BaseModel):
    id: uuid.UUID
    entity_type: str
    entity_id: Optional[uuid.UUID] = None
    title: Optional[str] = None
    created_by: uuid.UUID
    status: str
    is_pinned: bool
    view_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PostResponse(BaseModel):
    id: uuid.UUID
    thread_id: uuid.UUID
    body: str
    created_by: uuid.UUID
    parent_post_id: Optional[uuid.UUID] = None
    status: str
    is_solution: bool
    upvotes: int
    downvotes: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InstituteResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    branding_json: Dict[str, Any]
    owner_user_id: uuid.UUID
    is_active: bool
    subscription_plan_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class BatchResponse(BaseModel):
    id: uuid.UUID
    institute_id: uuid.UUID
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_students: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
