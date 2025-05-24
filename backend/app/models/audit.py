"""
Audit and Tracking Models
Database models for usage tracking, audit logs, and API keys
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class UsageTracking(Base):
    """Usage tracking model for analytics and billing"""

    __tablename__ = "usage_tracking"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Action information
    action_type = Column(String(50), nullable=False, index=True)  # document_generated, template_used, signature_sent
    resource_id = Column(UUID(as_uuid=True), nullable=True)  # Reference to document, template, etc.
    metadata = Column(JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="usage_tracking")

    def __repr__(self):
        return f"<UsageTracking(id={self.id}, user_id={self.user_id}, action={self.action_type})>"


class AuditLog(Base):
    """Audit log model for security and compliance"""

    __tablename__ = "audit_logs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)

    # Action information
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True)

    # Change tracking
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)

    # Request information
    ip_address = Column(INET, nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"


class APIKey(Base):
    """API key model for enterprise/partner integrations"""

    __tablename__ = "api_keys"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Key information
    key_name = Column(String(100), nullable=False)
    api_key_hash = Column(String(255), nullable=False, unique=True, index=True)
    permissions = Column(JSONB, nullable=False)  # Array of permitted actions

    # Rate limiting
    rate_limit = Column(Integer, default=1000, nullable=False)  # Requests per hour

    # Status and expiration
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="api_keys")

    def __repr__(self):
        return f"<APIKey(id={self.id}, name={self.key_name}, user_id={self.user_id})>"

    @property
    def is_expired(self) -> bool:
        """Check if API key is expired"""
        if not self.expires_at:
            return False

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)

        if self.expires_at.tzinfo is None:
            expires_at = self.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at = self.expires_at

        return now > expires_at

    @property
    def is_valid(self) -> bool:
        """Check if API key is valid (active and not expired)"""
        return self.is_active and not self.is_expired
