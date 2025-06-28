import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import pytchat
import queue
import webbrowser
from urllib.parse import urlparse, parse_qs

# 🌐 Dil kodları ve önerilen kaliteli sesler
LANGUAGE_CONFIG = {
    "Turkish": {"code": "tr", "preferred": ["Yelda"]},
    "English": {"code": "en", "preferred": ["Daniel", "Samantha", "Alex"]},
    "French": {"code": "fr", "preferred": ["Thomas", "Amelie"]},
    "German": {"code": "de", "preferred": ["Anna", "Markus"]},
    "Spanish": {"code": "es", "preferred": ["Jorge", "Monica"]},
    "Italian": {"code": "it", "preferred": ["Alice", "Luca"]},
}

def get_voice_by_language(lang_name):
    config = LANGUAGE_CONFIG.get(lang_name)
    if not config:
        return None

    lang_code = config["code"]
    preferred_voices = config["preferred"]

    try:
        output = subprocess.check_output(['say', '-v', '?'], text=True)

        for voice in preferred_voices:
            if voice in output:
                return voice

        enhanced = None
        standard = None
        for line in output.splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            name = parts[0]
            lang = parts[1].lower()
            if lang.startswith(lang_code):
                if 'enhanced' in line.lower():
                    enhanced = name
                elif not standard:
                    standard = name
        return enhanced or standard
    except Exception as e:
        print("Ses tespiti başarısız:", e)
        return None

def extract_video_id(url):
    try:
        parsed = urlparse(url)
        if parsed.hostname in ["www.youtube.com", "youtube.com"]:
            query = parse_qs(parsed.query)
            return query.get("v", [None])[0]
        elif parsed.hostname in ["youtu.be"]:
            return parsed.path[1:]
    except:
        return None

def say_text(text, voice):
    safe = text.replace('"', '\\"')
    cmd = ['say', '-v', voice, safe] if voice else ['say', safe]
    subprocess.run(cmd)

def open_requirements_help():
    webbrowser.open("https://pypi.org/project/pytchat/")

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎙️ YouTube Canlı Sohbet Seslendirici")
        self.root.geometry("620x520")
        self.root.configure(bg="#0f0f1a")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Cyber.TButton",
                        font=("Courier New", 12, "bold"),
                        foreground="white",
                        background="#00FF99",
                        borderwidth=1)

        # 🔤 Dil seçimi
        tk.Label(root, text="🌍 Dil Seçin:", font=("Courier", 12), bg="#0f0f1a", fg="#00FF99").pack(pady=5)
        self.lang_var = tk.StringVar(value="Turkish")
        self.lang_menu = ttk.Combobox(root, textvariable=self.lang_var, values=list(LANGUAGE_CONFIG.keys()), state="readonly")
        self.lang_menu.pack()

        # 🔗 Video link girişi
        tk.Label(root, text="🎥 YouTube Canlı Yayın Linki:", font=("Courier", 12), bg="#0f0f1a", fg="#00FF99").pack(pady=5)
        self.link_entry = ttk.Entry(root, width=55)
        self.link_entry.pack(pady=5)

        self.install_btn = ttk.Button(root, text="📦 Gereksinimleri Yükle", command=open_requirements_help, style="Cyber.TButton")
        self.install_btn.pack(pady=5)

        self.start_btn = ttk.Button(root, text="▶️ Başlat", command=self.start_chat, style="Cyber.TButton")
        self.start_btn.pack(pady=5)

        self.stop_btn = ttk.Button(root, text="⏹️ Durdur", command=self.stop_chat, style="Cyber.TButton", state="disabled")
        self.stop_btn.pack(pady=5)

        self.text_area = tk.Text(root, height=15, width=70, bg="#1a1a2e", fg="#39ff14", font=("Courier", 10), insertbackground="#39ff14")
        self.text_area.pack(pady=10)

        self.chat = None
        self.running = False

        # 🎵 Ses kuyruğu ve işleyici thread
        self.voice_queue = queue.Queue()
        self.voice_thread = threading.Thread(target=self.voice_worker, daemon=True)
        self.voice_thread.start()

    def start_chat(self):
        link = self.link_entry.get().strip()
        lang_name = self.lang_var.get()

        video_id = extract_video_id(link)
        if not video_id:
            messagebox.showerror("Hata", "Geçerli bir YouTube canlı yayın linki giriniz.")
            return

        self.voice = get_voice_by_language(lang_name)
        if not self.voice:
            messagebox.showwarning("Ses Yok", f"{lang_name} dili için ses bulunamadı. Sistem sesi kullanılacak.")

        self.chat = pytchat.create(video_id=video_id)
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        threading.Thread(target=self.chat_loop, daemon=True).start()

    def stop_chat(self):
        self.running = False
        if self.chat:
            self.chat.terminate()
        self.voice_queue.put(None)  # Thread’i durdurmak için sinyal
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.text_area.insert(tk.END, "⏹️ Yayın durduruldu.\n")

    def chat_loop(self):
        self.text_area.insert(tk.END, f"🎧 Yayın başladı ({self.voice})\n")
        while self.running and self.chat.is_alive():
            for c in self.chat.get().sync_items():
                msg = f"{c.author.name}: {c.message}"
                self.text_area.insert(tk.END, msg + "\n")
                self.text_area.see(tk.END)
                self.voice_queue.put(msg)
                time.sleep(0.1)

    def voice_worker(self):
        while True:
            msg = self.voice_queue.get()
            if msg is None:
                break
            say_text(msg, self.voice)
            self.voice_queue.task_done()

# 🧠 Ana uygulama
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
