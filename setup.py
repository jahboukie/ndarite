#!/usr/bin/env python3
"""
NDARite Platform Setup Script
Automated setup for the complete NDARite platform
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            check=check
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_system_requirements():
    """Check if system requirements are met"""
    print_header("CHECKING SYSTEM REQUIREMENTS")
    
    requirements_met = True
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 11):
        print_success(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print_error(f"Python 3.11+ required, found {python_version.major}.{python_version.minor}")
        requirements_met = False
    
    # Check Node.js
    success, stdout, stderr = run_command("node --version", check=False)
    if success:
        version = stdout.strip()
        print_success(f"Node.js {version}")
    else:
        print_error("Node.js not found. Please install Node.js 18+")
        requirements_met = False
    
    # Check npm
    success, stdout, stderr = run_command("npm --version", check=False)
    if success:
        version = stdout.strip()
        print_success(f"npm {version}")
    else:
        print_error("npm not found")
        requirements_met = False
    
    # Check Docker (optional)
    success, stdout, stderr = run_command("docker --version", check=False)
    if success:
        version = stdout.strip()
        print_success(f"Docker {version}")
    else:
        print_warning("Docker not found (optional for development)")
    
    # Check PostgreSQL (optional)
    success, stdout, stderr = run_command("psql --version", check=False)
    if success:
        version = stdout.strip()
        print_success(f"PostgreSQL {version}")
    else:
        print_warning("PostgreSQL not found (will use Docker)")
    
    return requirements_met

def setup_backend():
    """Set up the backend environment"""
    print_header("SETTING UP BACKEND")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print_error("Backend directory not found")
        return False
    
    os.chdir(backend_dir)
    
    # Create virtual environment
    print_info("Creating Python virtual environment...")
    success, stdout, stderr = run_command(f"{sys.executable} -m venv venv")
    if not success:
        print_error(f"Failed to create virtual environment: {stderr}")
        return False
    print_success("Virtual environment created")
    
    # Determine activation script based on OS
    if platform.system() == "Windows":
        activate_script = "venv\\Scripts\\activate"
        pip_command = "venv\\Scripts\\pip"
        python_command = "venv\\Scripts\\python"
    else:
        activate_script = "venv/bin/activate"
        pip_command = "venv/bin/pip"
        python_command = "venv/bin/python"
    
    # Install Python dependencies
    print_info("Installing Python dependencies...")
    success, stdout, stderr = run_command(f"{pip_command} install --upgrade pip")
    if not success:
        print_error(f"Failed to upgrade pip: {stderr}")
        return False
    
    success, stdout, stderr = run_command(f"{pip_command} install -r requirements.txt")
    if not success:
        print_error(f"Failed to install dependencies: {stderr}")
        return False
    print_success("Python dependencies installed")
    
    # Copy environment file
    env_example = Path(".env.example")
    env_file = Path(".env")
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print_success("Environment file created (.env)")
        print_warning("Please edit .env file with your configuration")
    
    os.chdir("..")
    return True

def setup_frontend():
    """Set up the frontend environment"""
    print_header("SETTING UP FRONTEND")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print_error("Frontend directory not found")
        return False
    
    os.chdir(frontend_dir)
    
    # Install Node.js dependencies
    print_info("Installing Node.js dependencies...")
    success, stdout, stderr = run_command("npm install")
    if not success:
        print_error(f"Failed to install Node.js dependencies: {stderr}")
        return False
    print_success("Node.js dependencies installed")
    
    # Copy environment file
    env_example = Path(".env.example")
    env_local = Path(".env.local")
    if env_example.exists() and not env_local.exists():
        shutil.copy(env_example, env_local)
        print_success("Environment file created (.env.local)")
        print_warning("Please edit .env.local file with your configuration")
    
    os.chdir("..")
    return True

def setup_database():
    """Set up the database"""
    print_header("SETTING UP DATABASE")
    
    choice = input("Choose database setup method:\n1. Docker (recommended)\n2. Local PostgreSQL\n3. Skip\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        return setup_database_docker()
    elif choice == "2":
        return setup_database_local()
    elif choice == "3":
        print_warning("Database setup skipped")
        return True
    else:
        print_error("Invalid choice")
        return False

def setup_database_docker():
    """Set up database using Docker"""
    print_info("Setting up database with Docker...")
    
    # Check if Docker is running
    success, stdout, stderr = run_command("docker info", check=False)
    if not success:
        print_error("Docker is not running. Please start Docker and try again.")
        return False
    
    os.chdir("backend")
    
    # Start database services
    success, stdout, stderr = run_command("docker-compose up -d postgres redis")
    if not success:
        print_error(f"Failed to start database services: {stderr}")
        return False
    
    print_success("Database services started with Docker")
    
    # Wait a moment for services to start
    print_info("Waiting for database to be ready...")
    import time
    time.sleep(5)
    
    # Initialize database
    if platform.system() == "Windows":
        python_command = "venv\\Scripts\\python"
    else:
        python_command = "venv/bin/python"
    
    success, stdout, stderr = run_command(f"{python_command} init_db.py")
    if not success:
        print_error(f"Failed to initialize database: {stderr}")
        return False
    
    print_success("Database initialized successfully")
    os.chdir("..")
    return True

def setup_database_local():
    """Set up database locally"""
    print_info("Setting up local PostgreSQL database...")
    
    # Check if PostgreSQL is available
    success, stdout, stderr = run_command("psql --version", check=False)
    if not success:
        print_error("PostgreSQL not found. Please install PostgreSQL or use Docker option.")
        return False
    
    # Create database
    db_name = "ndarite"
    success, stdout, stderr = run_command(f"createdb {db_name}", check=False)
    if success:
        print_success(f"Database '{db_name}' created")
    else:
        print_warning(f"Database might already exist: {stderr}")
    
    # Initialize database
    os.chdir("backend")
    if platform.system() == "Windows":
        python_command = "venv\\Scripts\\python"
    else:
        python_command = "venv/bin/python"
    
    success, stdout, stderr = run_command(f"{python_command} init_db.py")
    if not success:
        print_error(f"Failed to initialize database: {stderr}")
        return False
    
    print_success("Database initialized successfully")
    os.chdir("..")
    return True

def create_startup_scripts():
    """Create convenient startup scripts"""
    print_header("CREATING STARTUP SCRIPTS")
    
    # Backend startup script
    if platform.system() == "Windows":
        backend_script = """@echo off
cd backend
call venv\\Scripts\\activate
python run_dev.py
pause
"""
        with open("start_backend.bat", "w") as f:
            f.write(backend_script)
        print_success("Backend startup script created: start_backend.bat")
        
        # Frontend startup script
        frontend_script = """@echo off
cd frontend
npm run dev
pause
"""
        with open("start_frontend.bat", "w") as f:
            f.write(frontend_script)
        print_success("Frontend startup script created: start_frontend.bat")
        
    else:
        backend_script = """#!/bin/bash
cd backend
source venv/bin/activate
python run_dev.py
"""
        with open("start_backend.sh", "w") as f:
            f.write(backend_script)
        os.chmod("start_backend.sh", 0o755)
        print_success("Backend startup script created: start_backend.sh")
        
        # Frontend startup script
        frontend_script = """#!/bin/bash
cd frontend
npm run dev
"""
        with open("start_frontend.sh", "w") as f:
            f.write(frontend_script)
        os.chmod("start_frontend.sh", 0o755)
        print_success("Frontend startup script created: start_frontend.sh")

def print_final_instructions():
    """Print final setup instructions"""
    print_header("SETUP COMPLETE!")
    
    print_success("NDARite platform has been set up successfully!")
    print()
    print_info("Next steps:")
    print("1. Edit configuration files:")
    print("   - backend/.env (database, API keys, etc.)")
    print("   - frontend/.env.local (API URL, Stripe keys, etc.)")
    print()
    print("2. Start the services:")
    if platform.system() == "Windows":
        print("   - Backend: run start_backend.bat")
        print("   - Frontend: run start_frontend.bat")
    else:
        print("   - Backend: ./start_backend.sh")
        print("   - Frontend: ./start_frontend.sh")
    print()
    print("3. Access the application:")
    print("   - Frontend: http://localhost:3000")
    print("   - Backend API: http://localhost:8000")
    print("   - API Docs: http://localhost:8000/docs")
    print()
    print("4. Default admin account:")
    print("   - Email: admin@ndarite.com")
    print("   - Password: admin123!")
    print()
    print_warning("Remember to change the admin password in production!")

def main():
    """Main setup function"""
    print_header("NDARITE PLATFORM SETUP")
    print("This script will set up the complete NDARite platform for development.")
    print()
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print_error("Please run this script from the NDARite root directory")
        sys.exit(1)
    
    # Check system requirements
    if not check_system_requirements():
        print_error("System requirements not met. Please install missing dependencies.")
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print_error("Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print_error("Frontend setup failed")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print_error("Database setup failed")
        sys.exit(1)
    
    # Create startup scripts
    create_startup_scripts()
    
    # Print final instructions
    print_final_instructions()

if __name__ == "__main__":
    main()
