"""
NDARite Backend - FastAPI Application
Main application entry point
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import engine, create_tables
from app.api.v1 import auth, users, templates, documents, subscriptions
from app.middleware import LoggingMiddleware, SecurityMiddleware


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting NDARite Backend...")
    await create_tables()
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NDARite Backend...")


# Create FastAPI application
app = FastAPI(
    title="NDARite API",
    description="Legal NDA Generation Platform API",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityMiddleware)

# Include API routers
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["Users"]
)

app.include_router(
    templates.router,
    prefix="/api/v1/templates",
    tags=["Templates"]
)

app.include_router(
    documents.router,
    prefix="/api/v1/documents",
    tags=["Documents"]
)

app.include_router(
    subscriptions.router,
    prefix="/api/v1/subscriptions",
    tags=["Subscriptions"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NDARite API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )
