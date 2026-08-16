#!/bin/bash

# JARVIS Ubuntu Installation Script
# Script ini akan menginstall semua dependencies yang diperlukan

echo "🚀 Starting JARVIS installation for Ubuntu..."

# Update system
echo "📦 Updating system packages..."
sudo apt update -y

# Install Python packages
echo "🐍 Installing Python dependencies..."
pip3 install --user \
    fastapi \
    uvicorn \
    websockets \
    openai \
    speechrecognition \
    pyttsx3 \
    pyautogui \
    psutil \
    python-multipart

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    pulseaudio \
    portaudio19-dev \
    wmctrl \
    xdotool \
    scrot \
    espeak \
    espeak-data \
    libespeak-dev

# Install PyAudio (may need special handling)
echo "🎤 Installing PyAudio..."
pip3 install --user pyaudio || {
    echo "PyAudio installation failed, trying alternative..."
    sudo apt install -y python3-pyaudio
}

# Create virtual environment (optional but recommended)
echo "📁 Creating virtual environment..."
cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate

# Re-install in venv
echo "📦 Installing dependencies in virtual environment..."
pip install \
    fastapi \
    uvicorn \
    websockets \
    openai \
    speechrecognition \
    pyttsx3 \
    pyautogui \
    psutil \
    python-multipart \
    pyaudio

# Create .desktop file for application launcher
echo "🖥️ Creating application launcher..."
cat > ~/.local/share/applications/jarvis.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=JARVIS Assistant
Comment=AI-powered desktop assistant like Tony Stark's JARVIS
Exec=bash -c "cd $(pwd) && source venv/bin/activate && export OPENAI_API_KEY='YOUR_API_KEY' && python backend/main.py"
Icon=$(pwd)/icons/jarvis-icon.png
Terminal=true
Categories=Utility;Application;
Keywords=AI;Assistant;Voice;JARVIS;
StartupNotify=true
EOF

# Make it executable
chmod +x ~/.local/share/applications/jarvis.desktop

# Create startup script
echo "📝 Creating startup script..."
cat > ./start-jarvis.sh << 'EOF'
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
EOF

chmod +x ./start-jarvis.sh

# Download icon (placeholder)
echo "🎨 Setting up icons..."
mkdir -p ./icons
# Create a simple placeholder icon description
cat > ./icons/README.md << 'EOF'
# JARVIS Icons

For best experience, download a circular arc reactor icon and save it as `jarvis-icon.png` (512x512 recommended).

You can find free icons at:
- https://www.flaticon.com
- https://icons8.com

Recommended search terms: "arc reactor", "iron man", "circle tech"
EOF

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Set your OpenAI API key:"
echo "      export OPENAI_API_KEY='your-actual-api-key-here'"
echo ""
echo "   2. Start JARVIS:"
echo "      ./start-jarvis.sh"
echo ""
echo "   3. Open your browser and go to: http://localhost:8000"
echo ""
echo "   4. Or click on 'JARVIS Assistant' in your applications menu"
echo ""
echo "🎯 Example commands to try:"
echo "   - 'Open Firefox'"
echo "   - 'What's my CPU usage?'"
echo "   - 'Take a screenshot'"
echo "   - 'Search for quantum computing'"
echo "   - 'Set volume to 50'"
echo "   - 'Open terminal and run ls -la'"
echo ""
echo "⚠️  Security Note: JARVIS has full control over your system."
echo "   Only use trusted commands and keep your API key secure!"
echo ""
