import os
import json
import asyncio
import subprocess
import webbrowser
import requests
import platform
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import pyautogui
import keyboard
import wikipedia
import pywhatkit
from PIL import Image
import io
import base64

# Load konfigurasi dari .env
load_dotenv()

AI_API_URL = os.getenv("AI_API_URL", "http://localhost:1234/v1/chat/completions")
AI_API_KEY = os.getenv("AI_API_KEY", "local-key")
AI_MODEL = os.getenv("AI_MODEL", "local-model")

app = FastAPI()

# Inisialisasi Text-to-Speech
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Kecepatan bicara

# ==================== SYSTEM CONTROL FUNCTIONS ====================

def execute_terminal_command(command: str):
    """Menjalankan perintah terminal Linux dengan timeout dan safety."""
    try:
        # Safety check untuk command berbahaya
        dangerous_cmds = ['rm -rf /', 'mkfs', 'dd if=/dev/zero', ':(){:|:&};:']
        for dangerous in dangerous_cmds:
            if dangerous in command:
                return "⚠️ Command diblokir karena alasan keamanan."
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout.strip() if result.stdout else ""
        error = result.stderr.strip() if result.stderr else ""
        return f"Output: {output}\nError: {error}" if error else f"Output: {output}"
    except subprocess.TimeoutExpired:
        return "⚠️ Timeout: Command terlalu lama."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def open_application(app_name: str):
    """Membuka aplikasi di Ubuntu."""
    try:
        subprocess.Popen(["xdg-open", app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"✅ Membuka {app_name}..."
    except Exception as e:
        return f"❌ Gagal membuka: {str(e)}"

def manage_file(action: str, source: str, destination: str = ""):
    """Manajemen file: create, delete, move, copy, read."""
    try:
        if action == "create":
            Path(source).touch()
            return f"✅ File dibuat: {source}"
        elif action == "delete":
            if os.path.isfile(source):
                os.remove(source)
            elif os.path.isdir(source):
                shutil.rmtree(source)
            return f"✅ Dihapus: {source}"
        elif action == "move":
            shutil.move(source, destination)
            return f"✅ Dipindah: {source} -> {destination}"
        elif action == "copy":
            if os.path.isfile(source):
                shutil.copy2(source, destination)
            else:
                shutil.copytree(source, destination)
            return f"✅ Disalin: {source} -> {destination}"
        elif action == "read":
            with open(source, 'r') as f:
                content = f.read(1000)  # Batasi 1000 char
            return f"📄 Isi file:\n{content}"
        elif action == "list":
            items = os.listdir(source)
            return f"📁 Konten folder:\n" + "\n".join(items[:50])
        else:
            return "❌ Action tidak dikenali."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def install_package(package_name: str):
    """Install aplikasi/package di Ubuntu."""
    try:
        # Coba apt terlebih dahulu
        result = subprocess.run(f"sudo apt update && sudo apt install -y {package_name}", 
                              shell=True, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return f"✅ {package_name} berhasil diinstall."
        else:
            # Coba pip jika apt gagal
            result2 = subprocess.run(f"pip install {package_name}", shell=True, capture_output=True, text=True, timeout=60)
            if result2.returncode == 0:
                return f"✅ {package_name} (Python) berhasil diinstall."
            return f"❌ Gagal install: {result2.stderr}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_system_info():
    """Mendapatkan info sistem lengkap."""
    import psutil
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        
        info = {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_usage": f"{cpu_percent}%",
            "ram_total": f"{mem.total / (1024**3):.2f} GB",
            "ram_used": f"{mem.used / (1024**3):.2f} GB ({mem.percent}%)",
            "disk_total": f"{disk.total / (1024**3):.2f} GB",
            "disk_used": f"{disk.used / (1024**3):.2f} GB ({disk.percent}%)",
            "boot_time": boot_time,
            "python_version": platform.python_version()
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_process_list(limit: int = 10):
    """Daftar proses yang sedang berjalan."""
    try:
        import psutil
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        result = "\n".join([f"PID: {p['pid']}, Name: {p['name']}, CPU: {p.get('cpu_percent', 0):.1f}%, RAM: {p.get('memory_percent', 0):.1f}%" 
                          for p in processes[:limit]])
        return f"🔄 Top {limit} Proses:\n{result}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def kill_process(pid: int):
    """Menghentikan proses berdasarkan PID."""
    try:
        import psutil
        proc = psutil.Process(pid)
        proc.terminate()
        return f"✅ Proses {pid} dihentikan."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==================== GUI CONTROL FUNCTIONS ====================

def take_screenshot(filename: str = "screenshot.png"):
    """Mengambil screenshot layar."""
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return f"📸 Screenshot disimpan: {filename}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def mouse_click(x: int = None, y: int = None, button: str = "left"):
    """Klik mouse di posisi tertentu atau posisi saat ini."""
    try:
        if x is not None and y is not None:
            pyautogui.click(x, y, button=button)
            return f"🖱️ Klik {button} di ({x}, {y})"
        else:
            pyautogui.click(button=button)
            return f"🖱️ Klik {button} di posisi saat ini"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def mouse_move(x: int, y: int):
    """Gerakkan mouse ke koordinat tertentu."""
    try:
        pyautogui.moveTo(x, y, duration=0.5)
        return f"🖱️ Mouse dipindah ke ({x}, {y})"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def keyboard_type(text: str):
    """Mengetik teks menggunakan keyboard virtual."""
    try:
        pyautogui.write(text, interval=0.05)
        return f"⌨️ Teks diketik: {text[:50]}..."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def keyboard_press(key: str):
    """Menekan tombol keyboard khusus."""
    try:
        pyautogui.press(key)
        return f"⌨️ Tombol ditekan: {key}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_screen_resolution():
    """Mendapatkan resolusi layar."""
    try:
        width, height = pyautogui.size()
        return f"📺 Resolusi: {width}x{height}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==================== SECURITY FUNCTIONS ====================

def encrypt_file(filepath: str, password: str):
    """Enkripsi file sederhana menggunakan hash."""
    try:
        # Note: Ini enkripsi dasar, untuk produksi gunakan cryptography library
        with open(filepath, 'rb') as f:
            content = f.read()
        
        key = hashlib.sha256(password.encode()).digest()
        encrypted = bytes([content[i] ^ key[i % len(key)] for i in range(len(content))])
        
        enc_path = filepath + ".enc"
        with open(enc_path, 'wb') as f:
            f.write(encrypted)
        
        return f"🔒 File dienkripsi: {enc_path}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def decrypt_file(filepath: str, password: str):
    """Dekripsi file yang dienkripsi."""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        key = hashlib.sha256(password.encode()).digest()
        decrypted = bytes([content[i] ^ key[i % len(key)] for i in range(len(content))])
        
        dec_path = filepath.replace(".enc", "")
        with open(dec_path, 'wb') as f:
            f.write(decrypted)
        
        return f"🔓 File didekripsi: {dec_path}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def scan_processes(suspicious_only: bool = True):
    """Scan proses mencurigakan."""
    try:
        import psutil
        suspicious = []
        suspicious_names = ['miner', 'bot', 'trojan', 'backdoor', 'rootkit']
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = proc.info['name'].lower()
                cmdline = ' '.join(proc.info['cmdline'] or []).lower()
                if any(sus in name or sus in cmdline for sus in suspicious_names):
                    suspicious.append(f"PID: {proc.info['pid']}, Name: {name}")
            except:
                pass
        
        if suspicious:
            return f"⚠️ Proses mencurigakan ditemukan:\n" + "\n".join(suspicious)
        return "✅ Tidak ada proses mencurigakan terdeteksi."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==================== DEVELOPER FUNCTIONS ====================

def git_operation(operation: str, repo_path: str = ".", message: str = "", remote: str = "origin"):
    """Operasi Git otomatis."""
    try:
        if operation == "status":
            result = subprocess.run(f"cd {repo_path} && git status", shell=True, capture_output=True, text=True)
            return f"📊 Git Status:\n{result.stdout}"
        elif operation == "commit":
            subprocess.run(f"cd {repo_path} && git add .", shell=True)
            subprocess.run(f"cd {repo_path} && git commit -m '{message}'", shell=True)
            return f"✅ Commit berhasil: {message}"
        elif operation == "push":
            subprocess.run(f"cd {repo_path} && git push {remote}", shell=True)
            return f"✅ Push berhasil ke {remote}"
        elif operation == "pull":
            result = subprocess.run(f"cd {repo_path} && git pull {remote}", shell=True, capture_output=True, text=True)
            return f"✅ Pull result:\n{result.stdout}"
        else:
            return "❌ Operasi tidak dikenali."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def run_code(language: str, code: str):
    """Menjalankan snippet kode."""
    try:
        filename = f"temp_{language}"
        if language == "python":
            filename += ".py"
            with open(filename, 'w') as f:
                f.write(code)
            result = subprocess.run(f"python3 {filename}", shell=True, capture_output=True, text=True, timeout=10)
            os.remove(filename)
            return f"🐍 Python Output:\n{result.stdout}\nError: {result.stderr}" if result.stderr else f"🐍 Python Output:\n{result.stdout}"
        elif language == "bash":
            result = subprocess.run(code, shell=True, capture_output=True, text=True, timeout=10)
            return f"📟 Bash Output:\n{result.stdout}\nError: {result.stderr}" if result.stderr else f"📟 Bash Output:\n{result.stdout}"
        else:
            return f"❌ Bahasa {language} belum didukung."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def search_web(query: str):
    """Mencari informasi dari web (menggunakan duckduckgo search via terminal)."""
    try:
        # Menggunakan ddgr atau curl untuk search
        result = subprocess.run(f"curl -s 'https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}' | grep -oP '(?<=<a href=\").*?(?=\" class=\"result__a\")' | head -5", 
                              shell=True, capture_output=True, text=True, timeout=10)
        return f"🌐 Hasil pencarian untuk '{query}':\n{result.stdout}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def download_file(url: str, save_path: str = ""):
    """Download file dari URL."""
    try:
        if not save_path:
            save_path = url.split('/')[-1]
        result = subprocess.run(f"wget -O {save_path} '{url}'", shell=True, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return f"⬇️ File didownload: {save_path}"
        return f"❌ Gagal download: {result.stderr}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def send_email(to: str, subject: str, body: str):
    """Kirim email (menggunakan mail command di Linux)."""
    try:
        result = subprocess.run(f"echo '{body}' | mail -s '{subject}' {to}", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return f"📧 Email dikirim ke {to}"
        return f"⚠️ Mail command tidak tersedia. Install dengan: sudo apt install mailutils"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def set_wallpaper(image_path: str):
    """Ganti wallpaper desktop."""
    try:
        # Untuk GNOME
        subprocess.run(f"gsettings set org.gnome.desktop.background picture-uri 'file://{image_path}'", shell=True)
        subprocess.run(f"gsettings set org.gnome.desktop.background picture-uri-dark 'file://{image_path}'", shell=True)
        return f"🖼️ Wallpaper diganti: {image_path}"
    except Exception as e:
        return f"⚠️ Gagal ganti wallpaper (mungkin bukan GNOME): {str(e)}"

def change_brightness(level: int):
    """Ubah kecerahan layar (jika didukung)."""
    try:
        # Membutuhkan xbacklight atau brightnessctl
        result = subprocess.run(f"xbacklight -set {level}", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return f"💡 Kecerahan diubah ke {level}%"
        return "⚠️ xbacklight tidak tersedia. Install dengan: sudo apt install xbacklight"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_weather(city: str):
    """Dapatkan cuaca dari wttr.in."""
    try:
        result = subprocess.run(f"curl -s 'wttr.in/{city}?format=3'", shell=True, capture_output=True, text=True, timeout=10)
        return f"🌤️ Cuaca di {city}: {result.stdout}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def search_wikipedia(query: str):
    """Mencari ringkasan di Wikipedia."""
    try:
        return wikipedia.summary(query, sentences=3)
    except Exception as e:
        return f"❌ Tidak menemukan info: {str(e)}"

def play_youtube(song: str):
    """Memutar lagu di YouTube."""
    try:
        pywhatkit.playonyt(song)
        return f"▶️ Memutar {song} di YouTube..."
    except Exception as e:
        return f"❌ Gagal memutar: {str(e)}"

# ==================== DEFINISI TOOLS UNTUK AI ====================

tools_definition = [
    {"type": "function", "function": {"name": "execute_terminal_command", "description": "Menjalankan perintah terminal Linux. Gunakan untuk instalasi, navigasi, manajemen sistem.", "parameters": {"type": "object", "properties": {"command": {"type": "string", "description": "Perintah terminal"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "open_application", "description": "Membuka aplikasi atau file di Ubuntu.", "parameters": {"type": "object", "properties": {"app_name": {"type": "string", "description": "Nama aplikasi atau path"}}, "required": ["app_name"]}}},
    {"type": "function", "function": {"name": "manage_file", "description": "Manajemen file: create, delete, move, copy, read, list.", "parameters": {"type": "object", "properties": {"action": {"type": "string", "enum": ["create", "delete", "move", "copy", "read", "list"]}, "source": {"type": "string"}, "destination": {"type": "string"}}, "required": ["action", "source"]}}},
    {"type": "function", "function": {"name": "install_package", "description": "Install aplikasi/package (apt atau pip).", "parameters": {"type": "object", "properties": {"package_name": {"type": "string"}}, "required": ["package_name"]}}},
    {"type": "function", "function": {"name": "get_system_info", "description": "Info lengkap sistem: CPU, RAM, Disk, OS.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "get_process_list", "description": "Daftar proses berjalan.", "parameters": {"type": "object", "properties": {"limit": {"type": "integer", "default": 10}}, "required": []}}},
    {"type": "function", "function": {"name": "kill_process", "description": "Hentikan proses berdasarkan PID.", "parameters": {"type": "object", "properties": {"pid": {"type": "integer"}}, "required": ["pid"]}}},
    {"type": "function", "function": {"name": "take_screenshot", "description": "Ambil screenshot layar.", "parameters": {"type": "object", "properties": {"filename": {"type": "string", "default": "screenshot.png"}}, "required": []}}},
    {"type": "function", "function": {"name": "mouse_click", "description": "Klik mouse di posisi tertentu.", "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}, "button": {"type": "string", "enum": ["left", "right", "middle"]}}, "required": []}}},
    {"type": "function", "function": {"name": "mouse_move", "description": "Gerakkan mouse ke koordinat.", "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]}}},
    {"type": "function", "function": {"name": "keyboard_type", "description": "Ketik teks menggunakan keyboard virtual.", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "keyboard_press", "description": "Tekan tombol keyboard khusus (enter, tab, ctrl+c, dll).", "parameters": {"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]}}},
    {"type": "function", "function": {"name": "get_screen_resolution", "description": "Dapatkan resolusi layar.", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "encrypt_file", "description": "Enkripsi file dengan password.", "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}, "password": {"type": "string"}}, "required": ["filepath", "password"]}}},
    {"type": "function", "function": {"name": "decrypt_file", "description": "Dekripsi file yang dienkripsi.", "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}, "password": {"type": "string"}}, "required": ["filepath", "password"]}}},
    {"type": "function", "function": {"name": "scan_processes", "description": "Scan proses mencurigakan.", "parameters": {"type": "object", "properties": {"suspicious_only": {"type": "boolean", "default": True}}, "required": []}}},
    {"type": "function", "function": {"name": "git_operation", "description": "Operasi Git: status, commit, push, pull.", "parameters": {"type": "object", "properties": {"operation": {"type": "string", "enum": ["status", "commit", "push", "pull"]}, "repo_path": {"type": "string", "default": "."}, "message": {"type": "string"}, "remote": {"type": "string", "default": "origin"}}, "required": ["operation"]}}},
    {"type": "function", "function": {"name": "run_code", "description": "Jalankan snippet kode Python atau Bash.", "parameters": {"type": "object", "properties": {"language": {"type": "string", "enum": ["python", "bash"]}, "code": {"type": "string"}}, "required": ["language", "code"]}}},
    {"type": "function", "function": {"name": "search_web", "description": "Cari informasi dari web.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "download_file", "description": "Download file dari URL.", "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "save_path": {"type": "string"}}, "required": ["url"]}}},
    {"type": "function", "function": {"name": "send_email", "description": "Kirim email (perlu mailutils).", "parameters": {"type": "object", "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}, "required": ["to", "subject", "body"]}}},
    {"type": "function", "function": {"name": "set_wallpaper", "description": "Ganti wallpaper desktop.", "parameters": {"type": "object", "properties": {"image_path": {"type": "string"}}, "required": ["image_path"]}}},
    {"type": "function", "function": {"name": "change_brightness", "description": "Ubah kecerahan layar.", "parameters": {"type": "object", "properties": {"level": {"type": "integer", "minimum": 0, "maximum": 100}}, "required": ["level"]}}},
    {"type": "function", "function": {"name": "get_weather", "description": "Dapatkan cuaca dari kota.", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
    {"type": "function", "function": {"name": "search_wikipedia", "description": "Cari info di Wikipedia.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "play_youtube", "description": "Putar video di YouTube.", "parameters": {"type": "object", "properties": {"song": {"type": "string"}}, "required": ["song"]}}}
]

available_functions = {
    "execute_terminal_command": execute_terminal_command,
    "open_application": open_application,
    "manage_file": manage_file,
    "install_package": install_package,
    "get_system_info": get_system_info,
    "get_process_list": get_process_list,
    "kill_process": kill_process,
    "take_screenshot": take_screenshot,
    "mouse_click": mouse_click,
    "mouse_move": mouse_move,
    "keyboard_type": keyboard_type,
    "keyboard_press": keyboard_press,
    "get_screen_resolution": get_screen_resolution,
    "encrypt_file": encrypt_file,
    "decrypt_file": decrypt_file,
    "scan_processes": scan_processes,
    "git_operation": git_operation,
    "run_code": run_code,
    "search_web": search_web,
    "download_file": download_file,
    "send_email": send_email,
    "set_wallpaper": set_wallpaper,
    "change_brightness": change_brightness,
    "get_weather": get_weather,
    "search_wikipedia": search_wikipedia,
    "play_youtube": play_youtube
}

def speak(text):
    """Mengubah teks menjadi suara."""
    print(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()

async def call_ai(messages):
    """Mengirim request ke 9router / Local AI."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_API_KEY}"
    }
    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "tools": tools_definition,
        "tool_choice": "auto"
    }
    
    try:
        response = requests.post(AI_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return FileResponse('index.html')

@app.get("/api/system-stats")
async def get_stats():
    """API endpoint untuk stats real-time."""
    import psutil
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        
        return {
            "cpu": cpu,
            "ram_percent": mem.percent,
            "ram_used_gb": round(mem.used / (1024**3), 2),
            "disk_percent": disk.percent,
            "net_sent_mb": round(net.bytes_sent / (1024**2), 2),
            "net_recv_mb": round(net.bytes_recv / (1024**2), 2)
        }
    except Exception as e:
        return {"error": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    messages = [
        {"role": "system", "content": """Anda adalah JARVIS, asisten AI super canggih di Ubuntu Desktop. 
        Anda memiliki kontrol PENUH atas sistem: terminal, file, aplikasi, mouse, keyboard, jaringan, keamanan, dan development.
        
        CAPABILITIES:
        - Kontrol sistem lengkap (install apps, manage files, monitor resources)
        - GUI automation (mouse, keyboard, screenshot)
        - Security (encrypt/decrypt files, scan suspicious processes)
        - Developer tools (git operations, run code snippets)
        - Web operations (search, download, email)
        - System customization (wallpaper, brightness)
        - Information retrieval (wikipedia, weather, news)
        
        STYLE:
        - Jawab singkat, padat, dan profesional seperti AI canggih
        - Gunakan emoji secukupnya untuk visual feedback
        - Selalu konfirmasi sebelum aksi destruktif
        - Jika perintah ambigu, tanya klarifikasi
        
        SAFETY:
        - Jangan jalankan command berbahaya (rm -rf /, mkfs, dll)
        - Berikan warning untuk operasi berisiko"""}
    ]
    
    while True:
        data = await websocket.receive_text()
        user_input = data
        
        messages.append({"role": "user", "content": user_input})
        
        response_data = await call_ai(messages)
        
        if "error" in response_data:
            await websocket.send_text(f"❌ Error AI: {response_data['error']}")
            continue
            
        choice = response_data.get("choices", [{}])[0].get("message", {})
        ai_content = choice.get("content", "")
        tool_calls = choice.get("tool_calls", [])
        
        final_response = ai_content
        
        if tool_calls:
            for tool_call in tool_calls:
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])
                
                if func_name in available_functions:
                    result = available_functions[func_name](**func_args)
                    final_response += f"\n\n🔧 [Action: {func_name}]\n{result}"
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": str(result)
                    })
            
            if tool_calls:
                second_response = await call_ai(messages)
                if "choices" in second_response:
                    final_response = second_response["choices"][0]["message"].get("content", "✅ Perintah dijalankan.")

        messages.append({"role": "assistant", "content": final_response})
        
        await websocket.send_text(final_response)

if __name__ == "__main__":
    import uvicorn
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║           🤖 J.A.R.V.I.S. - FULL EDITION                  ║
    ║  Just A Rather Very Intelligent System                    ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  🚀 Server: http://localhost:8000                         ║
    ║  🧠 AI Endpoint: {AI_API_URL}                   ║
    ║  💻 Platform: {platform.system()} {platform.release()}                          ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  FEATURES:                                                ║
    ║  ✅ Full System Control                                   ║
    ║  ✅ GUI Automation (Mouse/Keyboard)                       ║
    ║  ✅ Security & Encryption                                 ║
    ║  ✅ Developer Tools (Git, Code Runner)                    ║
    ║  ✅ Real-time Dashboard                                   ║
    ║  ✅ Voice Control                                         ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)
