"""
NDARite Backend Configuration
Environment variables and application settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "NDARite"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://ndarite.com",
        "https://app.ndarite.com"
    ]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/ndarite"
    
    # Redis (for caching and task queue)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Email Configuration
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "noreply@ndarite.com"
    FROM_NAME: str = "NDARite"
    
    # File Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "ndarite-documents"
    
    # External API Keys
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    DOCUSIGN_INTEGRATION_KEY: Optional[str] = None
    DOCUSIGN_USER_ID: Optional[str] = None
    DOCUSIGN_ACCOUNT_ID: Optional[str] = None
    DOCUSIGN_PRIVATE_KEY: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Document Generation
    MAX_DOCUMENT_SIZE_MB: int = 10
    SUPPORTED_FORMATS: List[str] = ["pdf", "docx"]
    
    # Subscription Tiers
    FREE_TIER_DOCUMENT_LIMIT: int = 3
    STARTER_TIER_DOCUMENT_LIMIT: int = 25
    PROFESSIONAL_TIER_DOCUMENT_LIMIT: int = 100
    ENTERPRISE_TIER_DOCUMENT_LIMIT: int = -1  # Unlimited
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


# Validation
def validate_settings():
    """Validate critical settings"""
    if settings.ENVIRONMENT == "production":
        required_production_vars = [
            "SECRET_KEY",
            "DATABASE_URL",
            "SENDGRID_API_KEY",
            "STRIPE_SECRET_KEY",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY"
        ]
        
        missing_vars = []
        for var in required_production_vars:
            if not getattr(settings, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(
                f"Missing required production environment variables: {', '.join(missing_vars)}"
            )


# Run validation
validate_settings()
