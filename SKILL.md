---
name: video-motoru
description: HTML ile kare kare deterministik video üretimi (reels, short, tanıtım, motion graphics, altyazılı kurgu). Seslendirme → kelime zamanları → sahne HTML'i → headless Chrome kareleri → ffmpeg. Claude ile herhangi bir video, reels, short, tanıtım filmi, kinetik yazı, altyazı veya ffmpeg/HyperFrames/Remotion işi yapılırken HER ZAMAN kullan; kullanıcı her seferinde söylemez.
---

# Video motoru

Video = `render(t)` fonksiyonu olan tek bir HTML sayfası. Her kare, sayfa
`index.html#<saniye>` ile açılıp ekran görüntüsü alınarak üretilir; sonra
ffmpeg kareleri ve ses mixini birleştirir. Hiçbir şey gerçek zamana bağlı
olmadığı için çıktı her seferinde aynıdır ve her kare tek başına incelenebilir.

Hazır bir şablonu birebir kurma — herkes aynı videoyu yapar. Font, renk ve
logo her zaman projenin markasından gelir (projede tema/token dosyasını bul).

## İş akışı

```
0 ölç → 1 senaryo → 2 ses → 3 kelime zamanları → 4 sahne → 5 anahtar kare → 6 mix → 7 render → 8 kontrol
```

Betikler bu skill'in `scripts/` klasöründe, başlangıç sahnesi
`templates/scene.html`. Proje klasöründe: `index.html`, `timeline.json`,
`mix.wav`, fontlar, logolar.

### 0. Ölç
Kaynak dosya varsa önce `ffprobe` (süre, FPS, çözünürlük, ses kanalları).
Platformu seç: 9:16 1080×1920 (Reels/Shorts/TikTok, 20–40 sn) ya da 16:9
1920×1080 (YouTube). Yazı boyu dikeyde en az 56 px.

### 1. Senaryo
- Kısa videoda yapı: **sorun (2–5 sn) → çözüm cümlesi → 2 somut gösterim → marka kapanışı**.
- `lines.json`: `{"s1": ["ekranda görünen metin", "duygu", "okunuş (ops.)"]}`.
  Kısaltmaların okunuşunu üçüncü alana yaz (`MCP` → `Em Si Pi`).
- Ekrandaki her rakam/isim kaynaktan doğrulanır. Doğrulanamayanı ya çıkar ya
  "örnek" olduğunu belli et. Olmayan bir özelliği varmış gibi anlatmadan önce sor.

### 2. Ses (TTS)
Seçenekler ve gerekçeler `references/tts.md`'de. Kısaca:
- **Kalite önemliyse:** ElevenLabs, model v4, tüm senaryo **tek parça**
  (cümleler arası tonlama doğal kalır). Duygu etiketleri: `[tired]`,
  `[excited]`, `[confident]`. Sesi kullanıcıya seçtir; kendi zevkine göre seçme.
- **Ücretsiz ve hızlı:** Edge TTS (`tr-TR-EmelNeural` / `AhmetNeural`) —
  `scripts/tts_edge.py`, kelime sınırlarını da verir.
- Agent sesi duyamaz: 2 sürüm üret, ikisini de whisper'dan geçir, metne en
  sadık olanı seç ve bunu kullanıcıya açıkça söyle.

### 3. Kelime zamanları
```bash
python3 scripts/words.py vo_full.wav lines.json --offset 0.5 > timeline.json
```
whisper ile kelime düzeyinde zaman çıkarır ve satırlara böler (`T`: satır
başlangıç/bitiş + `end`, `W`: satır başına `[başla, bitir, kelime]`). Token
sayısı ekrandaki kelimeyle tutmazsa (ör. "PaketSoft" → "Paket Soft") satır
aralığını harf sayısına göre böler ve uyarı basar.

### 4. Sahne
`templates/scene.html`'i proje klasörüne kopyala, `__T__`/`__W__` yerine
`timeline.json`'u koy (`scripts/inject.py`). Kurallar:
- Tek `render(t)`; durum yok, `Date`/`requestAnimationFrame`/CSS animasyonu/`transition` yok.
- Yardımcılar: `C(a,b,t)` aralık ilerlemesi, `E` ease-out, `B` geri sekme,
  `L` ara değer. Sahne zamanları sabit sayı değil, `T.s3[0]` gibi seslendirmeden gelir.
- İlk kare boş olamaz: ilk sahnenin öğeleri `t<0`'dan girmeye başlasın.
- Arka arkaya iki sahnede aynı geçişi kullanma (kayma, ölçek, silme, kesmeden dönüşüm, yakınlaşma).
- Bir öğeyi sahneler arasında taşıyıp dönüştürmek ("kesmeden geçiş") en güçlü
  geçiştir; videoda 1–2 kez kullan.
- Emoji ve ✓ karakteri yerine SVG çiz; tik işareti `stroke-dashoffset` ile çizilerek gelsin.
- Alt altyazı: konuşulan kelime vurgulu, gelecek kelimeler soluk (şablonda hazır).

### 5. Anahtar kare
```bash
scripts/keyframes.sh index.html 0 3 6.5 10 14 20 26     # → keyframes.png
```
Tam render'dan önce mutlaka bak: üst üste binen yazı, taşan metin, boş kare.

### 6. Mix
Seslendirme 1.0, müzik 0.25–0.35 (konuşmanın altında, 1.2 sn fade-in), efekt
0.3–0.8. `amix=...:normalize=0`, ardından `loudnorm=I=-16:TP=-1.5:LRA=11`.
Örnek filtre ve efekt yerleşimi `references/ses.md`'de. CC BY müzik
kullandıysan atfı teslimde belirt.

### 7. Render
```bash
nohup scripts/render.sh <proje-klasörü> cikti.mp4 > render.log 2>&1 &
```
30 fps, 10 paralel tarayıcı. Arka planda başlat; uygulama kapanınca ölmesin.

### 8. Kontrol (teslimden önce zorunlu)
```bash
scripts/check.sh cikti.mp4
```
1. İlk kare dolu mu.
2. Süre ve ses akışı.
3. Ses yüksekliği −16 LUFS ±1.5.
4. Ses riski: agent duyamaz; kullanıcıya dinlemesi gereken 3–5 anı zaman
   damgasıyla ver (kısaltma okunuşları, sahne geçişleri, müzik girişi).
5. İsteğe bağlı: temiz bağlamlı bir alt-ajan anahtar kareleri eleştirsin, **en fazla 1 tur**.

Ölçmediğin şeyi "düzeldi" diye raporlama.

## Teslim
Videoyu dosya olarak gönder; yanına süre, ses, nelere baktığını ve **nelere
bakmadığını** (tamamını izlemedin, sesi duymadın) yaz.

## Tuzaklar
`references/tuzaklar.md` — yaşanmış hatalar ve çözümleri. Yeni bir hata
yaşarsan oraya ekle.
