from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Union
import uuid
import structlog

from app.core.config import settings
from app.models.user import User, UserProfile
from app.schemas.auth import UserCreate

logger = structlog.get_logger()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create an access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create a refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return user_id
        except JWTError:
            return None
    
    def verify_refresh_token(self, token: str) -> Optional[str]:
        """Verify and decode a refresh token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return user_id
        except JWTError:
            return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password"""
        try:
            # Get user with profile
            stmt = select(User).where(User.email == email)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            if not self.verify_password(password, user.password_hash):
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    async def register_user(self, user_data: UserCreate) -> User:
        """Register a new user"""
        try:
            # Check if user already exists
            stmt = select(User).where(User.email == user_data.email)
            result = await self.db.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                raise ValueError("User with this email already exists")
            
            # Create user
            hashed_password = self.get_password_hash(user_data.password)
            user = User(
                email=user_data.email,
                password_hash=hashed_password,
                phone=user_data.phone,
                locale=user_data.locale,
                timezone=user_data.timezone
            )
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            # Create user profile
            profile = UserProfile(
                user_id=user.id,
                first_name=user_data.first_name,
                last_name=user_data.last_name
            )
            
            self.db.add(profile)
            await self.db.commit()
            
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"User registration error: {e}")
            raise
    
    async def logout_user(self, token: str) -> bool:
        """Logout a user by invalidating their token"""
        try:
            # In a real implementation, you might want to add the token to a blacklist
            # For now, we'll just return success
            return True
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    async def send_password_reset_email(self, email: str) -> bool:
        """Send password reset email"""
        try:
            # Check if user exists
            stmt = select(User).where(User.email == email)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                # Don't reveal if user exists or not
                return True
            
            # Generate reset token
            reset_token = self.create_access_token(
                data={"sub": str(user.id), "type": "password_reset"},
                expires_delta=timedelta(hours=1)
            )
            
            # In a real implementation, send email here
            logger.info(f"Password reset token generated for user: {user.id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Send password reset email error: {e}")
            return False
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using reset token"""
        try:
            # Verify token
            user_id = self.verify_token(token)
            if not user_id:
                raise ValueError("Invalid or expired reset token")
            
            # Get user
            stmt = select(User).where(User.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError("User not found")
            
            # Update password
            hashed_password = self.get_password_hash(new_password)
            user.password_hash = hashed_password
            user.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(f"Password reset successfully for user: {user.id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Password reset error: {e}")
            raise
    
    @staticmethod
    async def get_current_user(token: str, db: AsyncSession) -> User:
        """Get current authenticated user from token"""
        try:
            # This is a placeholder - in real implementation, you'd inject the service
            # For now, we'll create a temporary service instance
            auth_service = AuthService(db)
            user_id = auth_service.verify_token(token)
            
            if user_id is None:
                raise ValueError("Invalid token")
            
            # Get user
            stmt = select(User).where(User.id == user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user is None:
                raise ValueError("User not found")
            
            return user
            
        except Exception as e:
            logger.error(f"Get current user error: {e}")
            raise ValueError("Invalid token")
