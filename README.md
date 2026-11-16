# video-motoru

Claude Code (ve `codex` gibi `SKILL.md` okuyan ajanlar) için **HTML'den kare kare video üreten** bir skill.
Seslendirme → kelime zamanları → sahne HTML'i → headless Chrome kareleri → ffmpeg.
Reels/Shorts/TikTok tanıtımları, kinetik yazı ve kelime kelime altyazılı videolar için.

```
senaryo (lines.json) → TTS (tek parça) → words.py → scene.html → keyframes.sh → mix → render.sh → check.sh
```

Neden bu yöntem?
- **Deterministik:** sahne yalnızca `render(t)` fonksiyonu; her kare `index.html#<saniye>` ile çekilir. Aynı girdi, aynı video.
- **Sese kilitli:** her yazı ve geçiş seslendirmenin kelime zamanlarından gelir; metin değişince her şey kendiliğinden kayar.
- **İncelenebilir:** ajan tam render'dan önce istediği anın karesine bakar.
- **Bağımlılık az:** Chrome headless shell + ffmpeg + whisper.cpp. Node projesi yok.

## Kurulum

```bash
git clone https://github.com/eymenaktas/video-motoru ~/.claude/skills/video-motoru
```

Gerekenler (macOS, Homebrew):

```bash
brew install ffmpeg whisper-cpp
```

```bash
npx playwright install chromium-headless-shell
```

```bash
mkdir -p ~/.cache/whisper && curl -L -o ~/.cache/whisper/ggml-base.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

İsteğe bağlı ücretsiz TTS:

```bash
pip install edge-tts
```

Model başka yerdeyse `WHISPER_MODEL=/yol/ggml-base.bin`, Chrome başka yerdeyse `CHROME=/yol/chrome-headless-shell`.

## Kullanım

Claude Code'da video ile ilgili bir şey istemen yeter ("ürünüm için 30 saniyelik dikey tanıtım yap"); skill kendiliğinden devreye girer ve `SKILL.md`'deki adımları izler. Elle çalıştırmak istersen:

```bash
S=~/.claude/skills/video-motoru
# 1) senaryo
cat > lines.json <<'J'
{"s1": ["Her gün aynı iş: fiyat güncelle, stok say.", "sad"],
 "s2": ["Artık sadece söyle.", "cheerful"],
 "s3": ["Marka. Konuşarak yönet.", "cheerful"]}
J
# 2) ses (ya da ElevenLabs'ten tek parça indir → vo_full.wav)
python3 $S/scripts/tts_edge.py lines.json vo_full.wav tr-TR-EmelNeural
# 3) kelime zamanları
python3 $S/scripts/words.py vo_full.wav lines.json --offset 0.5 > timeline.json
# 4) sahne
cp $S/templates/scene.html template.html && python3 $S/scripts/inject.py template.html timeline.json
# 5) anahtar kareler
$S/scripts/keyframes.sh index.html 0 2 4 6
# 6) ses mixi (en basit hali: yalnızca seslendirme)
ffmpeg -y -i vo_full.wav -af "adelay=500|500,loudnorm=I=-16:TP=-1.5" -ar 48000 mix.wav
# 7) render
$S/scripts/render.sh . video.mp4
# 8) kontrol
$S/scripts/check.sh video.mp4
```

## İçerik

| Dosya | Ne yapar |
|---|---|
| `SKILL.md` | Ajanın izlediği iş akışı ve kurallar |
| `scripts/words.py` | whisper ile kelime zamanları, satırlara noktalamaya göre hizalama |
| `scripts/inject.py` | `timeline.json`'u şablona gömer |
| `scripts/tts_edge.py` | Ücretsiz Edge TTS ile tek parça seslendirme |
| `scripts/keyframes.sh` | Seçili anların karelerini yan yana tek görsele koyar |
| `scripts/render.sh` | Paralel kare çekimi + ffmpeg (sesli MP4) |
| `scripts/check.sh` | İlk kare boş mu, süre, ses akışı, LUFS |
| `templates/scene.html` | Yardımcılar (`C`, `E`, `B`, `L`, çizilen SVG tik), örnek 3 sahne, karaoke altyazı |
| `references/tts.md` | Türkçe TTS karşılaştırması ve ElevenLabs ipuçları |
| `references/ses.md` | Ses katmanları, seviyeler, ffmpeg filtre örneği, lisanslı kaynaklar |
| `references/tuzaklar.md` | Yaşanmış hatalar ve çözümleri |

## Kaynak

Yöntemler, "Claude ile Video Editlemek İçin En İyi Repoları İnceledim" videosunda
(youtube.com/watch?v=VXe-Bkku-rM) incelenen repolardan seçilip kendi hattına
uyarlandı; o repoların kodu kopyalanmadı.

## Lisans

MIT
