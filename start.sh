#!/bin/bash

echo "🔧 Starting EdgarTools Content Service..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating one..."
    echo 'SEC_API_USER_AGENT="Crowe/EDGAR Query Engine 1.0 (brett.vantil@crowe.com)"' > .env
fi

# Set default port
export PORT=${PORT:-8001}

# Start the service
echo "🚀 Starting EdgarTools service on port $PORT..."
echo "🌐 Service will be available at http://localhost:$PORT"
echo "📊 Health check: http://localhost:$PORT/health"
echo "🔗 Company search: http://localhost:$PORT/search/company?q=Apple"

uvicorn main:app --host 0.0.0.0 --port $PORT --reload