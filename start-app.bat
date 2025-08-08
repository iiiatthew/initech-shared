@echo off
REM FastAPI User & Role Management - Start Script for Windows

echo Starting FastAPI User and Role Management Application...

REM Check if virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found. Creating one...
    python -m venv .venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Dependencies not installed. Installing from requirements.txt...
    pip install -r requirements.txt
)

REM Start the application
echo Starting application on http://localhost:8000
echo Press CTRL+C to stop the server
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000