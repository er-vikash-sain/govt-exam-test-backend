from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import structlog

from app.models.community import Thread, Post, Institute, Batch
from app.schemas.community import ThreadResponse, PostResponse, InstituteResponse, BatchResponse

logger = structlog.get_logger()

class CommunityService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_threads(
        self, 
        entity_type: Optional[str] = None, 
        entity_id: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Thread]:
        """Get discussion threads"""
        try:
            stmt = select(Thread).where(Thread.status == "active")
            
            if entity_type:
                stmt = stmt.where(Thread.entity_type == entity_type)
            if entity_id:
                stmt = stmt.where(Thread.entity_id == entity_id)
            
            stmt = stmt.offset(skip).limit(limit).order_by(Thread.created_at.desc())
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting threads: {e}")
            return []
    
    async def create_thread(self, thread_data: Dict[str, Any], user_id: str) -> Optional[Thread]:
        """Create a new discussion thread"""
        try:
            thread = Thread(
                entity_type=thread_data.get("entity_type", "general"),
                entity_id=thread_data.get("entity_id"),
                title=thread_data.get("title"),
                created_by=user_id
            )
            
            self.db.add(thread)
            await self.db.commit()
            await self.db.refresh(thread)
            
            return thread
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating thread: {e}")
            return None
    
    async def get_thread_posts(
        self, 
        thread_id: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Post]:
        """Get posts in a thread"""
        try:
            stmt = select(Post).where(
                Post.thread_id == thread_id,
                Post.status == "active"
            )
            stmt = stmt.offset(skip).limit(limit).order_by(Post.created_at.asc())
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting thread posts: {e}")
            return []
    
    async def create_post(self, thread_id: str, post_data: Dict[str, Any], user_id: str) -> Optional[Post]:
        """Create a new post in a thread"""
        try:
            post = Post(
                thread_id=thread_id,
                body=post_data.get("body", ""),
                created_by=user_id,
                parent_post_id=post_data.get("parent_post_id")
            )
            
            self.db.add(post)
            await self.db.commit()
            await self.db.refresh(post)
            
            return post
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating post: {e}")
            return None
    
    async def get_institutes(self, skip: int = 0, limit: int = 100) -> List[Institute]:
        """Get institutes"""
        try:
            stmt = select(Institute).where(Institute.is_active == True)
            stmt = stmt.offset(skip).limit(limit)
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting institutes: {e}")
            return []
    
    async def get_institute_by_id(self, institute_id: str) -> Optional[Institute]:
        """Get institute by ID"""
        try:
            stmt = select(Institute).where(Institute.id == institute_id, Institute.is_active == True)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting institute by ID: {e}")
            return None
    
    async def get_institute_batches(self, institute_id: str) -> List[Batch]:
        """Get batches for an institute"""
        try:
            stmt = select(Batch).where(Batch.institute_id == institute_id, Batch.is_active == True)
            result = await self.db.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting institute batches: {e}")
            return []
