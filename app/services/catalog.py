from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import structlog

from app.models.catalog import State, ExamBody, Exam, Syllabus, Topic

logger = structlog.get_logger()

class CatalogService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_states(self) -> List[State]:
        """Get all active states"""
        try:
            stmt = select(State).where(State.is_active == True)
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting states: {e}")
            return []
    
    async def get_exam_bodies(self, state_id: Optional[str] = None, scope: Optional[str] = None) -> List[ExamBody]:
        """Get exam bodies with optional filtering"""
        try:
            stmt = select(ExamBody).where(ExamBody.is_active == True)
            
            if state_id:
                stmt = stmt.where(ExamBody.state_id == state_id)
            if scope:
                stmt = stmt.where(ExamBody.scope == scope)
            
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting exam bodies: {e}")
            return []
    
    async def get_exams(self, body_id: Optional[str] = None, level: Optional[str] = None) -> List[Exam]:
        """Get exams with optional filtering"""
        try:
            stmt = select(Exam).where(Exam.is_active == True)
            
            if body_id:
                stmt = stmt.where(Exam.exam_body_id == body_id)
            if level:
                stmt = stmt.where(Exam.level == level)
            
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting exams: {e}")
            return []
    
    async def get_exam_by_id(self, exam_id: str) -> Optional[Exam]:
        """Get exam by ID"""
        try:
            stmt = select(Exam).where(Exam.id == exam_id, Exam.is_active == True)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting exam by ID: {e}")
            return None
    
    async def get_exam_syllabi(self, exam_id: str) -> List[Syllabus]:
        """Get syllabi for a specific exam"""
        try:
            stmt = select(Syllabus).where(Syllabus.exam_id == exam_id, Syllabus.is_active == True)
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting exam syllabi: {e}")
            return []
    
    async def get_topics(self, syllabus_id: Optional[str] = None, exam_id: Optional[str] = None, difficulty: Optional[str] = None) -> List[Topic]:
        """Get topics with optional filtering"""
        try:
            stmt = select(Topic).where(Topic.is_active == True)
            
            if syllabus_id:
                stmt = stmt.where(Topic.syllabus_id == syllabus_id)
            if exam_id:
                # Join with syllabus to filter by exam
                stmt = select(Topic).join(Syllabus).where(
                    Topic.syllabus_id == Syllabus.id,
                    Syllabus.exam_id == exam_id,
                    Topic.is_active == True
                )
            if difficulty:
                stmt = stmt.where(Topic.difficulty_band == difficulty)
            
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting topics: {e}")
            return []
