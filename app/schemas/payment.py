from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from decimal import Decimal

class WalletResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    balance_credits: int
    total_earned_credits: int
    total_spent_credits: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TransactionResponse(BaseModel):
    id: uuid.UUID
    wallet_id: uuid.UUID
    transaction_type: str
    amount: int
    status: str
    reason: str
    gateway_ref: Optional[str] = None
    payment_gateway: Optional[str] = None
    meta_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PlanResponse(BaseModel):
    id: uuid.UUID
    name: str
    plan_type: str
    price_inr: Decimal
    price_usd: Optional[Decimal] = None
    period_days: int
    credits_per_month: int
    features: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    plan_id: uuid.UUID
    status: str
    start_date: datetime
    end_date: datetime
    auto_renew: bool
    payment_gateway: Optional[str] = None
    gateway_subscription_id: Optional[str] = None
    meta_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
