import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import pywhatkit
import os

# Inisialisasi mesin suara
engine = pyttsx3.init('sapi5') # sapi5 untuk Windows, 'nsss' untuk Mac
voices = engine.getProperty('voices')
# Mengatur suara (0 biasanya laki-laki, 1 perempuan)
engine.setProperty('voice', voices[0].id) 
engine.setProperty('rate', 190) # Kecepatan bicara

def speak(text):
    """Fungsi untuk mengubah teks menjadi suara"""
    print(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()

def take_command():
    """Mendengarkan input suara dari mikrofon"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Mendengarkan...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Mengenali suara...")
        query = r.recognize_google(audio, language='en-in') # Menggunakan Google Speech API
        print(f"User: {query}\n")
    except Exception as e:
        print("Maaf, bisa ulangi?")
        return "None"
    return query.lower()

def wish_me():
    """Sapaan awal berdasarkan waktu"""
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning Sir!")
    elif 12 <= hour < 18:
        speak("Good Afternoon Sir!")
    else:
        speak("Good Evening Sir!")
    
    speak("I am your personal assistant. How may I help you?")

if __name__ == "__main__":
    wish_me()
    
    while True:
        query = take_command()

        # Logika perintah
        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            try:
                results = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia")
                speak(results)
            except:
                speak("I couldn't find any results on Wikipedia.")

        elif 'open youtube' in query:
            speak("Opening YouTube")
            pywhatkit.playonyt(query.replace("open youtube", ""))
            
        elif 'time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {strTime}")

        elif 'open code' in query:
            codePath = "code" # Pastikan VS Code sudah ada di PATH sistem
            speak("Opening Visual Studio Code")
            os.startfile(codePath) # Hanya berlaku di Windows
            
        elif 'exit' in query or 'quit' in query:
            speak("Goodbye Sir. Shutting down.")
            break
        
        elif query != "none":
            # Respon default jika perintah tidak dikenali
            speak("I am not sure how to help with that yet, but I am listening.")
