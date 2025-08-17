#!/bin/bash
# Legal Assistant Startup Script

echo "🏛️  Starting Belgian and EU Legal Assistant..."
echo "================================================"

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "🚀 Starting Ollama..."
    ollama serve &
    sleep 5
fi

# Check if Mixtral model is available
if ! ollama list | grep -q "mixtral"; then
    echo "📥 Downloading Mixtral model..."
    ollama pull mixtral
fi

# Start the legal assistant
echo "🎯 Starting legal assistant..."
python3 app.py
