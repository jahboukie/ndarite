"""
Template Management API Routes
NDA template browsing, selection, and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging

from app.database import get_db
from app.models.user import User
from app.models.template import NDATemplate, TemplateCategory
from app.schemas.template import (
    TemplateResponse, TemplateDetailResponse, TemplateListResponse,
    CategoryResponse, TemplateSearchRequest, TemplateCreate, TemplateUpdate
)
from app.dependencies import get_current_user, get_current_admin, get_optional_user, rate_limiter
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=TemplateListResponse)
async def get_templates(
    category: Optional[str] = Query(None, description="Filter by category slug"),
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    industry: Optional[str] = Query(None, description="Filter by industry focus"),
    complexity: Optional[str] = Query(None, description="Filter by complexity level"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("name", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of available NDA templates with filtering and pagination
    """
    try:
        # Build query
        query = select(NDATemplate).where(NDATemplate.is_active == True)
        
        # Apply filters
        if category:
            category_subquery = select(TemplateCategory.id).where(
                TemplateCategory.slug == category,
                TemplateCategory.is_active == True
            )
            query = query.where(NDATemplate.category_id.in_(category_subquery))
        
        if template_type:
            query = query.where(NDATemplate.template_type == template_type)
        
        if industry:
            query = query.where(NDATemplate.industry_focus == industry)
        
        if complexity:
            query = query.where(NDATemplate.complexity_level == complexity)
        
        if jurisdiction:
            query = query.where(NDATemplate.jurisdiction == jurisdiction)
        
        # Filter by user's subscription tier
        if current_user:
            user_tier = current_user.subscription_tier
        else:
            user_tier = "free"
        
        # Only show templates user can access
        tier_hierarchy = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
        user_level = tier_hierarchy.get(user_tier, 0)
        
        accessible_tiers = [tier for tier, level in tier_hierarchy.items() if level <= user_level]
        query = query.where(NDATemplate.tier_requirement.in_(accessible_tiers))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting
        if sort_by == "name":
            order_column = NDATemplate.name
        elif sort_by == "created_at":
            order_column = NDATemplate.created_at
        elif sort_by == "updated_at":
            order_column = NDATemplate.updated_at
        elif sort_by == "complexity_level":
            order_column = NDATemplate.complexity_level
        else:
            order_column = NDATemplate.name
        
        if sort_order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        # Execute query
        result = await db.execute(query)
        templates = result.scalars().all()
        
        # Calculate pagination info
        has_next = (offset + per_page) < total
        has_prev = page > 1
        
        return TemplateListResponse(
            templates=[TemplateResponse.from_orm(template) for template in templates],
            total=total,
            page=page,
            per_page=per_page,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logger.error(f"Get templates error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve templates"
        )


@router.get("/{template_id}", response_model=TemplateDetailResponse)
async def get_template(
    template_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific template
    """
    try:
        # Get template
        result = await db.execute(
            select(NDATemplate)
            .where(NDATemplate.id == template_id, NDATemplate.is_active == True)
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Check if user can access this template
        if current_user:
            user_tier = current_user.subscription_tier
        else:
            user_tier = "free"
        
        if not template.can_access(user_tier):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Template requires '{template.tier_requirement}' subscription or higher"
            )
        
        return TemplateDetailResponse.from_orm(template)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get template error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve template"
        )


@router.get("/categories/", response_model=List[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """
    Get all template categories
    """
    try:
        # Get categories with template counts
        result = await db.execute(
            select(
                TemplateCategory,
                func.count(NDATemplate.id).label("template_count")
            )
            .outerjoin(NDATemplate, and_(
                TemplateCategory.id == NDATemplate.category_id,
                NDATemplate.is_active == True
            ))
            .where(TemplateCategory.is_active == True)
            .group_by(TemplateCategory.id)
            .order_by(TemplateCategory.sort_order, TemplateCategory.name)
        )
        
        categories_with_counts = result.all()
        
        categories = []
        for category, template_count in categories_with_counts:
            category_response = CategoryResponse.from_orm(category)
            category_response.template_count = template_count
            categories.append(category_response)
        
        return categories
        
    except Exception as e:
        logger.error(f"Get categories error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve categories"
        )


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """
    Create a new NDA template (admin only)
    """
    try:
        # Verify category exists
        category_result = await db.execute(
            select(TemplateCategory)
            .where(TemplateCategory.id == template_data.category_id)
        )
        category = category_result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )
        
        # Create template
        new_template = NDATemplate(
            **template_data.dict(exclude={"category_id"}),
            category_id=template_data.category_id,
            created_by=current_user.id
        )
        
        db.add(new_template)
        await db.commit()
        await db.refresh(new_template)
        
        logger.info(f"Template created: {new_template.name} by {current_user.email}")
        
        return TemplateResponse.from_orm(new_template)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create template error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Template creation failed"
        )


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template_data: TemplateUpdate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """
    Update an existing template (admin only)
    """
    try:
        # Get template
        result = await db.execute(
            select(NDATemplate).where(NDATemplate.id == template_id)
        )
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Update template
        update_data = template_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)
        
        # Increment version if content changed
        if any(field in update_data for field in ['template_content', 'legal_clauses', 'required_fields']):
            template.version += 1
        
        await db.commit()
        await db.refresh(template)
        
        logger.info(f"Template updated: {template.name} by {current_user.email}")
        
        return TemplateResponse.from_orm(template)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update template error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Template update failed"
        )
