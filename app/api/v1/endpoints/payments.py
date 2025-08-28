from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import structlog

from app.core.database import get_db
from app.schemas.payment import WalletResponse, TransactionResponse, PlanResponse, SubscriptionResponse
from app.core.dependencies import get_current_user, get_current_admin_user
from app.services.payment import PaymentService

logger = structlog.get_logger()

router = APIRouter()

@router.get("/wallet", response_model=WalletResponse)
async def get_wallet(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's wallet"""
    try:
        payment_service = PaymentService(db)
        wallet = await payment_service.get_user_wallet(current_user.id)
        
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
        
        return wallet
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get wallet error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's transaction history"""
    try:
        payment_service = PaymentService(db)
        transactions = await payment_service.get_user_transactions(
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        return transactions
    except Exception as e:
        logger.error(f"Get transactions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/plans", response_model=List[PlanResponse])
async def get_plans(
    plan_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get available subscription plans"""
    try:
        payment_service = PaymentService(db)
        plans = await payment_service.get_plans(plan_type=plan_type)
        return plans
    except Exception as e:
        logger.error(f"Get plans error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's subscriptions"""
    try:
        payment_service = PaymentService(db)
        subscriptions = await payment_service.get_user_subscriptions(current_user.id)
        return subscriptions
    except Exception as e:
        logger.error(f"Get subscriptions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/subscribe")
async def subscribe_to_plan(
    plan_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Subscribe to a plan"""
    try:
        payment_service = PaymentService(db)
        subscription = await payment_service.create_subscription(plan_id, current_user.id)
        
        logger.info(f"Subscription created successfully: {subscription.id}")
        return {"subscription_id": str(subscription.id), "status": subscription.status}
    except Exception as e:
        logger.error(f"Subscribe to plan error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/wallet/charge")
async def charge_wallet(
    amount: int,
    payment_method: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Charge wallet with credits"""
    try:
        payment_service = PaymentService(db)
        transaction = await payment_service.charge_wallet(
            user_id=current_user.id,
            amount=amount,
            payment_method=payment_method
        )
        
        logger.info(f"Wallet charged successfully: {transaction.id}")
        return {"transaction_id": str(transaction.id), "status": transaction.status}
    except Exception as e:
        logger.error(f"Charge wallet error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
