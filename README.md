# Sosyal Medya Dijital Klon

Bu proje, sosyal medya profillerinden dijital klon oluşturan bir web uygulamasıdır. Uygulama, kullanıcının sosyal medya hesaplarından (Twitter, Instagram, LinkedIn) veri toplayarak bir "dijital klon" oluşturur ve bu klonla etkileşime geçmenizi sağlar.

## Özellikler

- Sosyal medya profil analizi
  - Duygu analizi
  - Kelime kullanım analizi
  - Konu ilgi alanları tespiti
  - Etkileşim metrikleri analizi
  - Zamansal paylaşım desenleri

- Gelişmiş metin işleme
  - Türkçe dil desteği
  - Kelime frekans analizi
  - Bigram analizi
  - Hashtag ve mention analizi
  - Duygu tonu analizi

- Kişiselleştirilmiş yanıtlar
  - Kullanıcının yazım stilini taklit etme
  - Duygu tonuna uygun yanıtlar
  - Emoji ve noktalama kullanımı
  - Konu odaklı yanıtlar

## Kurulum

1. Gerekli Python paketlerini yükleyin:
```bash
pip install -r requirements.txt
```

2. Uygulamayı başlatın:
```bash
python src/app.py
```

## Kullanım

1. Web arayüzünden bir sosyal medya profil URL'si girin
2. Sistem profili analiz edip dijital klon oluşturacak
3. Oluşturulan klonla sohbet edebilirsiniz

## Teknik Detaylar

- Backend: Python (Flask)
- NLP: NLTK, Transformers
- Dil Modeli: BERT (Turkish)
- Web Scraping: Selenium, BeautifulSoup4
- Veri Analizi: NumPy, scikit-learn

## Güvenlik ve Gizlilik

- Yalnızca kamuya açık veriler kullanılır
- Kişisel veriler işlendikten sonra silinir
- KVKK ve GDPR uyumlu veri işleme

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın. 