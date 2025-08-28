from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import structlog

from app.models.payments import Wallet, Transaction, Plan, Subscription
from app.schemas.payment import WalletResponse, TransactionResponse, PlanResponse, SubscriptionResponse

logger = structlog.get_logger()

class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_wallet(self, user_id: str) -> Optional[Wallet]:
        """Get user's wallet"""
        try:
            stmt = select(Wallet).where(Wallet.user_id == user_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user wallet: {e}")
            return None
    
    async def get_user_transactions(
        self, 
        user_id: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """Get user's transaction history"""
        try:
            stmt = select(Transaction).join(Wallet).where(Wallet.user_id == user_id)
            stmt = stmt.offset(skip).limit(limit).order_by(Transaction.created_at.desc())
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting user transactions: {e}")
            return []
    
    async def get_plans(self, plan_type: Optional[str] = None) -> List[Plan]:
        """Get available subscription plans"""
        try:
            stmt = select(Plan).where(Plan.is_active == True)
            
            if plan_type:
                stmt = stmt.where(Plan.plan_type == plan_type)
            
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting plans: {e}")
            return []
    
    async def get_user_subscriptions(self, user_id: str) -> List[Subscription]:
        """Get user's subscriptions"""
        try:
            stmt = select(Subscription).where(Subscription.user_id == user_id)
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting user subscriptions: {e}")
            return []
    
    async def create_subscription(self, plan_id: str, user_id: str) -> Optional[Subscription]:
        """Subscribe to a plan"""
        try:
            # Get plan details
            plan_stmt = select(Plan).where(Plan.id == plan_id, Plan.is_active == True)
            plan_result = await self.db.execute(plan_stmt)
            plan = plan_result.scalar_one_or_none()
            
            if not plan:
                return None
            
            # Create subscription
            subscription = Subscription(
                user_id=user_id,
                plan_id=plan_id,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=plan.period_days),
                status="active"
            )
            
            self.db.add(subscription)
            await self.db.commit()
            await self.db.refresh(subscription)
            
            return subscription
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating subscription: {e}")
            return None
    
    async def charge_wallet(self, user_id: str, amount: int, payment_method: str) -> Optional[Transaction]:
        """Charge wallet with credits"""
        try:
            # Get or create wallet
            wallet = await self.get_user_wallet(user_id)
            if not wallet:
                wallet = Wallet(user_id=user_id)
                self.db.add(wallet)
                await self.db.commit()
                await self.db.refresh(wallet)
            
            # Create transaction
            transaction = Transaction(
                wallet_id=wallet.id,
                transaction_type="credit",
                amount=amount,
                status="completed",
                reason="Wallet recharge",
                payment_gateway=payment_method
            )
            
            self.db.add(transaction)
            
            # Update wallet balance
            wallet.balance_credits += amount
            wallet.total_earned_credits += amount
            
            await self.db.commit()
            await self.db.refresh(transaction)
            
            return transaction
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error charging wallet: {e}")
            return None
