from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import structlog

from app.core.database import get_db
from app.schemas.quiz import QuizResponse, QuizCreate, QuizUpdate
from app.core.dependencies import get_current_user, get_current_admin_user
from app.services.quiz import QuizService

logger = structlog.get_logger()

router = APIRouter()

@router.get("/", response_model=List[QuizResponse])
async def get_quizzes(
    exam_id: Optional[str] = Query(None),
    quiz_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get quizzes with filtering"""
    try:
        quiz_service = QuizService(db)
        quizzes = await quiz_service.get_quizzes(
            exam_id=exam_id,
            quiz_type=quiz_type,
            status=status,
            skip=skip,
            limit=limit
        )
        return quizzes
    except Exception as e:
        logger.error(f"Get quizzes error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get quiz by ID"""
    try:
        quiz_service = QuizService(db)
        quiz = await quiz_service.get_quiz_by_id(quiz_id)
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        return quiz
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get quiz error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def create_quiz(
    quiz_data: QuizCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new quiz"""
    try:
        quiz_service = QuizService(db)
        quiz = await quiz_service.create_quiz(quiz_data, current_user.id)
        
        logger.info(f"Quiz created successfully: {quiz.id}")
        return quiz
    except Exception as e:
        logger.error(f"Create quiz error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_quiz(
    quiz_id: str,
    quiz_data: QuizUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update quiz"""
    try:
        quiz_service = QuizService(db)
        quiz = await quiz_service.update_quiz(quiz_id, quiz_data, current_user.id)
        
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found"
            )
        
        logger.info(f"Quiz updated successfully: {quiz_id}")
        return quiz
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update quiz error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{quiz_id}")
async def delete_quiz(
    quiz_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete quiz"""
    try:
        quiz_service = QuizService(db)
        await quiz_service.delete_quiz(quiz_id, current_user.id)
        
        logger.info(f"Quiz deleted successfully: {quiz_id}")
        return {"message": "Quiz deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete quiz error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
