"""
Subscription Management API Routes
Subscription plans, billing, and tier management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
import logging

from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.dependencies import get_current_user, rate_limiter
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/plans")
async def get_subscription_plans():
    """
    Get available subscription plans and pricing
    """
    plans = {
        "free": {
            "name": "Free",
            "price": 0,
            "currency": "USD",
            "billing_period": "month",
            "features": {
                "documents_per_month": settings.FREE_TIER_DOCUMENT_LIMIT,
                "templates_access": "Basic templates only",
                "storage_gb": 1,
                "support": "Community support",
                "api_access": False,
                "custom_branding": False,
                "priority_support": False
            },
            "limitations": [
                f"Limited to {settings.FREE_TIER_DOCUMENT_LIMIT} documents per month",
                "Basic templates only",
                "1GB storage limit",
                "Community support only"
            ]
        },
        "starter": {
            "name": "Starter",
            "price": 29,
            "currency": "USD",
            "billing_period": "month",
            "features": {
                "documents_per_month": settings.STARTER_TIER_DOCUMENT_LIMIT,
                "templates_access": "All standard templates",
                "storage_gb": 10,
                "support": "Email support",
                "api_access": True,
                "custom_branding": False,
                "priority_support": False,
                "electronic_signatures": True
            },
            "popular": True
        },
        "professional": {
            "name": "Professional",
            "price": 99,
            "currency": "USD",
            "billing_period": "month",
            "features": {
                "documents_per_month": settings.PROFESSIONAL_TIER_DOCUMENT_LIMIT,
                "templates_access": "All templates including advanced",
                "storage_gb": 50,
                "support": "Priority email support",
                "api_access": True,
                "custom_branding": True,
                "priority_support": True,
                "electronic_signatures": True,
                "bulk_operations": True,
                "analytics": True
            }
        },
        "enterprise": {
            "name": "Enterprise",
            "price": "Custom",
            "currency": "USD",
            "billing_period": "month",
            "features": {
                "documents_per_month": "Unlimited",
                "templates_access": "All templates + custom templates",
                "storage_gb": "Unlimited",
                "support": "Dedicated account manager",
                "api_access": True,
                "custom_branding": True,
                "priority_support": True,
                "electronic_signatures": True,
                "bulk_operations": True,
                "analytics": True,
                "sso": True,
                "custom_integrations": True,
                "legal_review": True
            },
            "contact_sales": True
        }
    }
    
    return {"plans": plans}


@router.get("/current")
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's subscription information
    """
    try:
        # Get active subscription
        result = await db.execute(
            select(Subscription)
            .where(
                Subscription.user_id == current_user.id,
                Subscription.status.in_(["active", "trialing"])
            )
            .order_by(Subscription.created_at.desc())
        )
        subscription = result.scalar_one_or_none()
        
        subscription_info = {
            "user_id": current_user.id,
            "current_tier": current_user.subscription_tier,
            "is_active": subscription.is_active if subscription else False,
            "is_trial": subscription.is_trial if subscription else False,
            "stripe_customer_id": current_user.stripe_customer_id,
            "subscription": None
        }
        
        if subscription:
            subscription_info["subscription"] = {
                "id": subscription.id,
                "plan_type": subscription.plan_type,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "days_until_renewal": subscription.days_until_renewal
            }
        
        return subscription_info
        
    except Exception as e:
        logger.error(f"Get subscription error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription information"
        )


@router.post("/upgrade")
async def upgrade_subscription(
    plan_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """
    Upgrade user subscription (would integrate with Stripe)
    """
    try:
        plan_type = plan_data.get("plan_type")
        
        if plan_type not in ["starter", "professional", "enterprise"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan type"
            )
        
        # Check if user is already on this plan or higher
        tier_hierarchy = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}
        current_level = tier_hierarchy.get(current_user.subscription_tier, 0)
        new_level = tier_hierarchy.get(plan_type, 1)
        
        if current_level >= new_level:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot downgrade or select same plan"
            )
        
        # TODO: Integrate with Stripe for actual payment processing
        # For now, just simulate the upgrade
        
        # Update user tier (in production, this would happen after successful payment)
        current_user.subscription_tier = plan_type
        await db.commit()
        
        logger.info(f"Subscription upgraded: {current_user.email} to {plan_type}")
        
        return {
            "message": f"Successfully upgraded to {plan_type} plan",
            "new_tier": plan_type,
            "redirect_url": "/dashboard"  # In production, this would be Stripe checkout URL
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Subscription upgrade error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Subscription upgrade failed"
        )


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """
    Cancel user subscription
    """
    try:
        # Get active subscription
        result = await db.execute(
            select(Subscription)
            .where(
                Subscription.user_id == current_user.id,
                Subscription.status.in_(["active", "trialing"])
            )
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        # TODO: Cancel subscription in Stripe
        # For now, just mark for cancellation at period end
        subscription.cancel_at_period_end = True
        subscription.status = "canceled"
        
        # Downgrade user to free tier (in production, this would happen at period end)
        current_user.subscription_tier = "free"
        
        await db.commit()
        
        logger.info(f"Subscription canceled: {current_user.email}")
        
        return {
            "message": "Subscription canceled successfully",
            "effective_date": subscription.current_period_end,
            "new_tier": "free"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Subscription cancellation error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Subscription cancellation failed"
        )


@router.get("/usage")
async def get_subscription_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current subscription usage and limits
    """
    try:
        from datetime import datetime, timezone
        from sqlalchemy import func
        from app.models.document import GeneratedDocument
        
        # Get current month usage
        current_month_start = datetime.now(timezone.utc).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        
        # Documents created this month
        docs_result = await db.execute(
            select(func.count(GeneratedDocument.id))
            .where(
                GeneratedDocument.user_id == current_user.id,
                GeneratedDocument.created_at >= current_month_start
            )
        )
        documents_this_month = docs_result.scalar() or 0
        
        # Get tier limits
        tier_limits = {
            "free": settings.FREE_TIER_DOCUMENT_LIMIT,
            "starter": settings.STARTER_TIER_DOCUMENT_LIMIT,
            "professional": settings.PROFESSIONAL_TIER_DOCUMENT_LIMIT,
            "enterprise": settings.ENTERPRISE_TIER_DOCUMENT_LIMIT
        }
        
        limit = tier_limits.get(current_user.subscription_tier, 0)
        
        usage_info = {
            "subscription_tier": current_user.subscription_tier,
            "documents_this_month": documents_this_month,
            "document_limit": limit if limit != -1 else "Unlimited",
            "usage_percentage": (documents_this_month / limit * 100) if limit > 0 else 0,
            "can_create_documents": current_user.can_create_documents(documents_this_month),
            "period_start": current_month_start,
            "period_end": datetime.now(timezone.utc).replace(
                month=datetime.now(timezone.utc).month + 1 if datetime.now(timezone.utc).month < 12 else 1,
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
        }
        
        return usage_info
        
    except Exception as e:
        logger.error(f"Get usage error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage information"
        )
