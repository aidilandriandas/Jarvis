#!/bin/bash

echo "🚀 Memulai Instalasi JARVIS Ubuntu (9router Edition)..."

# Update sistem
sudo apt update && sudo apt upgrade -y

# Install dependencies sistem
echo "📦 Menginstall dependencies sistem..."
sudo apt install -y python3 python3-pip python3-venv portaudio19-dev espeak ffmpeg git curl

# Membuat direktori proyek
mkdir -p ~/jarvis_ai
cd ~/jarvis_ai

# Membuat virtual environment
echo "🐍 Membuat virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python libraries (Tanpa openai, tambah requests untuk 9router)
echo "📥 Menginstall Python libraries..."
pip install --upgrade pip
pip install fastapi uvicorn[standard] speechrecognition pyaudio pyttsx3 wikipedia pywhatkit pyautogui keyboard requests websockets

# Membuat file konfigurasi .env
if [ ! -f .env ]; then
    echo "⚙️ Membuat file konfigurasi .env..."
    cat > .env << EOL
# Konfigurasi 9router / Local AI
AI_API_URL="http://localhost:1234/v1/chat/completions" # Ganti dengan URL 9router Anda
AI_API_KEY="tidak-perlu-kunci-lokal" # Ganti jika 9router butuh kunci
AI_MODEL="local-model" # Nama model di 9router Anda

# Konfigurasi Server
HOST="0.0.0.0"
PORT="8000"
EOL
    echo "✅ File .env dibuat. Silakan edit ~/jarvis_ai/.env untuk menyesuaikan URL 9router Anda."
else
    echo "⚠️ File .env sudah ada, melewatinya."
fi

# Menyalin file source (Asumsi file sudah ada atau akan dibuat oleh user, disini kita buat placeholder jika belum)
# Dalam skenario nyata, file backend.py dan frontend sudah ada di repo ini.
# Kita asumsikan user akan menaruh file backend.py yang sudah diupdate di sini.

echo ""
echo "✅ Instalasi Selesai!"
echo "----------------------------------------"
echo "LANGKAH SELANJUTNYA:"
echo "1. Edit file .env di ~/jarvis_ai/ dan pastikan AI_API_URL mengarah ke 9router Anda."
echo "2. Aktifkan venv: source ~/jarvis_ai/venv/bin/activate"
echo "3. Jalankan Server: python3 backend.py"
echo "4. Buka Dashboard: http://localhost:8000"
echo "----------------------------------------"
