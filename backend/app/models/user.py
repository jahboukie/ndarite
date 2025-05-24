"""
User Model
Database model for user accounts and authentication
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class User(Base):
    """User account model"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Account settings
    role = Column(String(20), default="user", nullable=False)  # user, admin, legal_partner
    subscription_tier = Column(String(20), default="free", nullable=False)  # free, starter, professional, enterprise
    
    # External service IDs
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    
    # Account status
    email_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    generated_documents = relationship("GeneratedDocument", back_populates="user", cascade="all, delete-orphan")
    usage_tracking = relationship("UsageTracking", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_premium(self) -> bool:
        """Check if user has premium subscription"""
        return self.subscription_tier in ["starter", "professional", "enterprise"]
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == "admin"
    
    def can_create_documents(self, current_count: int) -> bool:
        """Check if user can create more documents based on tier limits"""
        from app.config import settings
        
        limits = {
            "free": settings.FREE_TIER_DOCUMENT_LIMIT,
            "starter": settings.STARTER_TIER_DOCUMENT_LIMIT,
            "professional": settings.PROFESSIONAL_TIER_DOCUMENT_LIMIT,
            "enterprise": settings.ENTERPRISE_TIER_DOCUMENT_LIMIT
        }
        
        limit = limits.get(self.subscription_tier, 0)
        
        # -1 means unlimited
        if limit == -1:
            return True
            
        return current_count < limit
