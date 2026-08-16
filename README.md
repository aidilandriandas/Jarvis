# 🤖 J.A.R.V.I.S. - Full Edition
### Just A Rather Very Intelligent System

Asisten AI super canggih untuk Ubuntu Desktop dengan kontrol penuh sistem, integrasi 9router (AI lokal), dashboard futuristik, dan voice control.

---

## ✨ Fitur Lengkap

### 🧠 **Kontrol Sistem & Otomasi**
- ✅ Eksekusi perintah terminal dengan safety check
- ✅ Manajemen file (create, delete, move, copy, read, list)
- ✅ Install/uninstall aplikasi (apt & pip)
- ✅ Monitoring resource real-time (CPU, RAM, Disk, Network)
- ✅ Manajemen proses (list, kill suspicious processes)

### 🖥️ **GUI Automation**
- ✅ Screenshot layar
- ✅ Kontrol mouse (click, move)
- ✅ Kontrol keyboard (type, press special keys)
- ✅ Deteksi resolusi layar

### 🔒 **Keamanan & Privasi**
- ✅ Enkripsi/dekripsi file dengan password
- ✅ Scan proses mencurigakan (miner, bot, trojan)
- ✅ Safety block untuk command berbahaya
- ✅ Mode stealth (tanpa log)

### 🛠️ **Developer Tools**
- ✅ Operasi Git (status, commit, push, pull)
- ✅ Run code snippets (Python, Bash)
- ✅ Auto-debugging assistance

### 🌐 **Konektivitas & Internet**
- ✅ Search web (DuckDuckGo)
- ✅ Download file dari URL
- ✅ Kirim email (via mailutils)
- ✅ Cuaca real-time (wttr.in)
- ✅ Wikipedia search
- ✅ YouTube player

### 🎨 **System Customization**
- ✅ Ganti wallpaper desktop
- ✅ Atur kecerahan layar
- ✅ Kustomisasi tema dashboard

### 🎤 **Voice Control & Dashboard**
- ✅ Input suara (Web Speech API)
- ✅ Output suara (Text-to-Speech)
- ✅ Dashboard Iron Man style
- ✅ Real-time system stats
- ✅ Quick action buttons

---

## 📦 Instalasi

### 1. Clone atau Download Repository
```bash
cd /workspace
```

### 2. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install -y python3-pip python3-venv portaudio19-dev \
                    espeak espeak-data libespeak-dev \
                    scrot xclip xsel wmctrl \
                    mailutils wget curl
```

### 3. Setup 9router (AI Lokal)
Pastikan 9router sudah terinstall dan berjalan di localhost.
Jika belum, ikuti dokumentasi 9router untuk instalasi.

### 4. Konfigurasi Environment
```bash
# Copy file contoh
cp .env.example .env

# Edit sesuai konfigurasi 9router Anda
nano .env
```

Isi `.env`:
```env
AI_API_URL=http://localhost:1234/v1/chat/completions
AI_API_KEY=local-key
AI_MODEL=local-model
```

### 5. Jalankan JARVIS
```bash
python backend.py
```

Server akan berjalan di: **http://localhost:8000**

---

## 🚀 Cara Menggunakan

### Via Dashboard Web
1. Buka browser: `http://localhost:8000`
2. Ketik perintah atau klik tombol mikrofon untuk voice input
3. Lihat respons dan eksekusi aksi di chat
4. Monitor system stats di sidebar

### Contoh Perintah

**Sistem:**
- "Tampilkan info sistem lengkap"
- "List proses yang sedang berjalan"
- "Install vscode"
- "Buka Firefox"

**File:**
- "Buat file test.txt di Documents"
- "Hapus folder temp"
- "Baca isi config.json"
- "Copy file.txt ke backup/"

**Security:**
- "Scan proses mencurigakan"
- "Enkripsi rahasia.txt dengan password123"
- "Dekripsi rahasia.txt.enc dengan password123"

**Automation:**
- "Ambil screenshot"
- "Klik di posisi 500, 300"
- "Ketik Hello World"
- "Tekan tombol enter"

**Developer:**
- "Git status"
- "Commit perubahan dengan pesan update"
- "Jalankan kode Python: print('Hello')"

**Internet:**
- "Cuaca di Jakarta"
- "Search tentang AI terbaru"
- "Download file dari https://example.com/file.zip"
- "Putar lagu Bohemian Rhapsody di YouTube"

**Customization:**
- "Ganti wallpaper ke /home/user/pictures/bg.jpg"
- "Atur kecerahan ke 70%"

---

## 🎛️ Quick Actions (Dashboard)

Tombol cepat di sidebar:
- 📸 **Screenshot** - Ambil screenshot layar
- 💻 **System Info** - Tampilkan info lengkap sistem
- 🔄 **Processes** - List proses aktif
- 🔒 **Security Scan** - Scan ancaman keamanan

---

## ⚙️ Troubleshooting

### Error: PyAudio tidak terinstall
```bash
sudo apt install portaudio19-dev
pip install pyaudio
```

### Error: pyttsx3 tidak bersuara
```bash
sudo apt install espeak espeak-data
```

### Error: Permission denied untuk screenshot
```bash
sudo apt install scrot
```

### 9router tidak terkoneksi
- Pastikan 9router berjalan
- Cek URL dan port di `.env`
- Test dengan: `curl http://localhost:1234/v1/models`

---

## 🔐 Keamanan

⚠️ **PENTING**: JARVIS memiliki akses penuh ke sistem Anda!
- Jangan jalankan di server publik tanpa proteksi
- Gunakan hanya di lingkungan terpercaya
- Review command sebelum eksekusi (AI sudah ada safety check)
- Backup data penting secara rutin

---

## 📁 Struktur File

```
/workspace/
├── backend.py          # Server utama (FastAPI + AI integration)
├── index.html          # Dashboard frontend
├── requirements.txt    # Python dependencies
├── .env.example        # Template environment
├── .env                # Environment aktif (buat sendiri)
└── README.md           # Dokumentasi ini
```

---

## 🎯 Roadmap Fitur

- [ ] OCR (Optical Character Recognition)
- [ ] Image analysis multimodal
- [ ] Scheduled tasks / cron automation
- [ ] Plugin system untuk ekstensi
- [ ] Mobile app companion
- [ ] Multi-user support dengan autentikasi
- [ ] Encrypted communication
- [ ] Voice profile customization

---

## 📄 License

Open Source - Gunakan dengan bijak!

---

**Created with ❤️ for Ubuntu Desktop**
*"Sometimes you gotta run before you can walk." - Tony Stark*
