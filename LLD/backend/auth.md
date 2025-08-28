# Backend LLD - Authentication & Authorization
**Component:** Authentication System
**Technology:** JWT, FastAPI, Redis, PostgreSQL
**Version:** 1.0

---

## 1. Authentication Overview

The authentication system provides secure, scalable user authentication and authorization using JWT tokens, role-based access control (RBAC), and secure session management.

---

## 2. Authentication Architecture

### 2.1 System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client        │    │   FastAPI       │    │   Database      │
│   (Frontend)    │◄──►│   Auth Module   │◄──►│   (Users)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   JWT Token     │    │   Redis         │    │   Audit Logs    │
│   Storage       │    │   (Sessions)    │    │   (Security)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2.2 Authentication Flow
1. **User Registration** → Email verification
2. **User Login** → JWT token generation
3. **Token Validation** → Request authorization
4. **Token Refresh** → Extended sessions
5. **User Logout** → Token invalidation

---

## 3. JWT Token Structure

### 3.1 Access Token
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_uuid",
    "email": "user@example.com",
    "role": "student",
    "permissions": ["read:quiz", "write:attempt"],
    "iat": 1640995200,
    "exp": 1640998800,
    "jti": "token_uuid"
  },
  "signature": "HMACSHA256(...)"
}
```

### 3.2 Refresh Token
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_uuid",
    "type": "refresh",
    "iat": 1640995200,
    "exp": 1640998800,
    "jti": "refresh_token_uuid"
  },
  "signature": "HMACSHA256(...)"
}
```

---

## 4. User Roles & Permissions

### 4.1 Role Hierarchy
```
Super Admin
├── Full system access
├── User management
├── System configuration
└── Audit logs

Content Manager
├── Content creation
├── Content approval
├── User management
└── Analytics access

Editor/Reviewer
├── Content review
├── Content editing
├── Quality checks
└── Basic analytics

Institute Admin
├── Batch management
├── User assignment
├── Custom branding
└── Cohort analytics

Student
├── Take quizzes
├── View results
├── Study materials
└── Profile management
```

### 4.2 Permission Matrix
| Permission | Super Admin | Content Manager | Editor | Institute Admin | Student |
|------------|-------------|-----------------|---------|-----------------|---------|
| `user:read` | ✅ | ✅ | ❌ | ✅ | ❌ |
| `user:write` | ✅ | ✅ | ❌ | ✅ | ❌ |
| `content:read` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `content:write` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `content:approve` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `analytics:read` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `system:config` | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 5. Security Implementation

### 5.1 Password Security
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 5.2 JWT Security
- **Secret Key**: 256-bit random key stored in environment
- **Algorithm**: HS256 for symmetric signing
- **Token Expiry**: Access token (1 hour), Refresh token (7 days)
- **Token Rotation**: New refresh token on each use

### 5.3 Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Rate limits per endpoint
@limiter.limit("5/minute")  # Login attempts
@limiter.limit("100/hour")  # General API
@limiter.limit("1000/day")  # Daily limits
```

---

## 6. API Endpoints

### 6.1 Authentication Endpoints
```python
@router.post("/register")
async def register_user(user_data: UserRegister):
    """User registration with email verification"""
    pass

@router.post("/login")
async def login_user(credentials: UserLogin):
    """User login with JWT token generation"""
    pass

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    pass

@router.post("/logout")
async def logout_user():
    """User logout with token invalidation"""
    pass

@router.post("/verify-email")
async def verify_email(token: str):
    """Email verification"""
    pass

@router.post("/forgot-password")
async def forgot_password(email: str):
    """Password reset request"""
    pass

@router.post("/reset-password")
async def reset_password(token: str, new_password: str):
    """Password reset"""
    pass
```

### 6.2 User Management Endpoints
```python
@router.get("/me")
async def get_current_user(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    pass

@router.patch("/me")
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update user profile"""
    pass

@router.get("/users")
@require_permissions(["user:read"])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get users list (admin only)"""
    pass
```

---

## 7. Middleware & Dependencies

### 7.1 Authentication Middleware
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Extract and validate JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user
```

### 7.2 Permission Middleware
```python
def require_permissions(required_permissions: List[str]):
    """Decorator for permission-based access control"""
    def permission_checker(current_user: User = Depends(get_current_user)):
        user_permissions = get_user_permissions(current_user)
        for permission in required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
        return current_user
    return permission_checker
```

---

## 8. Session Management

### 8.1 Redis Session Storage
```python
import redis
from typing import Optional

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

class SessionManager:
    def __init__(self):
        self.redis = redis_client
    
    async def create_session(self, user_id: str, token_data: dict) -> str:
        """Create new user session"""
        session_id = f"session:{user_id}:{uuid.uuid4()}"
        await self.redis.setex(
            session_id,
            SESSION_EXPIRY,
            json.dumps(token_data)
        )
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        data = await self.redis.get(session_id)
        return json.loads(data) if data else None
    
    async def invalidate_session(self, session_id: str):
        """Invalidate user session"""
        await self.redis.delete(session_id)
```

### 8.2 Session Security
- **Session expiry**: Configurable TTL
- **Concurrent sessions**: Limit per user
- **Device tracking**: IP and user agent logging
- **Session invalidation**: On password change

---

## 9. Multi-Factor Authentication

### 9.1 MFA Implementation
```python
import pyotp

class MFAService:
    def __init__(self):
        self.secret_length = 32
    
    def generate_secret(self) -> str:
        """Generate TOTP secret"""
        return pyotp.random_base32(self.secret_length)
    
    def generate_qr_code(self, secret: str, email: str) -> str:
        """Generate QR code for authenticator app"""
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            email,
            issuer_name="Exam Platform"
        )
        return provisioning_uri
    
    def verify_code(self, secret: str, code: str) -> bool:
        """Verify TOTP code"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code)
```

### 9.2 MFA Flow
1. **Enable MFA**: Generate secret and QR code
2. **Verify Setup**: User scans QR and enters code
3. **Login Flow**: Username/password + MFA code
4. **Recovery Codes**: Backup access method

---

## 10. Audit & Logging

### 10.1 Security Events
```python
from enum import Enum
from datetime import datetime

class SecurityEventType(Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

class SecurityLogger:
    async def log_event(
        self,
        event_type: SecurityEventType,
        user_id: str,
        details: dict,
        ip_address: str,
        user_agent: str
    ):
        """Log security event"""
        event = SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow()
        )
        await self.save_event(event)
```

### 10.2 Audit Trail
- **User actions**: All critical operations logged
- **Access attempts**: Failed login attempts tracked
- **Permission changes**: Role and permission modifications
- **Data access**: Sensitive data access logging

---

## 11. Password Policies

### 11.1 Password Requirements
```python
import re

class PasswordValidator:
    def __init__(self):
        self.min_length = 8
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digits = True
        self.require_special = True
        self.max_length = 128
    
    def validate(self, password: str) -> tuple[bool, List[str]]:
        """Validate password strength"""
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters")
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain uppercase letter")
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain lowercase letter")
        
        if self.require_digits and not re.search(r'\d', password):
            errors.append("Password must contain digit")
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain special character")
        
        return len(errors) == 0, errors
```

### 11.2 Password History
- **Last 5 passwords**: Prevent reuse
- **Expiry policy**: 90 days
- **Complexity requirements**: Enforced validation
- **Breach checking**: Against known breached passwords

---

## 12. Security Headers

### 12.1 Security Middleware
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

---

## 13. Next Steps

1. **Implement JWT token** generation and validation
2. **Create user roles** and permission system
3. **Set up Redis** for session management
4. **Implement MFA** for enhanced security
5. **Add audit logging** for security events

---

*This authentication system provides secure, scalable user management with role-based access control and comprehensive security features.*
