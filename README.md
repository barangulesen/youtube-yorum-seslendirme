# 🎙 YouTube Canlı Sohbet Seslendirici

<p align="center">
  <img src="https://wearetheartmakers.com/img/chatSoundUI.png" alt="ChatSound UI" width="800"/>
</p>

Gerçek zamanlı olarak YouTube canlı sohbetlerini seslendirmenizi sağlayan macOS uygulaması. `say` komutuyla birleşik, cyberpunk/solarpunk esintili ultra modern bir GUI üzerinden kolayca kontrol edilir.

---

## ⚙️ Özellikler

- **Dil Seçimi**  
  Türkçe, İngilizce, Fransızca, Almanca, İspanyolca, İtalyanca

- **Otomatik Dil Algılama**  
  Mesaj içeriğine göre TTS dilini otomatik ayarlar

- **Ses Hızı Ayarı**  
  100–300 wpm aralığında kaydırıcı kontrollü hız seçimi

- **Tiyatro Modu**  
  Sadece Beyaz Liste’deki kullanıcıları seslendirir

- **Beyaz Liste / Kara Liste**  
  Belirli kullanıcı adlarını filtreleyin

- **Spam & Emoji Filtresi**  
  Kısa, tekrar eden veya emoji kodlu mesajları atlar

- **OBS Entegrasyonu**  
  WebSocket üzerinden kayıt başlat/durdur komutları

- **Modern GUI**  
  Okunabilir font ve dinamik renk paleti

---

## 🚀 Kurulum

1. **Projeyi klonlayın**  
   ```bash
   git clone https://github.com/yourusername/chatSound.git
   cd chatSound
   ```

2. **Sanal ortam oluşturun ve aktif edin**  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Gerekli paketleri yükleyin**  
   ```bash
   pip install -r requirements.txt
   pip install websocket-client langdetect
   ```

4. **Uygulamayı çalıştırın**  
   ```bash
   python3 tubeaudio.py
   ```

---

## 🖥️ Nasıl Kullanılır

1. **Dil** menüsünden konuşma dilini seçin veya **Otomatik Algıla**’yı işaretleyin.  
2. **Hız** kaydırıcısıyla TTS hızını ayarlayın.  
3. **Tiyatro Modu**’nu açıp Beyaz Liste’ye kullanıcı ekleyin (isteğe bağlı).  
4. **Kara Liste**’ye engellemek istediğiniz kullanıcı adlarını girin.  
5. **YouTube Link** alanına canlı yayın URL’sini yapıştırın.  
6. **Başlat** düğmesine tıklayın → sohbet log’a düşecek ve seslendirilecek.  
7. **OBS** ayarlarınızı girip “🎬 Kaydı Başlat” / “⏸️ Kaydı Durdur” butonlarını kullanın.  
8. İşiniz bittiğinde **Durdur** düğmesiyle akışı sonlandırın.

---

## 📌 İpuçları

- **macOS** Ayarlar → Erişilebilirlik → Konuşma → Sesler menüsünden Daniel, Samantha, Yelda gibi kaliteli ses paketlerini indirin.  
- **OBS WebSocket** eklentisinin yüklü ve aktif olduğundan emin olun.  
- `langdetect` kısa mesajlarda yanlış dil tespiti yapabilir; otomatiği uzun metinlerde tercih edin.

---

## 🤝 Katkıda Bulunun

Projeyi beğendiyseniz ⭐ atın, issue açın veya pull request gönderin!

---

© 2025 WATAM
