#!/usr/bin/env python3
"""
JARVIS Backend - Ubuntu Desktop Assistant
Menggunakan OpenAI API untuk kontrol penuh perangkat dengan Function Calling
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List

# FastAPI & WebSocket
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# AI & Speech
import openai
import speech_recognition as sr
import pyttsx3

# System Control
import pyautogui
import psutil

# Konfigurasi
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
openai.api_key = OPENAI_API_KEY

app = FastAPI(title="JARVIS Backend")

# CORS untuk frontend web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inisialisasi Text-to-Speech
engine = pyttsx3.init()
engine.setProperty('rate', 175)
engine.setProperty('volume', 0.9)

# Voice Recognition
recognizer = sr.Recognizer()

# Status sistem
class SystemStatus:
    def __init__(self):
        self.is_listening = False
        self.is_speaking = False
        self.current_task = None
        self.logs = []
        self.active_applications = []
    
    def add_log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {"timestamp": timestamp, "level": level, "message": message}
        self.logs.append(log_entry)
        if len(self.logs) > 100:
            self.logs.pop(0)
        return log_entry
    
    def get_active_apps(self):
        try:
            result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
            apps = [line.split(None, 4)[-1] for line in result.stdout.splitlines() if line.strip()]
            self.active_applications = apps
            return apps
        except:
            return []

status = SystemStatus()

# ===========================
# FUNGSI KONTROL SISTEM (TOOLS)
# ===========================

def execute_terminal_command(command: str) -> str:
    """Menjalankan perintah terminal Ubuntu"""
    try:
        status.add_log(f"Executing terminal command: {command}")
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        output = result.stdout if result.stdout else result.stderr
        status.add_log(f"Command output: {output[:200]}")
        return output[:1000]  # Batasi output
    except Exception as e:
        error_msg = f"Error executing command: {str(e)}"
        status.add_log(error_msg, "ERROR")
        return error_msg

def open_application(app_name: str) -> str:
    """Membuka aplikasi di Ubuntu"""
    app_mapping = {
        "firefox": "firefox",
        "chrome": "google-chrome",
        "terminal": "gnome-terminal",
        "files": "nautilus",
        "text editor": "gedit",
        "vscode": "code",
        "calculator": "gnome-calculator",
        "settings": "gnome-control-center",
        "music": "rhythmbox",
        "camera": "cheese",
    }
    
    try:
        cmd = app_mapping.get(app_name.lower(), app_name.lower())
        status.add_log(f"Opening application: {app_name}")
        subprocess.Popen([cmd], start_new_session=True)
        return f"Successfully opened {app_name}"
    except Exception as e:
        return f"Failed to open {app_name}: {str(e)}"

def close_application(app_name: str) -> str:
    """Menutup aplikasi"""
    try:
        status.add_log(f"Closing application: {app_name}")
        subprocess.run(['pkill', '-f', app_name])
        return f"Closed {app_name}"
    except Exception as e:
        return f"Failed to close {app_name}: {str(e)}"

def control_mouse(action: str, x: int = None, y: int = None) -> str:
    """Kontrol mouse: click, move, scroll"""
    try:
        if action == "click":
            pyautogui.click()
            status.add_log("Mouse clicked")
            return "Mouse clicked"
        elif action == "double_click":
            pyautogui.doubleClick()
            status.add_log("Mouse double clicked")
            return "Mouse double clicked"
        elif action == "move" and x is not None and y is not None:
            pyautogui.moveTo(x, y, duration=0.5)
            status.add_log(f"Mouse moved to ({x}, {y})")
            return f"Mouse moved to ({x}, {y})"
        elif action == "scroll_up":
            pyautogui.scroll(100)
            return "Scrolled up"
        elif action == "scroll_down":
            pyautogui.scroll(-100)
            return "Scrolled down"
        return "Unknown mouse action"
    except Exception as e:
        return f"Mouse control error: {str(e)}"

def type_text(text: str) -> str:
    """Mengetik teks"""
    try:
        status.add_log(f"Typing text: {text[:50]}...")
        pyautogui.write(text, interval=0.05)
        return f"Typed: {text}"
    except Exception as e:
        return f"Type error: {str(e)}"

def press_key(key: str) -> str:
    """Menekan tombol keyboard"""
    try:
        status.add_log(f"Pressing key: {key}")
        pyautogui.press(key)
        return f"Pressed {key}"
    except Exception as e:
        return f"Key press error: {str(e)}"

def get_system_info() -> Dict[str, Any]:
    """Dapatkan informasi sistem"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        info = {
            "cpu_usage": f"{cpu_percent}%",
            "memory_usage": f"{memory.percent}%",
            "disk_usage": f"{disk.percent}%",
            "battery": "N/A (Desktop)",
            "active_apps": status.get_active_apps()
        }
        return info
    except Exception as e:
        return {"error": str(e)}

def search_web(query: str) -> str:
    """Mencari di web (membuka browser)"""
    try:
        import webbrowser
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        status.add_log(f"Web search: {query}")
        return f"Searching for: {query}"
    except Exception as e:
        return f"Search error: {str(e)}"

def set_volume(level: int) -> str:
    """Mengatur volume sistem"""
    try:
        level = max(0, min(100, level))
        subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{level}%'])
        status.add_log(f"Volume set to {level}%")
        return f"Volume set to {level}%"
    except Exception as e:
        return f"Volume control error: {str(e)}"

def take_screenshot() -> str:
    """Mengambil screenshot"""
    try:
        filename = f"/tmp/jarvis_screenshot_{int(time.time())}.png"
        pyautogui.screenshot(filename)
        status.add_log(f"Screenshot taken: {filename}")
        return f"Screenshot saved to {filename}"
    except Exception as e:
        return f"Screenshot error: {str(e)}"

# Daftar tools untuk OpenAI
tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_terminal_command",
            "description": "Execute a terminal command on Ubuntu system",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The terminal command to execute"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Open an application on Ubuntu (firefox, chrome, terminal, files, gedit, vscode, calculator, settings, music, camera)",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the application to open"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_application",
            "description": "Close an application by name",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the application to close"}
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "control_mouse",
            "description": "Control mouse actions (click, double_click, move, scroll_up, scroll_down)",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["click", "double_click", "move", "scroll_up", "scroll_down"]},
                    "x": {"type": "integer", "description": "X coordinate (only for move action)"},
                    "y": {"type": "integer", "description": "Y coordinate (only for move action)"}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type text using keyboard",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to type"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": "Press a keyboard key (enter, space, tab, escape, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Key to press"}
                },
                "required": ["key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Get current system information (CPU, memory, disk, active apps)",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web using Google",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Set system volume (0-100)",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "integer", "description": "Volume level (0-100)"}
                },
                "required": ["level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Take a screenshot of the current screen",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

available_functions = {
    "execute_terminal_command": execute_terminal_command,
    "open_application": open_application,
    "close_application": close_application,
    "control_mouse": control_mouse,
    "type_text": type_text,
    "press_key": press_key,
    "get_system_info": get_system_info,
    "search_web": search_web,
    "set_volume": set_volume,
    "take_screenshot": take_screenshot,
}

def speak_text(text: str):
    """Convert text to speech"""
    try:
        status.is_speaking = True
        engine.say(text)
        engine.runAndWait()
        status.is_speaking = False
    except Exception as e:
        print(f"Speech error: {e}")
        status.is_speaking = False

async def process_with_ai(user_input: str) -> Dict[str, Any]:
    """Proses input pengguna menggunakan OpenAI"""
    try:
        messages = [
            {"role": "system", "content": "You are JARVIS, an advanced AI assistant for Ubuntu desktop. You can control the entire system. Be concise and helpful. When you need to perform an action, use the available tools. Respond in the same language as the user."},
            {"role": "user", "content": user_input}
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        results = []
        final_response = ""
        
        if tool_calls:
            messages.append(response_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                status.add_log(f"Calling function: {function_name}")
                
                if function_name in available_functions:
                    function_result = available_functions[function_name](**function_args)
                    results.append({"function": function_name, "result": function_result})
                    
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_result),
                    })
            
            # Get final response after tool execution
            second_response = openai.ChatCompletion.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.7
            )
            final_response = second_response.choices[0].message.content
        else:
            final_response = response_message.content
        
        return {
            "success": True,
            "response": final_response,
            "actions_taken": results,
            "logs": status.logs[-5:]
        }
    
    except Exception as e:
        error_msg = f"AI processing error: {str(e)}"
        status.add_log(error_msg, "ERROR")
        return {
            "success": False,
            "response": "Maaf, terjadi kesalahan saat memproses perintah Anda.",
            "error": str(e)
        }

# WebSocket untuk komunikasi real-time dengan frontend
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    status.add_log("Client connected to WebSocket")
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "voice_command":
                # Proses perintah suara
                text = data.get("text", "")
                status.add_log(f"Voice command received: {text}")
                
                result = await process_with_ai(text)
                
                # Kirim respons ke frontend
                await websocket.send_json(result)
                
                # Speak response jika ada
                if result["success"] and result["response"]:
                    threading.Thread(target=speak_text, args=(result["response"],)).start()
            
            elif data.get("type") == "text_command":
                # Proses perintah teks
                text = data.get("text", "")
                result = await process_with_ai(text)
                await websocket.send_json(result)
                
                if result["success"] and result["response"]:
                    threading.Thread(target=speak_text, args=(result["response"],)).start()
            
            elif data.get("type") == "get_status":
                # Kirim status sistem
                await websocket.send_json({
                    "type": "status",
                    "is_listening": status.is_listening,
                    "is_speaking": status.is_speaking,
                    "current_task": status.current_task,
                    "logs": status.logs[-10:],
                    "active_apps": status.get_active_apps()
                })
    
    except WebSocketDisconnect:
        status.add_log("Client disconnected")
    except Exception as e:
        status.add_log(f"WebSocket error: {str(e)}", "ERROR")

@app.get("/api/status")
async def get_status():
    return {
        "is_listening": status.is_listening,
        "is_speaking": status.is_speaking,
        "logs": status.logs[-20:],
        "active_apps": status.get_active_apps(),
        "system_info": get_system_info()
    }

@app.get("/api/logs")
async def get_logs():
    return {"logs": status.logs}

if __name__ == "__main__":
    import uvicorn
    print("🚀 JARVIS Backend starting...")
    print(f"📡 API Key configured: {'Yes' if OPENAI_API_KEY != 'your-api-key-here' else 'No - Please set OPENAI_API_KEY environment variable'}")
    print("🌐 Dashboard will be available at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
