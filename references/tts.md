# Türkçe TTS seçimi (2026-11 denemeleri)

| Seçenek | Kalite | Ücret | Kelime zamanı | Not |
|---|---|---|---|---|
| **ElevenLabs v4** | En iyi; duygu etiketleri çalışıyor | Kredi (~1 kredi/karakter) | Yok → whisper | Tek parça üret. Ses seçimi kritik. |
| **Edge TTS** (Emel, Ahmet) | İyi, biraz düz | Ücretsiz, çevrimiçi | WordBoundary verir | Hızlı taslak ve yedek. |
| Ahenk / VoxCPM2 + LoRA (yerel GPU) | Kararsız: kelime yutuyor, uyduruyor | Ücretsiz | Yok | Satır başına 30–180 sn. Reklamda kullanma. |
| Piper | Tek Türkçe ses (dfki), robotik | Ücretsiz | Yok | macOS'ta espeak yolu bozuk; GPL. |
| Coqui XTTS | İyi | — | — | Lisansı ticari kullanıma izin vermiyor. |

## ElevenLabs ipuçları
- Kütüphanede dil filtresi → Turkish, kullanım sayısına göre sırala. Denenmiş:
  **Dilara – Warm, Natural, Conversational** (beğenildi),
  Mehmet – Energetic Young Turkish Male (beğenilmedi: "aşırı kötü").
  Gökçe Deniz, Adam, Nil, Yunus da çok kullanılan seçenekler.
- Önizlemeler ücretsiz; üretim kredi harcar. Üretmeden önce kalan krediyi ve
  karakter sayısını kontrol et.
- Kısaltmaları okunuşuyla yaz (`Em Si Pi`). Tırnak içindeki komut cümleleri
  doğal okunuyor.
- Etiketler: başta `[tired]`/`[sad]`, çözümde `[excited]`, kapanışta `[confident]`.
- İndirilen MP3 `~/Downloads/ElevenLabs_<tarih>_<ses>_...mp3` adıyla gelir.

## Agent sesi duyamaz
Kalite seçimini kullanıcı yapar. Agent'ın yapabileceği: whisper ile metne
sadakati ölçmek (yanlış duyulan kelime sayısı), süre, sessizlik ve kırpılma
kontrolü. Seçimi neye göre yaptığını kullanıcıya yaz.
