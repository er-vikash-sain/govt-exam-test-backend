from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import structlog

from app.core.database import get_db
from app.schemas.community import ThreadResponse, PostResponse, InstituteResponse, BatchResponse
from app.core.dependencies import get_current_user, get_current_admin_user
from app.services.community import CommunityService

logger = structlog.get_logger()

router = APIRouter()

@router.get("/threads", response_model=List[ThreadResponse])
async def get_threads(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get discussion threads"""
    try:
        community_service = CommunityService(db)
        threads = await community_service.get_threads(
            entity_type=entity_type,
            entity_id=entity_id,
            skip=skip,
            limit=limit
        )
        return threads
    except Exception as e:
        logger.error(f"Get threads error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/threads", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_thread(
    thread_data: dict,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new discussion thread"""
    try:
        community_service = CommunityService(db)
        thread = await community_service.create_thread(thread_data, current_user.id)
        
        logger.info(f"Thread created successfully: {thread.id}")
        return thread
    except Exception as e:
        logger.error(f"Create thread error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/threads/{thread_id}/posts", response_model=List[PostResponse])
async def get_thread_posts(
    thread_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get posts in a thread"""
    try:
        community_service = CommunityService(db)
        posts = await community_service.get_thread_posts(
            thread_id=thread_id,
            skip=skip,
            limit=limit
        )
        return posts
    except Exception as e:
        logger.error(f"Get thread posts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/threads/{thread_id}/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    thread_id: str,
    post_data: dict,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new post in a thread"""
    try:
        community_service = CommunityService(db)
        post = await community_service.create_post(thread_id, post_data, current_user.id)
        
        logger.info(f"Post created successfully: {post.id}")
        return post
    except Exception as e:
        logger.error(f"Create post error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/institutes", response_model=List[InstituteResponse])
async def get_institutes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Get institutes"""
    try:
        community_service = CommunityService(db)
        institutes = await community_service.get_institutes(skip=skip, limit=limit)
        return institutes
    except Exception as e:
        logger.error(f"Get institutes error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/institutes/{institute_id}", response_model=InstituteResponse)
async def get_institute(
    institute_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get institute by ID"""
    try:
        community_service = CommunityService(db)
        institute = await community_service.get_institute_by_id(institute_id)
        
        if not institute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institute not found"
            )
        
        return institute
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get institute error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/institutes/{institute_id}/batches", response_model=List[BatchResponse])
async def get_institute_batches(
    institute_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get batches for an institute"""
    try:
        community_service = CommunityService(db)
        batches = await community_service.get_institute_batches(institute_id)
        return batches
    except Exception as e:
        logger.error(f"Get institute batches error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
