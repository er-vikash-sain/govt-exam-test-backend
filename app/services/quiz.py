from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
import uuid
import structlog

from app.models.quiz import Quiz, QuizQuestion, QuizTemplate
from app.schemas.quiz import QuizCreate, QuizUpdate

logger = structlog.get_logger()

class QuizService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_quizzes(
        self, 
        exam_id: Optional[str] = None, 
        quiz_type: Optional[str] = None, 
        status: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Quiz]:
        """Get quizzes with filtering"""
        try:
            stmt = select(Quiz).options(selectinload(Quiz.questions))
            
            if exam_id:
                stmt = stmt.where(Quiz.exam_id == exam_id)
            if quiz_type:
                stmt = stmt.where(Quiz.quiz_type == quiz_type)
            if status:
                stmt = stmt.where(Quiz.status == status)
            
            stmt = stmt.offset(skip).limit(limit)
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting quizzes: {e}")
            return []
    
    async def get_quiz_by_id(self, quiz_id: str) -> Optional[Quiz]:
        """Get quiz by ID with questions"""
        try:
            stmt = select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.id == quiz_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting quiz by ID: {e}")
            return None
    
    async def create_quiz(self, quiz_data: QuizCreate, user_id: str) -> Optional[Quiz]:
        """Create a new quiz"""
        try:
            quiz = Quiz(
                exam_id=quiz_data.exam_id,
                owner_user_id=user_id,
                title=quiz_data.title,
                description=quiz_data.description,
                quiz_type=quiz_data.quiz_type,
                config=quiz_data.config or {},
                time_limit_minutes=quiz_data.time_limit_minutes,
                passing_score_percentage=quiz_data.passing_score_percentage,
                negative_marking=quiz_data.negative_marking,
                negative_mark_value=quiz_data.negative_mark_value,
                is_randomized=quiz_data.is_randomized
            )
            
            self.db.add(quiz)
            await self.db.commit()
            await self.db.refresh(quiz)
            
            return quiz
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating quiz: {e}")
            return None
    
    async def update_quiz(self, quiz_id: str, quiz_data: QuizUpdate, user_id: str) -> Optional[Quiz]:
        """Update quiz"""
        try:
            # Check if user owns the quiz
            quiz = await self.get_quiz_by_id(quiz_id)
            if not quiz or str(quiz.owner_user_id) != str(user_id):
                return None
            
            stmt = update(Quiz).where(Quiz.id == quiz_id).values(
                **quiz_data.dict(exclude_unset=True),
                updated_at=datetime.utcnow()
            )
            await self.db.execute(stmt)
            await self.db.commit()
            
            return await self.get_quiz_by_id(quiz_id)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating quiz: {e}")
            return None
    
    async def delete_quiz(self, quiz_id: str, user_id: str) -> bool:
        """Delete quiz"""
        try:
            # Check if user owns the quiz
            quiz = await self.get_quiz_by_id(quiz_id)
            if not quiz or str(quiz.owner_user_id) != str(user_id):
                return False
            
            stmt = update(Quiz).where(Quiz.id == quiz_id).values(
                status="archived",
                updated_at=datetime.utcnow()
            )
            await self.db.execute(stmt)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting quiz: {e}")
            return False
