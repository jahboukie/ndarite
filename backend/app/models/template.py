"""
Template Models
Database models for NDA templates and categories
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class TemplateCategory(Base):
    """Template category model"""
    
    __tablename__ = "template_categories"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Category information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    templates = relationship("NDATemplate", back_populates="category")
    
    def __repr__(self):
        return f"<TemplateCategory(id={self.id}, name={self.name}, slug={self.slug})>"


class NDATemplate(Base):
    """NDA template model"""
    
    __tablename__ = "nda_templates"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    category_id = Column(UUID(as_uuid=True), ForeignKey("template_categories.id"), nullable=True, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Template information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template_type = Column(String(20), nullable=False)  # bilateral, unilateral, multilateral
    jurisdiction = Column(String(100), default="United States", nullable=False)
    industry_focus = Column(String(100), nullable=True)
    complexity_level = Column(String(20), default="standard", nullable=False)  # basic, standard, advanced
    
    # Template content (JSON structure)
    template_content = Column(JSONB, nullable=False)
    legal_clauses = Column(JSONB, nullable=True)
    required_fields = Column(JSONB, nullable=False)
    optional_fields = Column(JSONB, nullable=True)
    
    # Access control
    tier_requirement = Column(String(20), default="starter", nullable=False)  # free, starter, professional, enterprise
    
    # Version control
    version = Column(Integer, default=1, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    category = relationship("TemplateCategory", back_populates="templates")
    generated_documents = relationship("GeneratedDocument", back_populates="template")
    
    def __repr__(self):
        return f"<NDATemplate(id={self.id}, name={self.name}, type={self.template_type})>"
    
    @property
    def is_bilateral(self) -> bool:
        """Check if template is bilateral"""
        return self.template_type == "bilateral"
    
    @property
    def is_unilateral(self) -> bool:
        """Check if template is unilateral"""
        return self.template_type == "unilateral"
    
    @property
    def is_multilateral(self) -> bool:
        """Check if template is multilateral"""
        return self.template_type == "multilateral"
    
    def can_access(self, user_tier: str) -> bool:
        """Check if user tier can access this template"""
        tier_hierarchy = {
            "free": 0,
            "starter": 1,
            "professional": 2,
            "enterprise": 3
        }
        
        user_level = tier_hierarchy.get(user_tier, 0)
        required_level = tier_hierarchy.get(self.tier_requirement, 1)
        
        return user_level >= required_level
