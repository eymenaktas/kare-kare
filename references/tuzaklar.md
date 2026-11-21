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
- **macOS `xargs -I{}` 255 bayt sınırı**: proje yolu uzunsa render.sh "command line cannot be assembled, too long" verir ve kare üretmez → `xargs -S 4096 -P ... -I{}`. Ayrıca whisper kontrolünde `/tmp/w.wav` gibi ortak yollar başka ajanla çakışır; scratchpad kullan. Ozan TTS sabit tohumlu (seed 7): `--only` aynı metne aynı sesi verir, değiştirmek için metni değiştir.
- **macOS `xargs -I` 255 bayt sınırı**: render.sh'deki uzun `sh -c` şablonu "command line cannot be assembled, too long" verip hiç kare üretmeyebiliyor → kare başına ayrı betik (`frame.sh N`) ve `xargs -n 1`.
- **Eksik tek kare videoyu kısaltır**: ffmpeg `%05d` dizisi ilk boşlukta durur, `-shortest` sesi de keser. Encode'dan önce eksik kareleri kontrol et; check.sh süresini timeline `end` ile karşılaştır.
- **`whisper-cli -ml 1 -sow` ilk kelimeyi 0.05 sn'ye ezer ve hizalama kayar**: `-ml 1` olmadan `-ojf` ile BPE token zamanlarını alıp boşluk başlangıçlarına göre birleştirmek + karakter düzeyinde `SequenceMatcher` hizalaması yapmak hem gerçek cümle duraklamalarını korur hem sıfır kaymalı kelime takibi verir.
- **FFmpeg `adelay` + `atrim=0:END` ses süresini kısaltır**: `adelay` sonrası `atrim=0:END` PTS kayması nedeniyle çıktıyı `END - delay` saniyede kesebiliyor; `-shortest` ile video da kısalıyor. Mixi NumPy'da sabit `int(end*SR)` örnek uzunluğunda kurup son aşamada loudness normalize etmek ya da `atrim` öncesi/sonrası `asetpts=PTS-STARTPTS` ve `ffprobe` süre kontrolü yapmak şart.
- **words.py son satırları ezebilir**: whisper kapanış cümlesini az token'la verirse son satır 1 sn'ye sıkışır. `silencedetect=n=-35dB:d=0.18` ile duraklamaları bul, son satırların sınırını oradan koy, kelimeleri harf oranıyla dağıt.
- **Sahne pencereleri üst üste binmesin**: çıkışı bir sonraki sahnenin ilk kelimesinden *önce* bitir (`nx(k)-0.4 → nx(k)-0.05`). Aksi hâlde bir sahnenin başlığı ile sonrakinin dev yazısı aynı karede görünür.
- **Mix videodan kısa kalmasın**: `apad` + `amix=duration=longest` + `atrim=0:END`; render öncesi `ffprobe` ile mix süresi = `T.end` olmalı.
