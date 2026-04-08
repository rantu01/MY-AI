import speech_recognition as sr
import os
import requests
import webbrowser
from config import GOOGLE_API_KEY
import datetime
import random
import numpy as np
import shutdown
import tempfile
import sys
import base64
import subprocess
import time

# ── gTTS ──
try:
    from gtts import gTTS
    _has_gtts = True
except Exception:
    _has_gtts = False

# ── pygame mixer (সবচেয়ে reliable audio player) ──
try:
    import pygame
    pygame.mixer.init()
    _has_pygame = True
except Exception:
    _has_pygame = False

chatStr = ""

# ─────────────────────────────────────────────
# বাংলা কমান্ড ম্যাপিং
# ─────────────────────────────────────────────
BANGLA_SITES = [
    # (বাংলা কীওয়ার্ড তালিকা,  ইংরেজি নাম,  URL)
    (["ইউটিউব", "youtube", "ইউটিউব খোলো", "ইউটিউব খুলো", "open youtube"], "ইউটিউব", "https://www.youtube.com"),
    (["উইকিপিডিয়া", "wikipedia", "উইকিপিডিয়া খোলো", "উইকিপিডিয়া খুলো", "open wikipedia"], "উইকিপিডিয়া", "https://www.wikipedia.com"),
    (["গুগল", "google", "গুগল খোলো", "গুগল খুলো", "open google"], "গুগল", "https://www.google.com"),
    (["ফেসবুক", "facebook", "ফেসবুক খোলো", "ফেসবুক খুলো", "open facebook"], "ফেসবুক", "https://www.facebook.com"),
]

BANGLA_COMMANDS = {
    "time": [
        "সময়", "এখন কয়টা", "কয়টা বাজে", "সময় বলো", "সময় কত",
        "the time", "what time", "time বলো",
    ],
    "music": [
        "মিউজিক চালাও", "গান চালাও", "মিউজিক খোলো", "open music",
    ],
    "shutdown": [
        "বন্ধ করো", "কম্পিউটার বন্ধ", "শাটডাউন", "shutdown", "shut down",
        "কম্পিউটার বন্ধ করো", "পিসি বন্ধ করো",
    ],
    "exit": [
        "বিদায়", "জারভিস বন্ধ", "বন্ধ হও", "jarvis quit", "exit", "যাও",
    ],
    "reset": [
        "চ্যাট রিসেট", "রিসেট করো", "নতুন চ্যাট", "reset chat",
    ],
    "voice_change": [
        "ভয়েস পরিবর্তন", "ভয়েস চেঞ্জ", "গলা বদলাও", "change voice",
        "voice change", "change the voice",
    ],
    "ai_save": [
        "আর্টিফিশিয়াল ইন্টেলিজেন্স", "using artificial intelligence",
    ],
}

WAKE_WORDS = (
    "hello", "হ্যালো", "jervice", "jarvis", "জারভিস",
    "এই জারভিস", "ওহে জারভিস",
)

# ─────────────────────────────────────────────

def _friendly_gemini_error(error):
    err = str(error)
    if "RESOURCE_EXHAUSTED" in err or "quota" in err.lower() or "429" in err:
        return "Gemini quota শেষ হয়ে গেছে। Google billing বা quota চেক করুন।"
    if "API_KEY_INVALID" in err or ("invalid" in err.lower() and "key" in err.lower()):
        return "Gemini API key সঠিক নয়। config.py তে GOOGLE_API_KEY আপডেট করুন।"
    return "এই মুহূর্তে Gemini এর সাথে যোগাযোগ করা যাচ্ছে না। একটু পরে চেষ্টা করুন।"


def _generate_with_gemini(prompt, model=None):
    """Call Google Gemini REST API using an API key with model fallback."""
    if not GOOGLE_API_KEY:
        raise RuntimeError("No GOOGLE_API_KEY configured")

    models_to_try = [model] if model else [
        "gemini-2.0-flash-001",
        "gemini-2.0-flash",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
    ]
    params = {"key": GOOGLE_API_KEY}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 256},
    }

    last_error = None
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        try:
            r = requests.post(url, params=params, json=body, timeout=20)
            if r.status_code == 404:
                last_error = RuntimeError(f"Gemini model not found: {model_name}")
                continue
            r.raise_for_status()
            j = r.json()
            candidates = j.get("candidates", [])
            if not candidates:
                return ""
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                return ""
            return (parts[0].get("text") or "").strip()
        except Exception as e:
            last_error = e
            continue

    if last_error:
        raise last_error
    raise RuntimeError("Gemini request failed")


def chat(query):
    global chatStr
    # Gemini কে বাংলায় উত্তর দিতে বলা হচ্ছে
    system_hint = (
        "তুমি জারভিস, একটি বাংলা AI assistant। "
        "সবসময় বাংলায় উত্তর দাও। সংক্ষিপ্ত ও বন্ধুত্বপূর্ণ থাকো।\n\n"
    )
    chatStr += f"Rantu: {query}\n Jarvis: "
    try:
        text = _generate_with_gemini(system_hint + chatStr)
        if not text:
            text = "কোনো উত্তর পাওয়া যায়নি। আবার চেষ্টা করুন।"
    except Exception as e:
        text = _friendly_gemini_error(e)

    print(f"Jarvis: {text}")
    say(text)
    chatStr += f"{text}\n"
    return text


def ai(prompt):
    text = f"Gemini response for Prompt: {prompt} \n *************************\n\n"
    try:
        text += _generate_with_gemini(prompt)
    except Exception as e:
        text += _friendly_gemini_error(e)

    if not os.path.exists("Openai"):
        os.mkdir("Openai")

    filename = prompt.lower().split('artificial intelligence')[-1].strip()
    if not filename:
        filename = f"ai_response_{random.randint(1, 1000)}"

    safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '_', '-')).strip()
    if not safe_filename:
        safe_filename = f"ai_response_{random.randint(1, 1000)}"

    with open(f"Openai/{safe_filename}.txt", "w", encoding="utf-8") as f:
        f.write(text)
    say("AI এর উত্তর ফাইলে সেভ করা হয়েছে।")


# ─── TTS Setup ───────────────────────────────
try:
    import pyttsx3
    _tts_engine = pyttsx3.init()
except Exception:
    _tts_engine = None

tts_settings = {
    "lang": "bn",
    "pyttsx3_voice_id": None,
}


def _play_gtts_pygame(text, lang="bn"):
    """gTTS দিয়ে MP3 বানাও, pygame দিয়ে বাজাও — সবচেয়ে reliable"""
    if not _has_gtts or not _has_pygame:
        return False
    path = None
    try:
        tts = gTTS(text=text, lang=lang)
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        tts.save(path)

        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        # শেষ হওয়া পর্যন্ত অপেক্ষা করো
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.unload()
        return True
    except Exception as e:
        print(f"[say] pygame/gTTS error: {e}")
        return False
    finally:
        if path:
            try:
                os.remove(path)
            except Exception:
                pass


def say(text):
    print(f"[Jarvis]: {text}")  # সবসময় terminal এ দেখাবে

    # ── পদ্ধতি ১: gTTS + pygame (বাংলার জন্য সেরা) ──
    if _has_gtts and _has_pygame:
        ok = _play_gtts_pygame(text, lang=tts_settings.get("lang", "bn"))
        if ok:
            return

    # ── পদ্ধতি ২: pyttsx3 ──
    if _tts_engine:
        try:
            vid = tts_settings.get("pyttsx3_voice_id")
            if vid:
                try:
                    _tts_engine.setProperty('voice', vid)
                except Exception:
                    pass
            _tts_engine.say(text)
            _tts_engine.runAndWait()
            return
        except Exception as e:
            print(f"[say] pyttsx3 error: {e}")

    # ── পদ্ধতি ৩: Windows PowerShell TTS (English only fallback) ──
    if os.name == 'nt':
        try:
            ps_script = (
                "Add-Type -AssemblyName System.speech; "
                "$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                "$speak.Speak(@'\n" + text + "\n'@)"
            )
            encoded = base64.b64encode(ps_script.encode('utf-16-le')).decode('ascii')
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded],
                check=False,
            )
        except Exception as e:
            print(f"[say] PowerShell TTS error: {e}")
    else:
        try:
            subprocess.run(["say", text], check=False)
        except Exception:
            pass


def select_voice_interactive():
    print("Voice change options:\n1) Bangla (gTTS)\n2) pyttsx3 English\n3) pyttsx3 voice list")
    say("ভয়েস পরিবর্তনের মেনু খুলছে। নম্বর বলে বা টাইপ করে বেছে নিন।")
    choice = input("Select option (1-3): ")
    if choice.strip() == '1':
        if not _has_gtts:
            say("gTTS ইনস্টল নেই। আগের সেটিং রইলো।")
            return
        tts_settings['engine'] = 'gtts'
        tts_settings['lang'] = 'bn'
        say("এখন থেকে বাংলায় কথা বলব।")
        print("Set to gTTS Bangla")
        return
    if choice.strip() == '2':
        if _tts_engine:
            tts_settings['engine'] = 'pyttsx3'
            tts_settings['lang'] = 'en'
            say("Voice engine pyttsx3 set kora holo.")
            print("Set to pyttsx3 (default voice)")
        else:
            say("pyttsx3 ইনস্টল নেই।")
        return
    if choice.strip() == '3':
        if not _tts_engine:
            say("pyttsx3 ইনস্টল নেই।")
            return
        voices = _tts_engine.getProperty('voices')
        for i, v in enumerate(voices):
            print(f"{i}: {v.name} - {v.id}")
        idx = input("Enter voice index: ")
        try:
            idxn = int(idx.strip())
            vid = voices[idxn].id
            tts_settings['engine'] = 'pyttsx3'
            tts_settings['pyttsx3_voice_id'] = vid
            say("ভয়েস সেট করা হয়েছে।")
            print(f"Selected voice {voices[idxn].name}")
        except Exception:
            say("ভুল সিলেকশন।")


# ─── Speech Recognition ──────────────────────

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 0.8
        print("Listening...")
        audio = r.listen(source)
        try:
            print("Recognizing...")
            try:
                query = r.recognize_google(audio, language="bn-BD")
            except Exception:
                query = r.recognize_google(audio, language="en-IN")
            print(f"User said: {query}")
            return query
        except Exception:
            return "None"


def takeCommand_timed(timeout=5, phrase_time_limit=4):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 0.8
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            try:
                query = r.recognize_google(audio, language="bn-BD")
            except Exception:
                try:
                    query = r.recognize_google(audio, language="en-IN")
                except Exception:
                    return ""
            print(f"(timed) User said: {query}")
            return query
        except Exception:
            return ""


# ─── Command Matching Helpers ─────────────────

def _contains_any(text, keywords):
    """Return True if any keyword is a substring of text."""
    t = text.lower()
    for kw in keywords:
        if kw.lower() in t:
            return True
    return False


def _match_site(query):
    """Return (display_name, url) if a site open command is matched, else None."""
    for keywords, name, url in BANGLA_SITES:
        if _contains_any(query, keywords):
            return name, url
    return None


def _match_command(query, cmd_key):
    return _contains_any(query, BANGLA_COMMANDS[cmd_key])


# ─── Main Loop ───────────────────────────────

if __name__ == '__main__':
    print('Welcome to Jarvis A.I')
    say("জারভিস AI চালু হয়েছে। রুন্টু স্যার, আমি প্রস্তুত।")

    SLEEP_AFTER_SECONDS = 12

    while True:
        print("Waiting for wake word...")
        heard = takeCommand_timed(timeout=6, phrase_time_limit=4)
        if not heard:
            continue

        heard_l = heard.lower()
        if not any(w.lower() in heard_l for w in WAKE_WORDS):
            continue

        # ── Wake word detected ──
        say("হ্যাঁ স্যার, বলুন।")
        cmd = takeCommand_timed(timeout=10, phrase_time_limit=8)
        if not cmd:
            say("কিছু শুনতে পাইনি। আবার ডাকুন।")
            continue

        query = cmd  # keep original case for display; use .lower() only for matching
        query_l = query.lower()

        # 1) সাইট খোলার কমান্ড
        site_match = _match_site(query_l)
        if site_match:
            name, url = site_match
            say(f"{name} খোলা হচ্ছে স্যার।")
            print(f"Opening {name}: {url}")
            webbrowser.open(url)
            continue

        # 2) মিউজিক
        if _match_command(query_l, "music"):
            musicPath = "/Users/harry/Downloads/downfall-21371.mp3"
            say("মিউজিক চালু করছি স্যার।")
            os.system(f"open \"{musicPath}\"")
            continue

        # 3) সময়
        if _match_command(query_l, "time"):
            now = datetime.datetime.now()
            hour = now.strftime("%H")
            minute = now.strftime("%M")
            say(f"স্যার, এখন {hour} টা বেজে {minute} মিনিট।")
            continue

        # 4) শাটডাউন
        if _match_command(query_l, "shutdown"):
            say("খোলা ট্যাব বন্ধ করে কম্পিউটার শাটডাউন করছি।")
            try:
                shutdown.close_and_shutdown(say_func=say, delay=5)
            except Exception:
                pass
            exit()

        # 5) জারভিস বন্ধ
        if _match_command(query_l, "exit"):
            say("ঠিক আছে স্যার, বিদায়!")
            exit()

        # 6) চ্যাট রিসেট
        if _match_command(query_l, "reset"):
            chatStr = ""
            say("চ্যাট হিস্ট্রি রিসেট করা হয়েছে।")
            continue

        # 7) ভয়েস পরিবর্তন
        if _match_command(query_l, "voice_change"):
            select_voice_interactive()
            continue

        # 8) AI ফাইলে সেভ
        if _match_command(query_l, "ai_save"):
            ai(prompt=query)
            continue

        # 9) Default → chat with Gemini (বাংলায়)
        print("Chatting...")
        chat(query)