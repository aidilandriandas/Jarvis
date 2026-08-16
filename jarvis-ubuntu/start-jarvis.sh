#!/bin/bash

# JARVIS Startup Script

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set!"
    echo "Please set your OpenAI API key:"
    echo "  export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    read -p "Enter your OpenAI API key (or press Enter to skip): " api_key
    if [ ! -z "$api_key" ]; then
        export OPENAI_API_KEY="$api_key"
    else
        echo "❌ Cannot start without API key. Exiting..."
        exit 1
    fi
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the backend
echo "🚀 Starting JARVIS backend..."
echo "🌐 Dashboard will be available at: http://localhost:8000"
echo "📡 Open your browser and navigate to the dashboard URL"
echo ""

python backend/main.py
