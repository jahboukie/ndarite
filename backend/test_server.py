#!/usr/bin/env python3
"""
Simple test server to verify NDARite backend is working
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set environment variables for testing
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_ndarite.db"
os.environ["ENVIRONMENT"] = "development"
os.environ["SECRET_KEY"] = "test-secret-key-for-development-only"

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    # Create a simple test app
    app = FastAPI(title="NDARite Test Server", version="1.0.0")

    @app.get("/")
    async def root():
        return {"message": "NDARite Backend is running!", "status": "success"}

    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "NDARite Backend"}

    if __name__ == "__main__":
        import uvicorn
        print("🚀 Starting NDARite Test Server...")
        print("📍 Server will be available at: http://localhost:8001")
        print("🔄 Press Ctrl+C to stop\n")

        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure all dependencies are installed:")
    print("pip install fastapi uvicorn")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting server: {e}")
    sys.exit(1)
