#!/usr/bin/env python3
"""
Cross-platform start script for FastAPI User & Role Management Application
"""
import platform
import subprocess
import sys
from pathlib import Path


def main():
    print("Starting FastAPI User & Role Management Application...")
    
    # Check if virtual environment exists
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("Virtual environment not found. Creating one...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"])
    
    # Determine the correct Python executable in the virtual environment
    if platform.system() == "Windows":
        python_exe = Path(".venv/Scripts/python.exe")
        pip_exe = Path(".venv/Scripts/pip.exe")
    else:
        python_exe = Path(".venv/bin/python")
        pip_exe = Path(".venv/bin/pip")
    
    # Check if dependencies are installed
    print("Checking dependencies...")
    result = subprocess.run(
        [str(python_exe), "-c", "import fastapi"],
        capture_output=True
    )
    
    if result.returncode != 0:
        print("Dependencies not installed. Installing from requirements.txt...")
        subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"])
    
    # Start the application
    print("\nStarting application on http://localhost:8000")
    print("Press CTRL+C to stop the server\n")
    
    try:
        subprocess.run([
            str(python_exe), "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main()