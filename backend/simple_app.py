#!/usr/bin/env python3
"""
Simplified NDARite Application for Testing
This version works with SQLite and has basic functionality
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set environment variables for testing
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./ndarite.db"
os.environ["ENVIRONMENT"] = "development"
os.environ["SECRET_KEY"] = "test-secret-key-for-development-only-change-in-production"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="NDARite - Legal NDA Generation Platform",
    description="Generate legally-compliant, industry-specific Non-Disclosure Agreements",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic models
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

class MessageResponse(BaseModel):
    message: str
    status: str

# Routes
@app.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint"""
    return MessageResponse(
        message="🎉 NDARite Backend is running! Welcome to the Legal NDA Generation Platform.",
        status="success"
    )

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="NDARite Backend",
        version="1.0.0"
    )

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "v1",
        "status": "operational",
        "features": [
            "User Authentication",
            "Template Management",
            "Document Generation",
            "Subscription Management"
        ],
        "database": "Connected (SQLite)",
        "environment": "development"
    }

# Mock API endpoints for testing
@app.get("/api/v1/templates/")
async def get_templates():
    """Mock templates endpoint"""
    return {
        "templates": [
            {
                "id": "1",
                "name": "Standard Bilateral NDA",
                "description": "A comprehensive bilateral non-disclosure agreement",
                "template_type": "bilateral",
                "complexity_level": "standard",
                "tier_requirement": "free"
            },
            {
                "id": "2",
                "name": "Simple Unilateral NDA",
                "description": "A straightforward one-way confidentiality agreement",
                "template_type": "unilateral",
                "complexity_level": "basic",
                "tier_requirement": "free"
            }
        ],
        "total": 2
    }

@app.get("/api/v1/templates/categories/")
async def get_categories():
    """Mock categories endpoint"""
    return [
        {
            "id": "1",
            "name": "Business & Commercial",
            "description": "NDAs for business partnerships and commercial transactions",
            "slug": "business-commercial",
            "template_count": 5
        },
        {
            "id": "2",
            "name": "Technology & Software",
            "description": "NDAs for software development and technology partnerships",
            "slug": "technology-software",
            "template_count": 3
        }
    ]

@app.post("/api/v1/auth/register")
async def register():
    """Mock registration endpoint"""
    return {
        "message": "Registration endpoint - full implementation coming soon!",
        "status": "mock"
    }

@app.post("/api/v1/auth/login")
async def login():
    """Mock login endpoint with proper token structure"""
    return {
        "access_token": "mock-access-token-12345",
        "refresh_token": "mock-refresh-token-67890",
        "expires_in": 1800,
        "user": {
            "id": "mock-user-123",
            "email": "demo@ndarite.com",
            "first_name": "Demo",
            "last_name": "User",
            "company_name": "NDARite Demo",
            "role": "user",
            "subscription_tier": "free",
            "email_verified": True,
            "created_at": "2025-05-24T00:00:00Z",
            "last_login": "2025-05-24T23:00:00Z"
        }
    }

@app.get("/api/v1/documents/")
async def get_documents():
    """Mock documents endpoint"""
    return {
        "documents": [
            {
                "id": "doc-123",
                "document_name": "Sample Partnership NDA",
                "status": "generated",
                "created_at": "2025-05-24T10:00:00Z",
                "template_id": "template-1"
            },
            {
                "id": "doc-456",
                "document_name": "Employee Confidentiality Agreement",
                "status": "signed",
                "created_at": "2025-05-23T15:30:00Z",
                "template_id": "template-2"
            }
        ],
        "total": 2
    }

@app.get("/api/v1/users/usage-stats")
async def get_usage_stats():
    """Mock usage stats endpoint"""
    return {
        "documents_created": 5,
        "documents_signed": 3,
        "templates_used": 2,
        "storage_used_mb": 1024,
        "api_calls_this_month": 15,
        "subscription_tier": "free",
        "tier_limits": {
            "documents_per_month": 3,
            "storage_gb": 1,
            "api_calls_per_month": 100
        }
    }

@app.post("/api/v1/documents/generate")
async def generate_document():
    """Mock document generation endpoint"""
    return {
        "message": "Document generation endpoint - full implementation coming soon!",
        "document_id": "mock-doc-123",
        "status": "mock"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "message": "Endpoint not found",
            "available_endpoints": [
                "/",
                "/health",
                "/docs",
                "/api/v1/status",
                "/api/v1/templates/",
                "/api/v1/templates/categories/"
            ]
        }
    )

if __name__ == "__main__":
    print("🚀 Starting NDARite Backend (Simplified Version)...")
    print("📍 Server will be available at: http://localhost:8001")
    print("📚 API documentation at: http://localhost:8001/docs")
    print("🔄 This is a simplified version for testing")
    print("\nPress Ctrl+C to stop the server\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
