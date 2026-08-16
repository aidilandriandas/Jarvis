# JARVIS - AI Desktop Assistant for Ubuntu

Just A Rather Very Intelligent System - Asisten AI pribadi seperti milik Tony Stark, sekarang untuk Ubuntu Desktop Anda!

## 🎯 Fitur Utama

### 🧠 Kecerdasan Buatan
- **OpenAI GPT-4 Integration**: Memahami perintah dalam bahasa alami
- **Function Calling**: AI dapat memilih dan menjalankan fungsi sistem secara otomatis
- **Multi-bahasa**: Mendukung Bahasa Indonesia dan Inggris

### 🎤 Kontrol Suara
- **Speech Recognition**: Perintah suara real-time melalui browser
- **Text-to-Speech**: Respons suara yang natural
- **Auto-listen Mode**: Mode mendengarkan terus-menerus

### 💻 Kontrol Penuh Sistem
- **Terminal Commands**: Jalankan perintah terminal apa pun
- **Application Control**: Buka/tutup aplikasi (Firefox, Chrome, Terminal, dll)
- **Mouse Control**: Klik, geser, scroll
- **Keyboard Control**: Ketik teks, tekan tombol
- **System Info**: Monitor CPU, RAM, Disk usage
- **Volume Control**: Atur volume sistem
- **Screenshot**: Ambil tangkapan layar
- **Web Search**: Cari di Google langsung

### 🎨 Dashboard Futuristik
- **Arc Reactor Animation**: Visualisasi status ala Iron Man
- **Real-time Logs**: Lihat semua aktivitas sistem
- **Chat Interface**: Interaksi teks dan suara
- **System Stats**: Monitor performa sistem
- **Responsive Design**: Bekerja di berbagai ukuran layar

## 📦 Instalasi

### Prerequisites
- Ubuntu 20.04 atau lebih baru
- Python 3.8+
- OpenAI API Key (dapatkan dari https://platform.openai.com)
- Koneksi internet

### Quick Install

```bash
# Clone atau download project ini
cd jarvis-ubuntu

# Jalankan installer
chmod +x install.sh
./install.sh
```

### Manual Install

```bash
# Install dependencies sistem
sudo apt update
sudo apt install -y python3-pip python3-venv pulseaudio portaudio19-dev wmctrl xdotool scrot espeak libespeak-dev

# Install Python packages
pip3 install fastapi uvicorn websockets openai speechrecognition pyttsx3 pyautogui psutil python-multipart pyaudio

# Set API key
export OPENAI_API_KEY='your-api-key-here'

# Jalankan JARVIS
python backend/main.py
```

## 🚀 Cara Menggunakan

### 1. Start JARVIS

```bash
# Method 1: Menggunakan startup script
./start-jarvis.sh

# Method 2: Manual
export OPENAI_API_KEY='your-api-key-here'
python backend/main.py

# Method 3: Dari Applications Menu
Cari "JARVIS Assistant" di menu aplikasi Ubuntu
```

### 2. Akses Dashboard

Buka browser dan navigasi ke:
```
http://localhost:8000
```

### 3. Beri Perintah

**Via Suara:**
1. Klik tombol "🎤 Voice Command"
2. Izinkan akses mikrofon di browser
3. Ucapkan perintah Anda

**Via Teks:**
1. Ketik perintah di kolom input
2. Tekan Enter atau klik "Send"

## 📝 Contoh Perintah

### Aplikasi
```
"Buka Firefox"
"Open Chrome"
"Launch terminal"
"Tutup calculator"
```

### Sistem
```
"Berapa penggunaan CPU saya?"
"What's my memory usage?"
"Ambil screenshot"
"Set volume ke 70"
```

### Web & Informasi
```
"Cari informasi tentang quantum computing"
"Search for latest AI news"
"Buka YouTube dan putar lagu jazz"
```

### Terminal
```
"Jalankan perintah ls -la di terminal"
"Check disk space"
"Update system packages"
```

### Mouse & Keyboard
```
"Klik mouse"
"Scroll down"
"Ketik hello world"
"Tekan enter"
```

### Kompleks
```
"Buka terminal, jalankan top, lalu ambil screenshot"
"Cari info tentang Mars, buka text editor, dan tulis ringkasannya"
"Monitor CPU usage setiap 5 detik"
```

## 🔧 Konfigurasi

### Environment Variables

```bash
# Wajib: OpenAI API Key
export OPENAI_API_KEY='sk-...'

# Opsional: Custom settings
export JARVIS_VOICE_RATE=175      # Kecepatan suara (default: 175)
export JARVIS_VOICE_VOLUME=0.9    # Volume suara (default: 0.9)
export JARVIS_LANGUAGE='id-ID'    # Bahasa (default: en-US)
```

### Custom Functions

Tambahkan fungsi kustom di `backend/main.py`:

```python
def custom_function(param1, param2):
    """Deskripsi fungsi"""
    # Implementasi Anda
    return "Hasil"

# Daftarkan ke available_functions
available_functions["custom_function"] = custom_function

# Tambahkan ke tools list untuk OpenAI
tools.append({
    "type": "function",
    "function": {
        "name": "custom_function",
        "description": "Deskripsi untuk AI",
        "parameters": {...}
    }
})
```

## 🛡️ Keamanan

⚠️ **PENTING**: JARVIS memiliki kontrol penuh atas sistem Anda!

- Jangan pernah memberikan akses ke orang yang tidak dipercaya
- Simpan API key Anda dengan aman
- Gunakan hanya di lingkungan yang aman
- Review log aktivitas secara berkala
- Jangan jalankan perintah berbahaya yang diminta oleh pihak ketiga

## 🐛 Troubleshooting

### PyAudio Error
```bash
# Install dependencies
sudo apt install portaudio19-dev python3-pyaudio

# Reinstall PyAudio
pip uninstall pyaudio
pip install pyaudio
```

### Speech Recognition Tidak Berfungsi
- Pastikan mikrofon terhubung dan berfungsi
- Izinkan akses mikrofon di browser
- Check: `pactl list sources` untuk melihat device mikrofon

### WebSocket Connection Failed
- Pastikan backend berjalan di port 8000
- Check firewall: `sudo ufw allow 8000`
- Restart backend

### Aplikasi Tidak Terbuka
- Install wmctrl: `sudo apt install wmctrl`
- Pastikan aplikasi terinstall di sistem

## 📊 Arsitektur

```
┌─────────────────┐
│   Web Browser   │
│   (Dashboard)   │
└────────┬────────┘
         │ WebSocket
         ▼
┌─────────────────┐
│  FastAPI Server │
│   (Backend)     │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐  ┌──────────┐
│OpenAI │  │  System  │
│  API  │  │ Controls │
└───────┘  └──────────┘
```

## 🤝 Kontribusi

Kontribusi sangat diterima! Silakan:
1. Fork repository
2. Buat feature branch (`git checkout -b feature/amazing-feature`)
3. Commit perubahan (`git commit -m 'Add amazing feature'`)
4. Push ke branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

Project ini dilisensikan di bawah MIT License - lihat file LICENSE untuk detail.

## 🙏 Credits

- **OpenAI** - Untuk API AI yang powerful
- **FastAPI** - Framework backend yang cepat
- **PyAutoGUI** - Library kontrol mouse/keyboard
- **SpeechRecognition** - Library voice recognition
- **pyttsx3** - Text-to-speech engine

## 🎮 Roadmap

- [ ] Support multi-user
- [ ] Plugin system untuk ekstensi
- [ ] Mobile app companion
- [ ] Offline mode dengan model lokal
- [ ] Smart home integration
- [ ] Custom wake word ("Hey JARVIS")
- [ ] Task automation & scheduling
- [ ] Better context memory

---

**"Sometimes you gotta run before you can walk."** - Tony Stark

Dibuat dengan ❤️ untuk komunitas Ubuntu Indonesia
