#!/bin/bash

# Legal Platform Startup Script
# This script starts the unified legal platform server

echo "🚀 Starting Legal Platform Server..."
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "⚠️  Warning: Flask is not installed. Installing Flask..."
    pip3 install flask
fi

# Kill any existing servers on port 8080
echo "🔄 Checking for existing servers..."
if lsof -ti:8080 &> /dev/null; then
    echo "🛑 Stopping existing server on port 8080..."
    lsof -ti:8080 | xargs kill -9
    sleep 2
fi

# Start the unified server
echo "🚀 Launching Unified Legal Platform Server..."
echo "📱 Server will be available at: http://localhost:8080"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python3 unified_server.py 