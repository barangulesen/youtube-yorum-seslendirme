import os
import subprocess
import threading
import time
import queue
import json
import re
import webbrowser
from urllib.parse import urlparse, parse_qs

import pytchat
from langdetect import detect
from websocket import create_connection

from ttkbootstrap import Style
import ttkbootstrap as tb
from tkinter import messagebox

# --- Requirements ---
# pip install pytchat openai python-dotenv pydub pyttsx3 langdetect websocket-client ttkbootstrap

# 🌐 Dil ve ses konfigürasyonları
LANGUAGE_CONFIG = {
    "Turkish": {"code": "tr", "preferred": ["Cem", "Yelda"]},
    "English": {"code": "en", "preferred": ["Daniel", "Samantha", "Alex"]},
    "French": {"code": "fr", "preferred": ["Thomas", "Amelie"]},
    "German": {"code": "de", "preferred": ["Anna", "Markus"]},
    "Spanish": {"code": "es", "preferred": ["Jorge", "Monica"]},
    "Italian": {"code": "it", "preferred": ["Alice", "Luca"]},
}

# 🔍 Spam/Yinelenen/Emoji filtresi
FILTER_PATTERNS = [
    r"[:;=xX]-?[)D3]", r"<3", r"\b(lol|xd|haha|heh)\b",
    r"[❤🔥💀🌟😅😂🤣😭😍😎👀👍]+", r":[^\s:]+:"
]

OBS_DEFAULT_URL = "ws://127.0.0.1:4444"
OBS_DEFAULT_PASSWORD = ""

# ---- Yardımcı Fonksiyonlar ----
def get_voice_by_language(lang_name):
    cfg = LANGUAGE_CONFIG.get(lang_name, {})
    code, prefs = cfg.get("code", "en"), cfg.get("preferred", [])
    try:
        out = subprocess.check_output(["say", "-v", "?"], text=True)
        for v in prefs:
            if v in out:
                return v
        enh = std = None
        for ln in out.splitlines():
            parts = ln.split()
            if len(parts) < 2: continue
            name, lang = parts[0], parts[1].lower()
            if lang.startswith(code):
                if "enhanced" in ln.lower(): enh = name
                elif not std: std = name
        return enh or std
    except:
        return None

def extract_video_id(url):
    try:
        p = urlparse(url)
        if p.hostname and "youtube.com" in p.hostname:
            return parse_qs(p.query).get("v", [None])[0]
        if p.hostname == "youtu.be":
            return p.path.lstrip("/")
    except:
        pass
    return None

def is_message_spam(msg):
    txt = msg.strip().lower()
    if len(txt) < 3: return True
    return any(re.search(p, txt) for p in FILTER_PATTERNS)

def say_text(msg, voice, speed):
    try:
        spd = max(50, min(600, int(speed)))
    except:
        spd = 200
    safe = msg.replace('"', '\\"')
    cmd = ["say"]
    if voice:
        cmd += ["-v", voice]
    cmd += ["-r", str(spd), safe]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print(f"[HATA] say hatası hız={spd}")

def open_requirements():
    webbrowser.open("https://pypi.org/project/pytchat/")

# ---- Uygulama ----
class ChatApp(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("🔊 Youtube Yorumları Seslendirici")
        self.geometry("850x780")

        # Ayarlar bölümü
        frm = tb.Labelframe(self, text="⚙️ Ayarlar", padding=20)
        frm.pack(fill="x", padx=20, pady=(20,10))

        tb.Label(frm, text="Dil:").grid(row=0, column=0, sticky="w")
        self.lang = tb.StringVar(value="Turkish")
        tb.Combobox(frm, textvariable=self.lang, values=list(LANGUAGE_CONFIG), width=18).grid(row=0, column=1, padx=10)

        self.auto = tb.BooleanVar(value=False)
        tb.Checkbutton(frm, text="Otomatik Algıla", variable=self.auto).grid(row=0, column=2, padx=10)

        tb.Label(frm, text="Hız (50–600):").grid(row=1, column=0, sticky="w", pady=8)
        self.speed = tb.IntVar(value=200)
        tb.Scale(frm, from_=50, to=600, variable=self.speed, orient="horizontal", length=400).grid(row=1, column=1, columnspan=2)

        self.theatre = tb.BooleanVar(value=False)
        tb.Checkbutton(frm, text="🎭 Tiyatro Modu", variable=self.theatre).grid(row=2, column=0, pady=8)

        tb.Label(frm, text="Beyaz Liste (comma):").grid(row=3, column=0, sticky="w")
        self.whitelist = tb.Entry(frm, width=50)
        self.whitelist.grid(row=3, column=1, columnspan=2, pady=5)

        tb.Label(frm, text="Kara Liste (comma):").grid(row=4, column=0, sticky="w")
        self.blacklist = tb.Entry(frm, width=50)
        self.blacklist.grid(row=4, column=1, columnspan=2, pady=5)

        tb.Label(frm, text="YouTube Link:").grid(row=5, column=0, sticky="w", pady=8)
        self.link = tb.Entry(frm, width=60)
        self.link.grid(row=5, column=1, columnspan=2, pady=5)

        tb.Button(frm, text="📦 Gereksinimler", bootstyle="info-outline", command=open_requirements)\
            .grid(row=6, column=1, pady=12)

        # Başlat / Durdur
        ctrl = tb.Frame(self)
        ctrl.pack(fill="x", pady=(0,10))
        self.start_btn = tb.Button(ctrl, text="▶️ Başlat (Ctrl+S)", bootstyle="success", width=20, command=self.start)
        self.start_btn.pack(side="left", padx=20)
        self.stop_btn = tb.Button(ctrl, text="⏹️ Durdur (Ctrl+E)", bootstyle="danger", width=20,
                                  state="disabled", command=self.stop)
        self.stop_btn.pack(side="left", padx=20)

        # Log & OBS
        logfrm = tb.Labelframe(self, text="📜 Log & OBS", padding=15)
        logfrm.pack(fill="both", expand=True, padx=20, pady=(0,20))
        self.text = tb.Text(logfrm, wrap="word", height=15)
        self.text.pack(fill="both", expand=True)

        obsfrm = tb.Frame(logfrm)
        obsfrm.pack(fill="x", pady=10)
        tb.Label(obsfrm, text="OBS URL:").grid(row=0, column=0, sticky="w")
        self.obs_url = tb.Entry(obsfrm, width=30)
        self.obs_url.insert(0, OBS_DEFAULT_URL)
        self.obs_url.grid(row=0, column=1, padx=5)
        tb.Label(obsfrm, text="Parola:").grid(row=0, column=2, sticky="w")
        self.obs_pass = tb.Entry(obsfrm, width=20, show="*")
        self.obs_pass.insert(0, OBS_DEFAULT_PASSWORD)
        self.obs_pass.grid(row=0, column=3, padx=5)
        tb.Button(obsfrm, text="🎬 Başlat", bootstyle="warning-outline", command=self.obs_start)\
            .grid(row=1, column=1, pady=5)
        tb.Button(obsfrm, text="⏸️ Durdur", bootstyle="warning-outline", command=self.obs_stop)\
            .grid(row=1, column=2)

        # Kısayollar
        self.bind_all("<Control-s>", lambda e: self.start())
        self.bind_all("<Control-e>", lambda e: self.stop())

        # İç durum
        self.chat = None
        self.running = False
        self.last = {}
        self.q = queue.Queue()
        threading.Thread(target=self.voice_worker, daemon=True).start()

    def obs_start(self):
        if create_connection is None:
            messagebox.showerror("Hata", "websocket-client eksik!")
            return
        try:
            ws = create_connection(self.obs_url.get())
            ws.send(json.dumps({"request-type":"StartRecording","message-id":"1"}))
            self.log("🔴 OBS kayıt başladı")
        except Exception as ex:
            messagebox.showerror("OBS Hata", str(ex))

    def obs_stop(self):
        try:
            ws = getattr(self, "ws", None)
            if ws:
                ws.send(json.dumps({"request-type":"StopRecording","message-id":"2"}))
            self.log("⏸️ OBS kayıt durduruldu")
        except:
            pass

    def start(self):
        vid = extract_video_id(self.link.get())
        if not vid:
            messagebox.showerror("Hata", "Geçerli YouTube linki girin!")
            return
        self.settings = {
            "lang": self.lang.get(),
            "auto": self.auto.get(),
            "speed": self.speed.get(),
            "theatre": self.theatre.get(),
            "wl": [u.strip() for u in self.whitelist.get().split(",") if u.strip()],
            "bl": [u.strip() for u in self.blacklist.get().split(",") if u.strip()],
        }
        self.voice_def = get_voice_by_language(self.settings["lang"]) or "Alex"
        self.chat = pytchat.create(video_id=vid)
        self.running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        threading.Thread(target=self.read_loop, daemon=True).start()
        self.log(f"▶️ Chat başladı: {self.settings['lang']} hız={self.settings['speed']}")

    def stop(self):
        self.running = False
        if self.chat:
            self.chat.terminate()
        self.q.put((None,None,None))
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.log("⏹️ Chat durduruldu")

    def read_loop(self):
        while self.running and self.chat.is_alive():
            for c in self.chat.get().sync_items():
                u, r = c.author.name, c.message.strip()
                if u in self.settings["bl"] or is_message_spam(r):
                    continue
                if self.settings["theatre"] and u not in self.settings["wl"]:
                    continue
                lang = detect(r) if self.settings["auto"] else self.settings["lang"]
                v = get_voice_by_language(lang) or self.voice_def
                msg = f"{u}: {r}"
                if self.last.get(u)==msg:
                    continue
                self.last[u] = msg
                self.log(msg)
                self.q.put((msg, v, self.settings["speed"]))
                time.sleep(0.05)

    def voice_worker(self):
        while True:
            item = self.q.get()
            if item==(None,None,None): break
            msg,v,spd = item
            say_text(msg,v,spd)
            self.q.task_done()

    def log(self, txt):
        ts = time.strftime("[%H:%M:%S] ")
        self.text.insert("end", ts+txt+"\n")
        self.text.see("end")

if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()
