from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import structlog

from app.models.attempts import Attempt, AttemptAnswer
from app.models.quiz import Quiz
from app.schemas.attempt import AttemptCreate, AttemptAnswerCreate

logger = structlog.get_logger()

class AttemptService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_attempts(
        self, 
        user_id: str,
        quiz_id: Optional[str] = None, 
        status: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Attempt]:
        """Get user's attempts with filtering"""
        try:
            stmt = select(Attempt).options(selectinload(Attempt.answers)).where(Attempt.user_id == user_id)
            
            if quiz_id:
                stmt = stmt.where(Attempt.quiz_id == quiz_id)
            if status:
                stmt = stmt.where(Attempt.status == status)
            
            stmt = stmt.offset(skip).limit(limit).order_by(Attempt.created_at.desc())
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting user attempts: {e}")
            return []
    
    async def get_attempt_by_id(self, attempt_id: str) -> Optional[Attempt]:
        """Get attempt by ID with answers"""
        try:
            stmt = select(Attempt).options(selectinload(Attempt.answers)).where(Attempt.id == attempt_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting attempt by ID: {e}")
            return None
    
    async def create_attempt(self, attempt_data: AttemptCreate, user_id: str) -> Optional[Attempt]:
        """Start a new quiz attempt"""
        try:
            # Get quiz to calculate total possible score
            quiz_stmt = select(Quiz).where(Quiz.id == attempt_data.quiz_id)
            quiz_result = await self.db.execute(quiz_stmt)
            quiz = quiz_result.scalar_one_or_none()
            
            if not quiz:
                return None
            
            attempt = Attempt(
                quiz_id=attempt_data.quiz_id,
                user_id=user_id,
                status="in_progress",
                started_at=datetime.utcnow(),
                time_limit_seconds=quiz.time_limit_minutes * 60 if quiz.time_limit_minutes else None
            )
            
            self.db.add(attempt)
            await self.db.commit()
            await self.db.refresh(attempt)
            
            return attempt
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating attempt: {e}")
            return None
    
    async def submit_answer(self, attempt_id: str, answer_data: AttemptAnswerCreate, user_id: str) -> bool:
        """Submit an answer for a question in an attempt"""
        try:
            # Verify attempt belongs to user
            attempt = await self.get_attempt_by_id(attempt_id)
            if not attempt or str(attempt.user_id) != str(user_id):
                return False
            
            # Check if answer already exists
            existing_stmt = select(AttemptAnswer).where(
                AttemptAnswer.attempt_id == attempt_id,
                AttemptAnswer.question_id == answer_data.question_id
            )
            existing_result = await self.db.execute(existing_stmt)
            existing_answer = existing_result.scalar_one_or_none()
            
            if existing_answer:
                # Update existing answer
                stmt = update(AttemptAnswer).where(AttemptAnswer.id == existing_answer.id).values(
                    selected_option_id=answer_data.selected_option_id,
                    answer_text=answer_data.answer_text,
                    updated_at=datetime.utcnow()
                )
            else:
                # Create new answer
                answer = AttemptAnswer(
                    attempt_id=attempt_id,
                    question_id=answer_data.question_id,
                    selected_option_id=answer_data.selected_option_id,
                    answer_text=answer_data.answer_text
                )
                self.db.add(answer)
            
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error submitting answer: {e}")
            return False
    
    async def finish_attempt(self, attempt_id: str, user_id: str) -> Optional[Attempt]:
        """Finish a quiz attempt and calculate results"""
        try:
            # Verify attempt belongs to user
            attempt = await self.get_attempt_by_id(attempt_id)
            if not attempt or str(attempt.user_id) != str(user_id):
                return None
            
            # Calculate score and results
            # This is a simplified version - in real implementation, you'd calculate based on answers
            attempt.status = "completed"
            attempt.finished_at = datetime.utcnow()
            attempt.score_raw = 0.0  # Calculate based on correct answers
            attempt.score_percentage = 0.0  # Calculate percentage
            attempt.duration_seconds = int((attempt.finished_at - attempt.started_at).total_seconds())
            
            await self.db.commit()
            await self.db.refresh(attempt)
            
            return attempt
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error finishing attempt: {e}")
            return None
    
    async def get_attempt_results(self, attempt_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed results for a completed attempt"""
        try:
            # Verify attempt belongs to user
            attempt = await self.get_attempt_by_id(attempt_id)
            if not attempt or str(attempt.user_id) != str(user_id):
                return None
            
            # Get answers with question details
            answers_stmt = select(AttemptAnswer).where(AttemptAnswer.attempt_id == attempt_id)
            answers_result = await self.db.execute(answers_stmt)
            answers = answers_result.scalars().all()
            
            # Calculate detailed breakdown
            total_questions = len(answers)
            correct_answers = sum(1 for answer in answers if answer.is_correct)
            
            results = {
                "attempt_id": str(attempt.id),
                "quiz_id": str(attempt.quiz_id),
                "status": attempt.status,
                "score_raw": attempt.score_raw,
                "score_percentage": attempt.score_percentage,
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "incorrect_answers": total_questions - correct_answers,
                "duration_seconds": attempt.duration_seconds,
                "started_at": attempt.started_at,
                "finished_at": attempt.finished_at,
                "answers": [
                    {
                        "question_id": str(answer.question_id),
                        "selected_option_id": str(answer.selected_option_id) if answer.selected_option_id else None,
                        "is_correct": answer.is_correct,
                        "points_earned": answer.points_earned,
                        "time_spent_seconds": answer.time_spent_seconds
                    }
                    for answer in answers
                ]
            }
            
            return results
        except Exception as e:
            logger.error(f"Error getting attempt results: {e}")
            return None
