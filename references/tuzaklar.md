# Yaşanmış hatalar

- **İlk kare boş**: öğeler t=0'da girmeye başlarsa ilk kare boş kalır. Girişleri
  `C(-0.45+i*0.18, 0+i*0.18, t)` gibi negatif zamandan başlat.
- **✓ ve emoji karakterleri** fonta göre tuhaf görünüyor → SVG çiz (`check()` şablonda).
- **Satır satır TTS** cümleler arasında tonlamayı bozuyor → tek parça üret, whisper ile böl.
- **whisper token sayısı ≠ ekran kelimesi** ("PaketSoft" → "Paket Soft", "MCP" tek token).
  `words.py` satır sonu noktalamasına göre hizalar, gerekirse harf oranıyla böler.
- **Ses mixinde girdi indeksi** `len(inp)` değil `len(inp)//2` ("-i" de listede).
- **Uzun render uygulama kapanınca ölüyor** → `nohup ... & disown`.
- **`npx hyperframes`** otomatik modda reddedilebiliyor; chrome-headless-shell + ffmpeg
  hattı aynı işi bağımlılıksız yapıyor.
- **macOS'ta ~/Documents'tan `cp`** "Interrupted system call" verebiliyor → dosyayı yerinde kullan ya da `cat` ile tekrar dene.
- **CSS `transition`/`animation`** kare kare çekimde rastgele ara durum verir → yasak.
- **Doğrulanmamış iddia** (README'de "11 tema", kodda 2) videoya girmez.
- **Kullanıcının beğenmediği ses**: sesi kendin seçme; 2–3 aday önizlemesi sun ya da kullanıcının söylediği sesi kullan.
