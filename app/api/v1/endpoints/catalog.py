from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import structlog

from app.core.database import get_db
from app.schemas.catalog import StateResponse, ExamBodyResponse, ExamResponse, SyllabusResponse, TopicResponse
from app.services.catalog import CatalogService

logger = structlog.get_logger()

router = APIRouter()

@router.get("/states", response_model=List[StateResponse])
async def get_states(
    db: AsyncSession = Depends(get_db)
):
    """Get all states"""
    try:
        catalog_service = CatalogService(db)
        states = await catalog_service.get_states()
        return states
    except Exception as e:
        logger.error(f"Get states error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/exam-bodies", response_model=List[ExamBodyResponse])
async def get_exam_bodies(
    state_id: Optional[str] = Query(None),
    scope: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get exam bodies with optional filtering"""
    try:
        catalog_service = CatalogService(db)
        exam_bodies = await catalog_service.get_exam_bodies(state_id=state_id, scope=scope)
        return exam_bodies
    except Exception as e:
        logger.error(f"Get exam bodies error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/exams", response_model=List[ExamResponse])
async def get_exams(
    body_id: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get exams with optional filtering"""
    try:
        catalog_service = CatalogService(db)
        exams = await catalog_service.get_exams(body_id=body_id, level=level)
        return exams
    except Exception as e:
        logger.error(f"Get exams error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/exams/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get exam by ID"""
    try:
        catalog_service = CatalogService(db)
        exam = await catalog_service.get_exam_by_id(exam_id)
        
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )
        
        return exam
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get exam error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/exams/{exam_id}/syllabi", response_model=List[SyllabusResponse])
async def get_exam_syllabi(
    exam_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get syllabi for a specific exam"""
    try:
        catalog_service = CatalogService(db)
        syllabi = await catalog_service.get_exam_syllabi(exam_id)
        return syllabi
    except Exception as e:
        logger.error(f"Get exam syllabi error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/topics", response_model=List[TopicResponse])
async def get_topics(
    syllabus_id: Optional[str] = Query(None),
    exam_id: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get topics with optional filtering"""
    try:
        catalog_service = CatalogService(db)
        topics = await catalog_service.get_topics(
            syllabus_id=syllabus_id,
            exam_id=exam_id,
            difficulty=difficulty
        )
        return topics
    except Exception as e:
        logger.error(f"Get topics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
