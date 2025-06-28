🎙 YouTube Canlı Sohbet Seslendirici

Bu uygulama, YouTube canlı yayın sohbetlerini gerçek zamanlı olarak seslendirmenizi sağlar. macOS say komutuyla birleştirilmiş, ultra modern bir GUI arayüzü üzerinden kolayca kontrol edebilirsiniz.

⚙️ Özellikler

Dil Seçimi: Türkçe, İngilizce, Fransızca, Almanca, İspanyolca, İtalyanca

Otomatik Dil Algılama: Mesaj içeriğine göre TTS dilini otomatik ayarlar

Ses Hızı Ayarı: 100–300 aralığında özel hız kontrolleri

Tiyatro Modu: Sadece Beyaz Liste’deki kullanıcıları seslendirir

Beyaz Liste / Kara Liste: Belirli kullanıcıları filtreleme

Spam & Emoji Filtresi: Kısa, tekrar eden, emoji kodlu mesajları atlar

OBS Entegrasyonu: WebSocket ile kayıt başlat/durdur

Ultra Modern GUI: Cyberpunk/Solarpunk esintili, okunabilir font ve renk paleti

🚀 Kurulum

Proje klasörünü klonlayın veya indirin.

Sanal ortam oluşturun ve aktif edin:

python3 -m venv .venv
source .venv/bin/activate

Gerekli paketleri yükleyin:

pip install -r requirements.txt
pip install websocket-client langdetect

tubeaudio.py dosyasını çalıştırın:

python3 tubeaudio.py

🖥 Nasıl Kullanılır

Dil menüsünden varsayılan konuşma dilini seçin veya Otomatik Algıla kutusunu işaretleyin.

Hız kaydırıcısını kullanarak ses hızını ayarlayın.

Tiyatro Modu’nu açarak yalnızca belirli kullanıcıları dinlemek için Beyaz Liste’yi doldurun.

İstenmeyen kullanıcılar için Kara Liste’ye kullanıcı adlarını girin.

Canlı yayın YouTube linkini yapıştırın.

Başlat butonuna tıklayın — sohbet mesajları log’a düşecek ve seslendirilecektir.

🤖 OBS Entegrasyonu ile yayın kaydını başlatmak veya durdurmak için gerekli bilgileri girip butonları kullanın.

Durdur butonuyla sesi ve sohbet akışını güvenle durdurun.

📌 İpuçları

macOS Ayarlar > Erişilebilirlik > Konuşma > Sesler’den Daniel, Samantha, Yelda gibi kaliteli sesleri indirin.

OBS kayıt kontrolü için OBS WebSocket eklentisinin yüklü ve çalışır durumda olduğundan emin olun.

langdetect bazen kısa mesajlarda hataya düşebilir; otomatik algılamayı sadece uzun metinlerde kullanın.

🤝 Katkıda Bulunun

Projeyi beğendiyseniz ⭐️ atın, pull request’ler ve öneriler için issues açın.

© 2025 WATAM