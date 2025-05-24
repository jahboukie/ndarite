#!/usr/bin/env python3
"""
Development Server Runner
Quick script to start the NDARite backend in development mode
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import uvicorn
        import fastapi
        import sqlalchemy
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_database():
    """Check if database is accessible"""
    try:
        from app.config import settings
        print(f"✅ Database URL configured: {settings.DATABASE_URL}")
        return True
    except Exception as e:
        print(f"❌ Database configuration error: {e}")
        return False

def init_database():
    """Initialize database if needed"""
    try:
        print("🔄 Initializing database...")
        result = subprocess.run([sys.executable, "init_db.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Database initialized successfully")
            return True
        else:
            print(f"❌ Database initialization failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False

def start_server():
    """Start the FastAPI development server"""
    try:
        print("🚀 Starting NDARite backend server...")
        print("📍 Server will be available at: http://localhost:8000")
        print("📚 API documentation at: http://localhost:8000/docs")
        print("🔄 Auto-reload enabled for development")
        print("\nPress Ctrl+C to stop the server\n")
        
        # Start uvicorn with development settings
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--reload-dir", "app",
            "--log-level", "info"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

def main():
    """Main function to run the development server"""
    print("🔧 NDARite Backend Development Server")
    print("=" * 40)
    
    # Change to backend directory if not already there
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check database configuration
    if not check_database():
        sys.exit(1)
    
    # Ask user if they want to initialize database
    init_db = input("🗄️  Initialize/reset database? (y/N): ").lower().strip()
    if init_db in ['y', 'yes']:
        if not init_database():
            sys.exit(1)
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()
