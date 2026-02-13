#!/bin/bash

# Backend startup script

echo "Starting Microbial Segmentation Backend..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create necessary directories
mkdir -p uploads outputs

# Run FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
