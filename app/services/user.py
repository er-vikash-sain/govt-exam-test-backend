from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
import uuid
import structlog

from app.models.user import User, UserProfile
from app.schemas.user import UserUpdate, UserProfileUpdate

logger = structlog.get_logger()

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID with profile"""
        try:
            stmt = select(User).options(selectinload(User.profile)).where(User.id == user_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    async def get_users(self, skip: int = 0, limit: int = 100, role: Optional[str] = None, status: Optional[str] = None) -> List[User]:
        """Get users with filtering"""
        try:
            stmt = select(User).options(selectinload(User.profile))
            
            if role:
                stmt = stmt.where(User.role == role)
            if status:
                stmt = stmt.where(User.status == status)
            
            stmt = stmt.offset(skip).limit(limit)
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        try:
            stmt = update(User).where(User.id == user_id).values(
                **user_data.dict(exclude_unset=True),
                updated_at=datetime.utcnow()
            )
            await self.db.execute(stmt)
            await self.db.commit()
            
            return await self.get_user_by_id(user_id)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, profile_data: UserProfileUpdate) -> Optional[UserProfile]:
        """Update user profile"""
        try:
            stmt = update(UserProfile).where(UserProfile.user_id == user_id).values(
                **profile_data.dict(exclude_unset=True),
                updated_at=datetime.utcnow()
            )
            await self.db.execute(stmt)
            await self.db.commit()
            
            # Get updated profile
            stmt = select(UserProfile).where(UserProfile.user_id == user_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user profile: {e}")
            return None
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        try:
            stmt = select(UserProfile).where(UserProfile.user_id == user_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            stmt = update(User).where(User.id == user_id).values(
                last_login=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            await self.db.execute(stmt)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating last login: {e}")
            return False
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user (soft delete by setting status to inactive)"""
        try:
            stmt = update(User).where(User.id == user_id).values(
                status="inactive",
                updated_at=datetime.utcnow()
            )
            await self.db.execute(stmt)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting user: {e}")
            return False
