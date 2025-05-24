"""
User Schemas
Pydantic models for user-related requests and responses
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    company_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        from app.utils.security import is_strong_password
        
        is_valid, issues = is_strong_password(v)
        if not is_valid:
            raise ValueError(f"Password requirements not met: {'; '.join(issues)}")
        
        return v
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format"""
        return v.lower().strip()
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Validate name fields"""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip().title()
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v:
            import re
            # Remove all non-digit characters
            digits_only = re.sub(r'\D', '', v)
            if len(digits_only) < 10:
                raise ValueError("Phone number must contain at least 10 digits")
        return v


class UserUpdate(BaseModel):
    """Schema for user profile updates"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    company_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Validate name fields"""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Name cannot be empty")
            return v.strip().title()
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v:
            import re
            digits_only = re.sub(r'\D', '', v)
            if len(digits_only) < 10:
                raise ValueError("Phone number must contain at least 10 digits")
        return v


class UserResponse(UserBase):
    """Schema for user data responses"""
    id: UUID
    role: str
    subscription_tier: str
    email_verified: bool
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str = Field(..., min_length=1)
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format"""
        return v.lower().strip()


class TokenResponse(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class PasswordReset(BaseModel):
    """Schema for password reset"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        from app.utils.security import is_strong_password
        
        is_valid, issues = is_strong_password(v)
        if not is_valid:
            raise ValueError(f"Password requirements not met: {'; '.join(issues)}")
        
        return v


class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        from app.utils.security import is_strong_password
        
        is_valid, issues = is_strong_password(v)
        if not is_valid:
            raise ValueError(f"Password requirements not met: {'; '.join(issues)}")
        
        return v


class EmailVerification(BaseModel):
    """Schema for email verification"""
    token: str


class ForgotPassword(BaseModel):
    """Schema for forgot password request"""
    email: EmailStr
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format"""
        return v.lower().strip()


class UsageStatsResponse(BaseModel):
    """Schema for user usage statistics"""
    documents_created: int
    documents_signed: int
    templates_used: int
    storage_used_mb: float
    api_calls_this_month: int
    subscription_tier: str
    tier_limits: dict
    
    class Config:
        from_attributes = True
