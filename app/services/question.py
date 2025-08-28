from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
import uuid
import structlog

from app.models.content import Question, QuestionOption
from app.schemas.question import QuestionCreate, QuestionUpdate

logger = structlog.get_logger()

class QuestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_questions(
        self, 
        exam_id: Optional[str] = None, 
        topic_id: Optional[str] = None, 
        difficulty: Optional[str] = None, 
        status: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Question]:
        """Get questions with filtering"""
        try:
            stmt = select(Question).options(selectinload(Question.options))
            
            if exam_id:
                stmt = stmt.where(Question.exam_id == exam_id)
            if topic_id:
                stmt = stmt.where(Question.topic_id == topic_id)
            if difficulty:
                stmt = stmt.where(Question.difficulty == difficulty)
            if status:
                stmt = stmt.where(Question.status == status)
            
            stmt = stmt.offset(skip).limit(limit)
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting questions: {e}")
            return []
    
    async def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """Get question by ID with options"""
        try:
            stmt = select(Question).options(selectinload(Question.options)).where(Question.id == question_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting question by ID: {e}")
            return None
    
    async def create_question(self, question_data: QuestionCreate, user_id: str) -> Optional[Question]:
        """Create a new question"""
        try:
            question = Question(
                exam_id=question_data.exam_id,
                topic_id=question_data.topic_id,
                question_type=question_data.question_type,
                stem=question_data.stem,
                explanation=question_data.explanation,
                difficulty=question_data.difficulty,
                language=question_data.language,
                metadata=question_data.metadata or {},
                tags=question_data.tags or []
            )
            
            self.db.add(question)
            await self.db.commit()
            await self.db.refresh(question)
            
            # Add options if provided
            if question_data.options:
                for option_data in question_data.options:
                    option = QuestionOption(
                        question_id=question.id,
                        text=option_data.text,
                        is_correct=option_data.is_correct,
                        order_idx=option_data.order_idx,
                        explanation=option_data.explanation
                    )
                    self.db.add(option)
                
                await self.db.commit()
                await self.db.refresh(question)
            
            return question
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating question: {e}")
            return None
    
    async def update_question(self, question_id: str, question_data: QuestionUpdate) -> Optional[Question]:
        """Update question"""
        try:
            stmt = update(Question).where(Question.id == question_id).values(
                **question_data.dict(exclude_unset=True),
                updated_at=datetime.utcnow()
            )
            await self.db.execute(stmt)
            await self.db.commit()
            
            return await self.get_question_by_id(question_id)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating question: {e}")
            return None
    
    async def delete_question(self, question_id: str) -> bool:
        """Delete question (soft delete by setting status to deprecated)"""
        try:
            stmt = update(Question).where(Question.id == question_id).values(
                status="deprecated",
                updated_at=datetime.utcnow()
            )
            await self.db.execute(stmt)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting question: {e}")
            return False
