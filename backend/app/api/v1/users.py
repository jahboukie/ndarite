"""
User Management API Routes
User profile, settings, and account management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any
import logging

from app.database import get_db
from app.models.user import User
from app.models.document import GeneratedDocument
from app.models.audit import UsageTracking
from app.schemas.user import (
    UserResponse, UserUpdate, UsageStatsResponse, PasswordChange
)
from app.dependencies import get_current_user, rate_limiter
from app.utils.security import verify_password, get_password_hash
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile
    """
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """
    Update user profile information
    """
    try:
        # Update only provided fields
        update_data = profile_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        await db.commit()
        await db.refresh(current_user)
        
        logger.info(f"Profile updated for user: {current_user.email}")
        
        return current_user
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """
    Change user password
    """
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_user.password_hash = get_password_hash(password_data.new_password)
        await db.commit()
        
        logger.info(f"Password changed for user: {current_user.email}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.get("/usage-stats", response_model=UsageStatsResponse)
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user usage statistics and limits
    """
    try:
        # Get document counts
        documents_created_result = await db.execute(
            select(func.count(GeneratedDocument.id))
            .where(GeneratedDocument.user_id == current_user.id)
        )
        documents_created = documents_created_result.scalar() or 0
        
        documents_signed_result = await db.execute(
            select(func.count(GeneratedDocument.id))
            .where(
                GeneratedDocument.user_id == current_user.id,
                GeneratedDocument.status.in_(["signed", "completed"])
            )
        )
        documents_signed = documents_signed_result.scalar() or 0
        
        # Get template usage count
        templates_used_result = await db.execute(
            select(func.count(func.distinct(GeneratedDocument.template_id)))
            .where(GeneratedDocument.user_id == current_user.id)
        )
        templates_used = templates_used_result.scalar() or 0
        
        # Get API calls this month (if applicable)
        from datetime import datetime, timezone
        current_month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        api_calls_result = await db.execute(
            select(func.count(UsageTracking.id))
            .where(
                UsageTracking.user_id == current_user.id,
                UsageTracking.created_at >= current_month_start
            )
        )
        api_calls_this_month = api_calls_result.scalar() or 0
        
        # Calculate storage used (simplified - would need actual file sizes)
        storage_used_mb = documents_created * 0.5  # Estimate 0.5MB per document
        
        # Get tier limits
        tier_limits = {
            "documents_per_month": {
                "free": settings.FREE_TIER_DOCUMENT_LIMIT,
                "starter": settings.STARTER_TIER_DOCUMENT_LIMIT,
                "professional": settings.PROFESSIONAL_TIER_DOCUMENT_LIMIT,
                "enterprise": settings.ENTERPRISE_TIER_DOCUMENT_LIMIT
            }.get(current_user.subscription_tier, 0),
            "storage_gb": {
                "free": 1,
                "starter": 10,
                "professional": 50,
                "enterprise": -1  # Unlimited
            }.get(current_user.subscription_tier, 1),
            "api_calls_per_month": {
                "free": 0,
                "starter": 1000,
                "professional": 10000,
                "enterprise": -1  # Unlimited
            }.get(current_user.subscription_tier, 0)
        }
        
        return UsageStatsResponse(
            documents_created=documents_created,
            documents_signed=documents_signed,
            templates_used=templates_used,
            storage_used_mb=storage_used_mb,
            api_calls_this_month=api_calls_this_month,
            subscription_tier=current_user.subscription_tier,
            tier_limits=tier_limits
        )
        
    except Exception as e:
        logger.error(f"Usage stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage statistics"
        )


@router.delete("/account", status_code=status.HTTP_200_OK)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """
    Delete user account (soft delete - deactivate)
    """
    try:
        # Soft delete - deactivate account
        current_user.is_active = False
        await db.commit()
        
        logger.info(f"Account deactivated for user: {current_user.email}")
        
        return {"message": "Account has been deactivated"}
        
    except Exception as e:
        logger.error(f"Account deletion error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        )


@router.post("/reactivate", status_code=status.HTTP_200_OK)
async def reactivate_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reactivate deactivated account
    """
    try:
        current_user.is_active = True
        await db.commit()
        
        logger.info(f"Account reactivated for user: {current_user.email}")
        
        return {"message": "Account has been reactivated"}
        
    except Exception as e:
        logger.error(f"Account reactivation error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account reactivation failed"
        )
