"""
Database Initialization Script
Create initial database tables and seed data
"""

import asyncio
import logging
from sqlalchemy import text

from app.database import engine, create_tables
from app.models.template import TemplateCategory, NDATemplate
from app.models.user import User
from app.utils.security import get_password_hash
from app.database import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_template_categories():
    """Create initial template categories"""
    async with AsyncSessionLocal() as session:
        try:
            categories = [
                {
                    "name": "Business & Commercial",
                    "description": "NDAs for business partnerships, vendor relationships, and commercial transactions",
                    "slug": "business-commercial",
                    "sort_order": 1
                },
                {
                    "name": "Employment & HR",
                    "description": "Employee confidentiality agreements and HR-related NDAs",
                    "slug": "employment-hr",
                    "sort_order": 2
                },
                {
                    "name": "Technology & Software",
                    "description": "NDAs for software development, technology partnerships, and IP protection",
                    "slug": "technology-software",
                    "sort_order": 3
                },
                {
                    "name": "Investment & Finance",
                    "description": "NDAs for investment discussions, financial partnerships, and due diligence",
                    "slug": "investment-finance",
                    "sort_order": 4
                },
                {
                    "name": "Healthcare & Medical",
                    "description": "Medical confidentiality agreements and healthcare-related NDAs",
                    "slug": "healthcare-medical",
                    "sort_order": 5
                },
                {
                    "name": "Real Estate",
                    "description": "NDAs for real estate transactions and property development",
                    "slug": "real-estate",
                    "sort_order": 6
                }
            ]
            
            for cat_data in categories:
                category = TemplateCategory(**cat_data)
                session.add(category)
            
            await session.commit()
            logger.info("Template categories created successfully")
            
        except Exception as e:
            logger.error(f"Error creating template categories: {e}")
            await session.rollback()


async def create_sample_templates():
    """Create sample NDA templates"""
    async with AsyncSessionLocal() as session:
        try:
            # Get business category
            from sqlalchemy import select
            result = await session.execute(
                select(TemplateCategory).where(TemplateCategory.slug == "business-commercial")
            )
            business_category = result.scalar_one_or_none()
            
            if not business_category:
                logger.error("Business category not found")
                return
            
            # Sample template content structure
            template_content = {
                "sections": [
                    {
                        "id": "definition",
                        "title": "Definition of Confidential Information",
                        "content": "For purposes of this Agreement, \"Confidential Information\" means any and all non-public, confidential or proprietary information..."
                    },
                    {
                        "id": "obligations",
                        "title": "Obligations of Receiving Party",
                        "content": "The Receiving Party agrees to hold and maintain the Confidential Information in strict confidence..."
                    },
                    {
                        "id": "term",
                        "title": "Term",
                        "content": "This Agreement shall remain in effect for a period of {{term_years}} years..."
                    }
                ],
                "variables": [
                    {"name": "term_years", "type": "number", "default": 3},
                    {"name": "governing_law", "type": "text", "default": "United States"}
                ],
                "formatting": {
                    "font": "Times New Roman",
                    "font_size": 12,
                    "line_spacing": 1.6
                }
            }
            
            required_fields = {
                "disclosing_party": {
                    "type": "object",
                    "required": True,
                    "fields": {
                        "name": {"type": "text", "required": True},
                        "address": {"type": "text", "required": True},
                        "email": {"type": "email", "required": True}
                    }
                },
                "receiving_party": {
                    "type": "object",
                    "required": True,
                    "fields": {
                        "name": {"type": "text", "required": True},
                        "address": {"type": "text", "required": True},
                        "email": {"type": "email", "required": True}
                    }
                },
                "effective_date": {"type": "date", "required": False},
                "term_years": {"type": "number", "required": False, "default": 3}
            }
            
            templates = [
                {
                    "name": "Standard Bilateral NDA",
                    "description": "A comprehensive bilateral non-disclosure agreement suitable for most business relationships",
                    "template_type": "bilateral",
                    "jurisdiction": "United States",
                    "industry_focus": "General Business",
                    "complexity_level": "standard",
                    "template_content": template_content,
                    "required_fields": required_fields,
                    "tier_requirement": "free",
                    "category_id": business_category.id
                },
                {
                    "name": "Simple Unilateral NDA",
                    "description": "A straightforward one-way confidentiality agreement",
                    "template_type": "unilateral",
                    "jurisdiction": "United States",
                    "industry_focus": "General Business",
                    "complexity_level": "basic",
                    "template_content": template_content,
                    "required_fields": required_fields,
                    "tier_requirement": "free",
                    "category_id": business_category.id
                },
                {
                    "name": "Advanced Bilateral NDA",
                    "description": "A comprehensive bilateral NDA with advanced clauses for complex business relationships",
                    "template_type": "bilateral",
                    "jurisdiction": "United States",
                    "industry_focus": "General Business",
                    "complexity_level": "advanced",
                    "template_content": template_content,
                    "required_fields": required_fields,
                    "tier_requirement": "professional",
                    "category_id": business_category.id
                }
            ]
            
            for template_data in templates:
                template = NDATemplate(**template_data)
                session.add(template)
            
            await session.commit()
            logger.info("Sample templates created successfully")
            
        except Exception as e:
            logger.error(f"Error creating sample templates: {e}")
            await session.rollback()


async def create_admin_user():
    """Create default admin user"""
    async with AsyncSessionLocal() as session:
        try:
            # Check if admin user already exists
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.email == "admin@ndarite.com")
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                logger.info("Admin user already exists")
                return
            
            # Create admin user
            admin_user = User(
                email="admin@ndarite.com",
                password_hash=get_password_hash("admin123!"),
                first_name="Admin",
                last_name="User",
                company_name="NDARite",
                role="admin",
                subscription_tier="enterprise",
                email_verified=True
            )
            
            session.add(admin_user)
            await session.commit()
            
            logger.info("Admin user created: admin@ndarite.com / admin123!")
            
        except Exception as e:
            logger.error(f"Error creating admin user: {e}")
            await session.rollback()


async def init_database():
    """Initialize database with tables and seed data"""
    try:
        logger.info("Starting database initialization...")
        
        # Create tables
        await create_tables()
        
        # Create seed data
        await create_template_categories()
        await create_sample_templates()
        await create_admin_user()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(init_database())
