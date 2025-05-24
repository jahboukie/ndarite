"""
FastAPI Dependencies
Common dependencies for authentication, database access, and authorization
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.utils.security import verify_token
from app.config import settings

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = verify_token(credentials.credentials, "access")
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (additional check for active status)
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify admin privileges
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_current_premium_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify premium subscription
    """
    if not current_user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Premium subscription required"
        )
    return current_user


async def verify_subscription_tier(
    required_tier: str,
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verify user has required subscription tier
    """
    tier_hierarchy = {
        "free": 0,
        "starter": 1,
        "professional": 2,
        "enterprise": 3
    }
    
    user_level = tier_hierarchy.get(current_user.subscription_tier, 0)
    required_level = tier_hierarchy.get(required_tier, 1)
    
    if user_level < required_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Subscription tier '{required_tier}' or higher required"
        )
    
    return current_user


def require_tier(tier: str):
    """
    Dependency factory for requiring specific subscription tier
    """
    async def _verify_tier(current_user: User = Depends(get_current_user)) -> User:
        return await verify_subscription_tier(tier, current_user)
    
    return _verify_tier


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None
    Useful for endpoints that work for both authenticated and anonymous users
    """
    authorization = request.headers.get("Authorization")
    
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.split(" ")[1]
    
    try:
        payload = verify_token(token, "access")
        if payload is None:
            return None
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user and user.is_active:
            return user
            
    except Exception:
        pass
    
    return None


class RateLimiter:
    """
    Simple rate limiter dependency
    """
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    async def __call__(self, request: Request):
        import time
        
        # Get client IP
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self.requests = {
            ip: timestamps for ip, timestamps in self.requests.items()
            if any(t > current_time - self.window_seconds for t in timestamps)
        }
        
        # Get current requests for this IP
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Filter recent requests
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if t > current_time - self.window_seconds
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)


# Create rate limiter instances
rate_limiter = RateLimiter(max_requests=settings.RATE_LIMIT_PER_MINUTE, window_seconds=60)
strict_rate_limiter = RateLimiter(max_requests=10, window_seconds=60)  # For sensitive endpoints
