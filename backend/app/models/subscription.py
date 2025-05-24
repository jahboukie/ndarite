"""
Subscription Model
Database model for user subscription management
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Subscription(Base):
    """User subscription model"""
    
    __tablename__ = "subscriptions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Stripe integration
    stripe_subscription_id = Column(String(255), unique=True, nullable=True, index=True)
    
    # Subscription details
    plan_type = Column(String(20), nullable=False)  # starter, professional, enterprise
    status = Column(String(20), nullable=False)  # active, canceled, past_due, trialing
    
    # Billing periods
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Cancellation
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan={self.plan_type}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        return self.status in ["active", "trialing"]
    
    @property
    def is_trial(self) -> bool:
        """Check if subscription is in trial period"""
        return self.status == "trialing"
    
    @property
    def days_until_renewal(self) -> int:
        """Calculate days until next billing period"""
        from datetime import datetime, timezone
        
        if not self.current_period_end:
            return 0
            
        now = datetime.now(timezone.utc)
        if self.current_period_end.tzinfo is None:
            # Handle naive datetime
            from datetime import timezone
            period_end = self.current_period_end.replace(tzinfo=timezone.utc)
        else:
            period_end = self.current_period_end
            
        delta = period_end - now
        return max(0, delta.days)
