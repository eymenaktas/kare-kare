<div align="center">

# kare-kare

**Claude'a "bir tanıtım videosu yap" de; seslendirmesiyle, kelime kelime altyazısıyla, render'ı ve kontrolüyle gelsin.**

HTML'den kare kare, deterministik video üreten bir [Claude Code](https://claude.com/claude-code) skill'i.
`SKILL.md` okuyan her ajanda (`codex`, `agy`…) da çalışır.

[Tanıtım videosu](ornek/tanitim/kare-kare-tanitim.mp4) · [Nasıl çalışır](#nasıl-çalışır) · [Kurulum](#kurulum) · [Kendi videonu yap](#kendi-videonu-yap)

</div>

---

## Bu videoyu hiçbir insan kurgulamadı

[`ornek/tanitim/kare-kare-tanitim.mp4`](ornek/tanitim/kare-kare-tanitim.mp4) — 37 saniye, 1080×1920, 1101 kare.

Videodaki ses **ElevenLabs** (eleven_v4, tek parça), gördüğün her kare de **kare-kare**. Senaryodan
son MP4'e kadar her adım bu repodaki betiklerle yapıldı; videonun bütün kaynağı
[`ornek/tanitim/`](ornek/tanitim) klasöründe duruyor. Köşedeki `KARE 0840` sayacı süs değil:
sahne gerçekten kaçıncı karede olduğunu biliyor, çünkü her kare `index.html#<saniye>` açılarak çekiliyor.

## Neden böyle?

Klasik video editörü zaman çizelgesi, fare ve "bir kare kaydı mı?" demek. Bir ajan bunların hiçbirini iyi yapamaz.
Ama bir ajan **kod yazmayı** ve **bir resme bakmayı** çok iyi yapar. kare-kare videoyu bu ikisine indirger:

| | |
|---|---|
| **Deterministik** | Sahne tek bir `render(t)` fonksiyonu. `Date`, `requestAnimationFrame`, CSS animasyonu yok. Aynı girdi → aynı kareler. |
| **Sese kilitli** | Her yazı ve geçiş seslendirmedeki kelime zamanlarından gelir (`T.s3[0]`, `W.s5[2][0]`). Metni değiştir, her şey kendiliğinden kayar. |
| **İncelenebilir** | Ajan tam render'dan önce istediği anın karesine bakar (`keyframes.sh`). Üst üste binen yazıyı izlemeden yakalar. |
| **Hafif** | Chrome headless shell + ffmpeg + whisper.cpp. Node projesi, Remotion, After Effects yok. |

## Nasıl çalışır

```
0 ölç → 1 senaryo → 2 ses → 3 kelime zamanları → 4 sahne → 5 anahtar kare → 6 mix → 7 render → 8 kontrol
```

1. **Senaryo** — `lines.json`: satır başına ekran metni, duygu ve gerekirse okunuş (`"Claude Code"` → `"Klod Kod"`).
2. **Ses** — Tüm senaryo **tek parça** okunur; cümleler arası tonlama doğal kalır. Kalite için ElevenLabs, ücretsiz seçenek Edge TTS. Ajan sesi duyamadığı için iki sürüm üretir, ikisini de whisper'dan geçirip metne sadık olanı seçer.
3. **Kelime zamanları** — `words.py` whisper ile her kelimenin başlangıç/bitişini bulur ve satırlara böler → `timeline.json`.
4. **Sahne** — `templates/scene.html`: yardımcılar (`C` aralık, `E` ease-out, `B` geri sekme, `L` ara değer), çizilerek gelen SVG tik, karaoke altyazı.
5. **Anahtar kare** — Seçilen anlar tek görselde yan yana; ajan render'dan önce buna bakar.
6. **Mix** — Seslendirme 1.0, müzik ~0.25, `loudnorm` ile −16 LUFS.
7. **Render** — 10 paralel headless Chrome, 30 fps, eksik kare kontrolü, ffmpeg ile H.264 + AAC.
8. **Kontrol** — `check.sh`: ilk kare boş mu, süre, ses akışı, ses yüksekliği.

## Kurulum

```bash
git clone https://github.com/eymenaktas/kare-kare ~/.claude/skills/kare-kare
```

```bash
brew install ffmpeg whisper-cpp
```

```bash
npx playwright install chromium-headless-shell
```

```bash
mkdir -p ~/.cache/whisper && curl -L -o ~/.cache/whisper/ggml-base.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

İsteğe bağlı ücretsiz TTS: `pip install edge-tts`. Model veya Chrome başka yerdeyse
`WHISPER_MODEL=/yol/ggml-base.bin`, `CHROME=/yol/chrome-headless-shell`.

## Kendi videonu yap

Claude Code'da istemen yeter, skill kendiliğinden devreye girer:

> ürünüm için 30 saniyelik dikey bir tanıtım videosu yap, ElevenLabs ile seslendir

Elle çalıştırmak istersen:

```bash
S=~/.claude/skills/kare-kare
python3 $S/scripts/tts_edge.py lines.json vo_full.wav tr-TR-EmelNeural   # ya da ElevenLabs'ten vo_full.wav
python3 $S/scripts/words.py vo_full.wav lines.json --offset 0.5 > timeline.json
cp $S/templates/scene.html template.html && python3 $S/scripts/inject.py template.html timeline.json
$S/scripts/keyframes.sh index.html 0 3 6 10                              # → keyframes.png
ffmpeg -y -i vo_full.wav -af "adelay=500|500,loudnorm=I=-16:TP=-1.5" -ar 48000 mix.wav
$S/scripts/render.sh . video.mp4
$S/scripts/check.sh video.mp4
```

Tanıtım videosunu baştan üretmek için [`ornek/tanitim/`](ornek/tanitim) içinde `../../scripts/render.sh . video.mp4` yeter; ses, mix ve zamanlar hazır.

## İçerik

| Dosya | Ne yapar |
|---|---|
| `SKILL.md` | Ajanın izlediği iş akışı ve kurallar |
| `scripts/words.py` | whisper ile kelime zamanları, satırlara hizalama |
| `scripts/inject.py` | `timeline.json`'u şablona gömer |
| `scripts/tts_edge.py` | Ücretsiz Edge TTS ile tek parça seslendirme |
| `scripts/keyframes.sh` | Seçili anların karelerini yan yana tek görsele koyar |
| `scripts/render.sh` | Paralel kare çekimi, eksik kare kontrolü, ffmpeg |
| `scripts/check.sh` | İlk kare, süre, ses akışı, LUFS |
| `templates/scene.html` | Başlangıç sahnesi ve yardımcılar |
| `references/tts.md` | Türkçe TTS karşılaştırması, ElevenLabs ipuçları |
| `references/ses.md` | Ses katmanları, seviyeler, ffmpeg filtreleri |
| `references/tuzaklar.md` | Gerçek projelerde yaşanmış hatalar ve çözümleri |
| `ornek/tanitim/` | Bu reponun tanıtım videosunun tüm kaynağı |

## Sınırlar

- Ajan sesi duyamaz. Okunuşları whisper'la doğrular ama son dinleme senin işin; skill teslimde dinlemen gereken anları zaman damgasıyla verir.
- Render süresi kare sayısıyla doğrusal artar; birkaç dakikalık videolar dakikalar sürer.
- macOS'ta geliştirildi; Linux'ta Chrome ve whisper yollarını ortam değişkenleriyle ver.

## Lisans

MIT. Tanıtım videosundaki müzik Suno ile üretildi.
