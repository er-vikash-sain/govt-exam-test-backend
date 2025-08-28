from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
import asyncpg
import redis.asyncio as redis
from typing import AsyncGenerator
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Database URL for async operations
ASYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create sync session factory for migrations
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine.sync_engine if hasattr(engine, 'sync_engine') else None,
)

# Base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

# Redis connection
redis_client: redis.Redis = None

async def get_redis_client() -> redis.Redis:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database connection and create tables"""
    try:
        # Test database connection
        async with engine.begin() as conn:
            from sqlalchemy import text
            await conn.run_sync(lambda sync_conn: sync_conn.execute(text("SELECT 1")))
        
        logger.info("Database connection established successfully")
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def close_db():
    """Close database connections"""
    try:
        await engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

async def init_redis():
    """Initialize Redis connection"""
    try:
        global redis_client
        redis_client = await get_redis_client()
        await redis_client.ping()
        logger.info("Redis connection established successfully")
    except Exception as e:
        logger.error(f"Redis initialization failed: {e}")
        raise

async def close_redis():
    """Close Redis connection"""
    try:
        global redis_client
        if redis_client:
            await redis_client.close()
            logger.info("Redis connection closed successfully")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {e}")

# Health check functions
async def check_db_health() -> bool:
    """Check if database is healthy"""
    try:
        async with engine.begin() as conn:
            from sqlalchemy import text
            await conn.run_sync(lambda sync_conn: sync_conn.execute(text("SELECT 1")))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

async def check_redis_health() -> bool:
    """Check if Redis is healthy"""
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False
