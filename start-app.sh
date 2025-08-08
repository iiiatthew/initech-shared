#!/bin/bash

# FastAPI User & Role Management - Start Script

echo "Starting FastAPI User & Role Management Application..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Dependencies not installed. Installing from requirements.txt..."
    pip install -r requirements.txt
fi

# Start the application
echo "Starting application on http://localhost:8000"
echo "Press CTRL+C to stop the server"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000