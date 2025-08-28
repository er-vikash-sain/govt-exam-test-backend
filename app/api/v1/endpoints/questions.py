from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import structlog

from app.core.database import get_db
from app.schemas.question import QuestionResponse, QuestionCreate, QuestionUpdate
from app.core.dependencies import get_current_user, get_current_admin_user
from app.services.question import QuestionService

logger = structlog.get_logger()

router = APIRouter()

@router.get("/", response_model=List[QuestionResponse])
async def get_questions(
    exam_id: Optional[str] = Query(None),
    topic_id: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get questions with filtering"""
    try:
        question_service = QuestionService(db)
        questions = await question_service.get_questions(
            exam_id=exam_id,
            topic_id=topic_id,
            difficulty=difficulty,
            status=status,
            skip=skip,
            limit=limit
        )
        return questions
    except Exception as e:
        logger.error(f"Get questions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get question by ID"""
    try:
        question_service = QuestionService(db)
        question = await question_service.get_question_by_id(question_id)
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        return question
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get question error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new question (admin/editor only)"""
    try:
        # Check permissions
        if current_user.role not in ["admin", "editor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        question_service = QuestionService(db)
        question = await question_service.create_question(question_data, current_user.id)
        
        logger.info(f"Question created successfully: {question.id}")
        return question
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create question error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: str,
    question_data: QuestionUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update question (admin/editor only)"""
    try:
        # Check permissions
        if current_user.role not in ["admin", "editor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        question_service = QuestionService(db)
        question = await question_service.update_question(question_id, question_data)
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
        
        logger.info(f"Question updated successfully: {question_id}")
        return question
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update question error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{question_id}")
async def delete_question(
    question_id: str,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete question (admin only)"""
    try:
        # Check permissions
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        question_service = QuestionService(db)
        await question_service.delete_question(question_id)
        
        logger.info(f"Question deleted successfully: {question_id}")
        return {"message": "Question deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete question error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
