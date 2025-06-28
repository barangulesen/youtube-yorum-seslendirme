import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pytchat
import queue
import webbrowser
from urllib.parse import urlparse, parse_qs
from langdetect import detect
import pyttsx3
# websocket-client için: pip install websocket-client
try:
    from websocket import create_connection
except ImportError:
    create_connection = None
import json
import re

# 🌐 Dil ve ses konfigürasyonları
LANGUAGE_CONFIG = {
    "Turkish": {"code": "tr", "preferred": ["Hazel", "Zira"]},
    "English": {"code": "en", "preferred": ["David", "Zira", "Mark"]},
    "French": {"code": "fr", "preferred": []},
    "German": {"code": "de", "preferred": []},
    "Spanish": {"code": "es", "preferred": []},
    "Italian": {"code": "it", "preferred": []},
}

# 🔍 Spam/Yinelenen/Emoji filtresi
FILTER_PATTERNS = [
    r"[:;=xX]-?[)D3]",
    r"<3",
    r"\b(lol|xd|haha|heh)\b",
    r"[❤🔥💀🌟😅😂🤣😭😍😎👀👍]+",
    r":[^\s:]+:",
]

OBS_DEFAULT_URL = "ws://127.0.0.1:4444"
OBS_DEFAULT_PASSWORD = ""

# TTS motoru
engine = pyttsx3.init()

def get_voice_by_language(lang_name):
    cfg = LANGUAGE_CONFIG.get(lang_name, {})
    prefs = cfg.get("preferred", [])
    voices = engine.getProperty('voices')
    for pref in prefs:
        for v in voices:
            if pref.lower() in v.name.lower():
                return v.id
    code = cfg.get("code", "en")
    for v in voices:
        if code in v.id.lower() or code in v.name.lower():
            return v.id
    return None

def extract_video_id(url):
    try:
        p = urlparse(url)
        if p.hostname and 'youtube.com' in p.hostname:
            return parse_qs(p.query).get('v', [None])[0]
        if p.hostname == 'youtu.be':
            return p.path.lstrip('/')
    except:
        return None

def is_message_spam(msg):
    txt = msg.strip().lower()
    if len(txt) < 3:
        return True
    for patt in FILTER_PATTERNS:
        if re.search(patt, txt):
            return True
    return False

def say_text(msg, voice_id, speed):
    try:
        spd = max(50, min(600, int(float(speed))))
    except:
        spd = 200
    engine.setProperty('rate', spd)
    if voice_id:
        engine.setProperty('voice', voice_id)
    engine.say(msg)
    engine.runAndWait()

def open_requirements():
    webbrowser.open('https://pypi.org/project/pytchat/')

class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('🔊 Youtube Yorumları Seslendirici (Windows)')
        self.configure(bg='#0D0D12')

        # Dinamik boyut: ekranın %80'i
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w, h = int(sw * 0.8), int(sh * 0.8)
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self.minsize(600, 400)

        # Stil
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TLabel', background='#0D0D12', foreground='#00FFD6', font=('Segoe UI', 12))
        style.configure('TEntry', fieldbackground='#1F1F24', foreground='#F0F0F0', font=('Consolas', 11))
        style.configure('TButton', background='#00FFD6', foreground='#0D0D12', font=('Segoe UI', 12, 'bold'), padding=6)
        style.map('TButton', background=[('active', '#00E6C2')])
        style.configure('TCheckbutton', background='#0D0D12', foreground='#00FFD6', font=('Segoe UI', 12))
        style.configure('TScale', troughcolor='#1F1F24', background='#00FFD6')

        # Üst: Ayarlar
        top = ttk.LabelFrame(self, text='⚙️ Ayarlar', padding=10)
        top.pack(fill='x', padx=10, pady=10)
        for i in range(3):
            top.columnconfigure(i, weight=1)

        ttk.Label(top, text='Dil:').grid(row=0, column=0, sticky='w')
        self.lang = tk.StringVar(master=self, value='Turkish')
        ttk.Combobox(top, textvariable=self.lang, values=list(LANGUAGE_CONFIG.keys()), state='readonly').grid(row=0, column=1, sticky='ew', padx=5)

        self.auto = tk.BooleanVar(master=self, value=False)
        ttk.Checkbutton(top, text='Otomatik Algıla', variable=self.auto).grid(row=0, column=2, sticky='w')

        ttk.Label(top, text='Hız:').grid(row=1, column=0, sticky='w', pady=5)
        self.speed = tk.IntVar(master=self, value=200)
        ttk.Scale(top, from_=50, to=600, variable=self.speed, orient='horizontal').grid(row=1, column=1, columnspan=2, sticky='ew')

        self.theatre = tk.BooleanVar(master=self, value=False)
        ttk.Checkbutton(top, text='🎭 Tiyatro Modu', variable=self.theatre).grid(row=2, column=0, pady=5)

        ttk.Label(top, text='Beyaz Liste:').grid(row=3, column=0, sticky='w')
        self.whitelist = ttk.Entry(top)
        self.whitelist.grid(row=3, column=1, columnspan=2, sticky='ew', pady=2)

        ttk.Label(top, text='Kara Liste:').grid(row=4, column=0, sticky='w')
        self.blacklist = ttk.Entry(top)
        self.blacklist.grid(row=4, column=1, columnspan=2, sticky='ew', pady=2)

        ttk.Label(top, text='YouTube Link:').grid(row=5, column=0, sticky='w', pady=5)
        self.link = ttk.Entry(top)
        self.link.grid(row=5, column=1, columnspan=2, sticky='ew', pady=2)

        ttk.Button(top, text='📦 Gereksinimler', command=open_requirements).grid(row=6, column=1, pady=5)

        # Kontroller
        ctrl = ttk.Frame(self)
        ctrl.pack(fill='x', padx=10, pady=5)
        ctrl.columnconfigure((0,1), weight=1)
        self.start_btn = ttk.Button(ctrl, text='▶️ Başlat', command=self.start)
        self.start_btn.grid(row=0, column=0, sticky='ew', padx=5)
        self.stop_btn = ttk.Button(ctrl, text='⏹️ Durdur', command=self.stop, state='disabled')
        self.stop_btn.grid(row=0, column=1, sticky='ew', padx=5)

        # Alt: Log & OBS
        bottom = ttk.LabelFrame(self, text='📜 Log & OBS', padding=10)
        bottom.pack(fill='both', expand=True, padx=10, pady=10)
        bottom.rowconfigure(0, weight=1)
        bottom.columnconfigure(0, weight=1)

        self.text = tk.Text(bottom, bg='#1E1E22', fg='#00FFD6', font=('Consolas', 11))
        self.text.grid(row=0, column=0, sticky='nsew')

        obsfrm = ttk.Frame(bottom)
        obsfrm.grid(row=1, column=0, sticky='ew', pady=5)
        obsfrm.columnconfigure((1,3), weight=1)
        ttk.Label(obsfrm, text='OBS URL:').grid(row=0, column=0, sticky='w')
        self.obs_url = ttk.Entry(obsfrm)
        self.obs_url.insert(0, OBS_DEFAULT_URL)
        self.obs_url.grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Label(obsfrm, text='Parola:').grid(row=0, column=2, sticky='w')
        self.obs_pass = ttk.Entry(obsfrm, show='*')
        self.obs_pass.insert(0, OBS_DEFAULT_PASSWORD)
        self.obs_pass.grid(row=0, column=3, sticky='ew', padx=5)
        ttk.Button(obsfrm, text='🎬 Başlat', command=self.obs_start).grid(row=1, column=1, pady=5)
        ttk.Button(obsfrm, text='⏸️ Durdur', command=self.obs_stop).grid(row=1, column=2, pady=5)

        # Thread & state
        self.chat = None
        self.running = False
        self.last = {}
        self.q = queue.Queue()
        threading.Thread(target=self.voice_worker, daemon=True).start()

    def obs_start(self):
        if create_connection is None:
            messagebox.showerror('Hata', 'websocket-client kurulmalı!')
            return
        try:
            self.ws = create_connection(self.obs_url.get(), timeout=5)
            self.ws.send(json.dumps({'request-type':'StartRecording','message-id':'1'}))
            self.text.insert('end', '🔴 OBS kayıt başladı\n')
            self.text.see('end')
        except Exception as e:
            messagebox.showerror('OBS Hata', str(e))

    def obs_stop(self):
        if getattr(self, 'ws', None):
            self.ws.send(json.dumps({'request-type':'StopRecording','message-id':'2'}))
            self.text.insert('end', '⏸️ OBS kayıt durduruldu\n')
            self.text.see('end')

    def start(self):
        vid = extract_video_id(self.link.get())
        if not vid:
            messagebox.showerror('Hata', 'Geçerli link girin')
            return
        self.settings = {
            'lang': self.lang.get(),
            'auto': self.auto.get(),
            'speed': self.speed.get(),
            'theatre': self.theatre.get(),
            'wl': [u.strip() for u in self.whitelist.get().split(',') if u.strip()],
            'bl': [u.strip() for u in self.blacklist.get().split(',') if u.strip()],
        }
        self.voice_def = get_voice_by_language(self.settings['lang'])
        self.chat = pytchat.create(video_id=vid)
        self.running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        threading.Thread(target=self.read_loop, daemon=True).start()
        self.text.insert('end', f"▶️ Chat başladı: {self.settings['lang']} hız={self.settings['speed']}\n")
        self.text.see('end')

    def stop(self):
        self.running = False
        if self.chat:
            self.chat.terminate()
        self.q.put((None, None, None))
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.text.insert('end', '⏹️ Chat durduruldu\n')
        self.text.see('end')

    def read_loop(self):
        while self.running and self.chat.is_alive():
            for c in self.chat.get().sync_items():
                u, r = c.author.name, c.message.strip()
                if u in self.settings['bl'] or is_message_spam(r):
                    continue
                if self.settings['theatre'] and u not in self.settings['wl']:
                    continue
                lang = detect(r) if self.settings['auto'] else self.settings['lang']
                v = get_voice_by_language(lang) or self.voice_def
                msg = f"{u}: {r}"
                if self.last.get(u) == msg:
                    continue
                self.last[u] = msg
                self.text.insert('end', msg + '\n')
                self.text.see('end')
                self.q.put((msg, v, self.settings['speed']))
                time.sleep(0.05)

    def voice_worker(self):
        while True:
            item = self.q.get()
            if item == (None, None, None):
                break
            msg, v, spd = item
            try:
                say_text(msg, v, spd)
            except Exception as e:
                print("[HATA] say_text sırasında:", e)
            finally:
                self.q.task_done()

if __name__ == '__main__':
    ChatApp().mainloop()
