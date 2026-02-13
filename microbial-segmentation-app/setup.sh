#!/bin/bash

# Automated setup script for Microbial Segmentation App

set -e  # Exit on error

echo "=========================================="
echo "Microbial Segmentation App - Setup"
echo "=========================================="
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION found"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi
NODE_VERSION=$(node --version)
echo "✓ Node.js $NODE_VERSION found"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi
NPM_VERSION=$(npm --version)
echo "✓ npm $NPM_VERSION found"

echo ""
echo "=========================================="
echo "Setting up Backend..."
echo "=========================================="
echo ""

cd backend

# Check if model checkpoint exists
if [ ! -f "temporal_unet_TC_finetuned.pt" ]; then
    echo "⚠️  Warning: Model checkpoint 'temporal_unet_TC_finetuned.pt' not found!"
    echo "   Please copy your model checkpoint to: backend/temporal_unet_TC_finetuned.pt"
    echo ""
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
echo "✓ Python dependencies installed"

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads outputs
echo "✓ Directories created"

# Deactivate virtual environment
deactivate

cd ..

echo ""
echo "=========================================="
echo "Setting up Frontend..."
echo "=========================================="
echo ""

cd frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies (this may take a few minutes)..."
npm install
echo "✓ Node.js dependencies installed"

cd ..

echo ""
echo "=========================================="
echo "Setup Complete! ✅"
echo "=========================================="
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  ./run.sh"
echo "  # Or: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo ""
echo "For testing:"
echo "  cd scripts"
echo "  python test_local.py --input /path/to/video.mp4 --checkpoint ../backend/temporal_unet_TC_finetuned.pt"
echo ""
echo "See QUICKSTART.md for more details."
echo "=========================================="
