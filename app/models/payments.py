from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum, ForeignKey, Integer, JSON, Float, Numeric
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base
import uuid

class TransactionType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"

class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentGateway(str, enum.Enum):
    RAZORPAY = "razorpay"
    STRIPE = "stripe"
    PAYTM = "paytm"
    INTERNAL = "internal"

class PlanType(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    INSTITUTE = "institute"

class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    balance_credits = Column(Integer, default=0, nullable=False)  # Available credits
    total_earned_credits = Column(Integer, default=0, nullable=False)  # Total credits ever earned
    total_spent_credits = Column(Integer, default=0, nullable=False)  # Total credits ever spent
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="wallet")
    transactions = relationship("Transaction", back_populates="wallet")
    
    # Indexes for performance
    __table_args__ = (
        # Index on user_id for filtering
    )

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False)
    transaction_type = Column(ENUM(TransactionType), nullable=False)
    amount = Column(Integer, nullable=False)  # Amount in credits
    status = Column(ENUM(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    reason = Column(String(200), nullable=False)  # Transaction reason
    gateway_ref = Column(String(200), nullable=True)  # External gateway reference
    payment_gateway = Column(ENUM(PaymentGateway), nullable=True)
    meta_data = Column(JSON, default={})  # Additional transaction metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    
    # Indexes for performance
    __table_args__ = (
        # Index on wallet_id for filtering
        # Index on transaction_type for filtering
        # Index on status for filtering
        # Index on created_at for sorting
    )

class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    plan_type = Column(ENUM(PlanType), nullable=False)
    price_inr = Column(Numeric(10, 2), nullable=False)  # Price in Indian Rupees
    price_usd = Column(Numeric(10, 2), nullable=True)  # Price in USD
    period_days = Column(Integer, nullable=False)  # Plan validity in days
    credits_per_month = Column(Integer, default=0)  # Credits included per month
    features = Column(JSON, default={})  # Plan features and limitations
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")
    
    # Indexes for performance
    __table_args__ = (
        # Index on plan_type for filtering
        # Index on is_active for filtering
        # Index on price_inr for filtering
    )

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
    status = Column(String(50), default="active", nullable=False)  # active, cancelled, expired
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    auto_renew = Column(Boolean, default=True)
    payment_gateway = Column(ENUM(PaymentGateway), nullable=True)
    gateway_subscription_id = Column(String(200), nullable=True)
    meta_data = Column(JSON, default={})  # Additional subscription metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    
    # Indexes for performance
    __table_args__ = (
        # Index on user_id for filtering
        # Index on plan_id for filtering
        # Index on status for filtering
        # Index on end_date for filtering
    )
