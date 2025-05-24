"""
Security Utilities
Password hashing, JWT token management, and security functions
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import hashlib

from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            return None
            
        # Check expiration
        exp = payload.get("exp")
        if exp is None:
            return None
            
        if datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            return None
            
        return payload
        
    except JWTError:
        return None


def generate_reset_token() -> str:
    """Generate secure password reset token"""
    return secrets.token_urlsafe(32)


def generate_verification_token() -> str:
    """Generate email verification token"""
    return secrets.token_urlsafe(32)


def generate_api_key() -> str:
    """Generate API key"""
    return f"nda_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """Verify API key against hash"""
    return hash_api_key(api_key) == hashed_key


def generate_document_id() -> str:
    """Generate unique document identifier"""
    return f"doc_{secrets.token_urlsafe(16)}"


def is_strong_password(password: str) -> tuple[bool, list[str]]:
    """
    Check if password meets security requirements
    Returns (is_valid, list_of_issues)
    """
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        issues.append("Password must contain at least one number")
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        issues.append("Password must contain at least one special character")
    
    return len(issues) == 0, issues


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    import re
    
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\s-.]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    
    return filename.strip('-.')


def generate_secure_filename(original_filename: str, user_id: str) -> str:
    """Generate secure filename with user ID and timestamp"""
    import os
    from datetime import datetime
    
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create secure filename
    secure_name = f"{user_id}_{timestamp}_{secrets.token_urlsafe(8)}{ext}"
    
    return secure_name
