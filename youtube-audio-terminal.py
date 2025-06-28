import os
import threading
import subprocess
import pytchat

# 1) MacOS'taki yüklü sesleri kontrol ederek öncelikle "Enhanced" Türkçe sesi seç
#    Ardından standart Türkçe seslere bak

def detect_turkish_voice():
    try:
        output = subprocess.check_output(['say', '-v', '?'], text=True)
        enhanced = None
        standard = None
        for line in output.splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            name = parts[0]
            lang = parts[1]
            if lang.lower().startswith('tr'):
                # Öncelik: Enhanced etiketli
                if 'enhanced' in line.lower():
                    enhanced = name
                elif not standard:
                    standard = name
        # Eğer Enhanced bulunduysa onu kullan
        if enhanced:
            return enhanced
        # Yoksa standart Türkçe varsa onu dön
        if standard:
            return standard
    except Exception:
        pass
    # Hiçbir Türkçe ses yoksa None dön
    return None

TURKISH_VOICE = detect_turkish_voice()
if TURKISH_VOICE:
    print(f"🎤 Türkçe ses detekte edildi: {TURKISH_VOICE}")
else:
    print("⚠️ Türkçe ses bulunamadı, sistem varsayılan sesi kullanılacak.")

# 2) 'say' komutunda eşzamanlılık için kilit
tts_lock = threading.Lock()


def offline_say(text: str):
    """macOS 'say' komutuyla tespit edilen Türkçe sesle seslendir."""
    safe = text.replace('"', '\\"')
    if TURKISH_VOICE:
        cmd = ['say', '-v', TURKISH_VOICE, safe]
    else:
        cmd = ['say', safe]
    with tts_lock:
        subprocess.run(cmd)


def generate_and_play(text: str):
    """Her yorumda doğrudan macOS 'say' ile metni seslendir."""
    offline_say(text)


def tts_thread(text: str):
    threading.Thread(target=generate_and_play, args=(text,), daemon=True).start()


def main(video_id: str):
    chat = pytchat.create(video_id=video_id)
    header = f"🎤 Yorumlar seslendiriliyor{' (' + TURKISH_VOICE + ')' if TURKISH_VOICE else ''}... (Çıkmak için CTRL+C)"
    print(header + "\n")
    try:
        while chat.is_alive():
            for c in chat.get().sync_items():
                msg = f"{c.author.name} dedi ki: {c.message}"
                print(msg)
                tts_thread(msg)
    except KeyboardInterrupt:
        print("\n❚❚ Program sonlandırıldı.")
    finally:
        chat.terminate()

if __name__ == "__main__":
    vid = input("Canlı yayın video ID'sini girin: ").strip()
    main(vid)
