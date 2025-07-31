#!/bin/bash

# LuLu Dictionary Word Note Generator - Web Application Startup Script

echo "🚀 Starting LuLu Dictionary Word Note Generator Web Application..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if keys.json exists
if [ ! -f "keys.json" ]; then
    echo "⚠️ keys.json not found. Creating from template..."
    if [ -f "keys.json.example" ]; then
        cp keys.json.example keys.json
        echo "📝 Please edit keys.json and add your API keys before running the application."
    else
        echo "📝 Creating keys.json template..."
        cat > keys.json << EOF
{
  "gemini": "",
  "luludict": "",
  "openai": "",
  "anthropic": ""
}
EOF
        echo "📝 Please edit keys.json and add your API keys before running the application."
    fi
fi

# Set environment variables from keys.json if they exist
if [ -f "keys.json" ]; then
    echo "🔑 Loading API keys from keys.json..."
    export GEMINI_API_KEY=$(python3 -c "import json; print(json.load(open('keys.json')).get('gemini', ''))" 2>/dev/null || echo "")
    export LULUDICT_TOKEN=$(python3 -c "import json; print(json.load(open('keys.json')).get('luludict', ''))" 2>/dev/null || echo "")
    export OPENAI_API_KEY=$(python3 -c "import json; print(json.load(open('keys.json')).get('openai', ''))" 2>/dev/null || echo "")
    export ANTHROPIC_API_KEY=$(python3 -c "import json; print(json.load(open('keys.json')).get('anthropic', ''))" 2>/dev/null || echo "")
fi

# Start the Flask application
echo "🌐 Starting Flask web server..."
echo "📡 The application will be available at: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Set Flask environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start the application
python3 app.py
