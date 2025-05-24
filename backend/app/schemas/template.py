"""
Template Schemas
Pydantic models for template-related requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime


class TemplateBase(BaseModel):
    """Base template schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    template_type: str = Field(..., regex="^(bilateral|unilateral|multilateral)$")
    jurisdiction: str = Field(default="United States", max_length=100)
    industry_focus: Optional[str] = Field(None, max_length=100)
    complexity_level: str = Field(default="standard", regex="^(basic|standard|advanced)$")


class TemplateCreate(TemplateBase):
    """Schema for creating new templates"""
    category_id: UUID
    template_content: Dict[str, Any]
    legal_clauses: Optional[Dict[str, Any]] = None
    required_fields: Dict[str, Any]
    optional_fields: Optional[Dict[str, Any]] = None
    tier_requirement: str = Field(default="starter", regex="^(free|starter|professional|enterprise)$")
    
    @validator('template_content')
    def validate_template_content(cls, v):
        """Validate template content structure"""
        required_keys = ['sections', 'variables', 'formatting']
        for key in required_keys:
            if key not in v:
                raise ValueError(f"Template content must include '{key}' section")
        return v
    
    @validator('required_fields')
    def validate_required_fields(cls, v):
        """Validate required fields structure"""
        if not isinstance(v, dict):
            raise ValueError("Required fields must be a dictionary")
        
        for field_name, field_config in v.items():
            if not isinstance(field_config, dict):
                raise ValueError(f"Field config for '{field_name}' must be a dictionary")
            
            if 'type' not in field_config:
                raise ValueError(f"Field '{field_name}' must specify a type")
                
        return v


class TemplateUpdate(BaseModel):
    """Schema for updating templates"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    template_type: Optional[str] = Field(None, regex="^(bilateral|unilateral|multilateral)$")
    jurisdiction: Optional[str] = Field(None, max_length=100)
    industry_focus: Optional[str] = Field(None, max_length=100)
    complexity_level: Optional[str] = Field(None, regex="^(basic|standard|advanced)$")
    template_content: Optional[Dict[str, Any]] = None
    legal_clauses: Optional[Dict[str, Any]] = None
    required_fields: Optional[Dict[str, Any]] = None
    optional_fields: Optional[Dict[str, Any]] = None
    tier_requirement: Optional[str] = Field(None, regex="^(free|starter|professional|enterprise)$")
    is_active: Optional[bool] = None


class TemplateResponse(TemplateBase):
    """Schema for template responses"""
    id: UUID
    category_id: Optional[UUID]
    tier_requirement: str
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TemplateDetailResponse(TemplateResponse):
    """Schema for detailed template responses"""
    template_content: Dict[str, Any]
    legal_clauses: Optional[Dict[str, Any]]
    required_fields: Dict[str, Any]
    optional_fields: Optional[Dict[str, Any]]


class TemplateListResponse(BaseModel):
    """Schema for template list responses"""
    templates: List[TemplateResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    slug: str = Field(..., min_length=1, max_length=100, regex="^[a-z0-9-]+$")
    sort_order: int = Field(default=0, ge=0)


class CategoryCreate(CategoryBase):
    """Schema for creating categories"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating categories"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    slug: Optional[str] = Field(None, min_length=1, max_length=100, regex="^[a-z0-9-]+$")
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema for category responses"""
    id: UUID
    is_active: bool
    created_at: datetime
    template_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class TemplateSearchRequest(BaseModel):
    """Schema for template search requests"""
    query: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = None
    template_type: Optional[str] = Field(None, regex="^(bilateral|unilateral|multilateral)$")
    industry: Optional[str] = None
    complexity: Optional[str] = Field(None, regex="^(basic|standard|advanced)$")
    jurisdiction: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="name", regex="^(name|created_at|updated_at|complexity_level)$")
    sort_order: str = Field(default="asc", regex="^(asc|desc)$")


class TemplatePreviewRequest(BaseModel):
    """Schema for template preview requests"""
    template_id: UUID
    sample_data: Optional[Dict[str, Any]] = None
