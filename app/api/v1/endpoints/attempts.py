from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import structlog

from app.core.database import get_db
from app.schemas.attempt import AttemptResponse, AttemptCreate, AttemptAnswerCreate
from app.core.dependencies import get_current_user, get_current_admin_user
from app.services.attempt import AttemptService

logger = structlog.get_logger()

router = APIRouter()

@router.get("/", response_model=List[AttemptResponse])
async def get_attempts(
    quiz_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's attempts with filtering"""
    try:
        attempt_service = AttemptService(db)
        attempts = await attempt_service.get_user_attempts(
            user_id=current_user.id,
            quiz_id=quiz_id,
            status=status,
            skip=skip,
            limit=limit
        )
        return attempts
    except Exception as e:
        logger.error(f"Get attempts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{attempt_id}", response_model=AttemptResponse)
async def get_attempt(
    attempt_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get attempt by ID"""
    try:
        attempt_service = AttemptService(db)
        attempt = await attempt_service.get_attempt_by_id(attempt_id)
        
        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attempt not found"
            )
        
        # Check if user owns this attempt
        if str(attempt.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        return attempt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get attempt error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/", response_model=AttemptResponse, status_code=status.HTTP_201_CREATED)
async def create_attempt(
    attempt_data: AttemptCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a new quiz attempt"""
    try:
        attempt_service = AttemptService(db)
        attempt = await attempt_service.create_attempt(attempt_data, current_user.id)
        
        logger.info(f"Attempt started successfully: {attempt.id}")
        return attempt
    except Exception as e:
        logger.error(f"Create attempt error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/{attempt_id}/answer")
async def submit_answer(
    attempt_id: str,
    answer_data: AttemptAnswerCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit an answer for a question in an attempt"""
    try:
        attempt_service = AttemptService(db)
        await attempt_service.submit_answer(attempt_id, answer_data, current_user.id)
        
        logger.info(f"Answer submitted successfully for attempt: {attempt_id}")
        return {"message": "Answer submitted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit answer error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/{attempt_id}/finish", response_model=AttemptResponse)
async def finish_attempt(
    attempt_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Finish a quiz attempt and calculate results"""
    try:
        attempt_service = AttemptService(db)
        attempt = await attempt_service.finish_attempt(attempt_id, current_user.id)
        
        logger.info(f"Attempt finished successfully: {attempt_id}")
        return attempt
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Finish attempt error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{attempt_id}/results")
async def get_attempt_results(
    attempt_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed results for a completed attempt"""
    try:
        attempt_service = AttemptService(db)
        results = await attempt_service.get_attempt_results(attempt_id, current_user.id)
        
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get attempt results error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
