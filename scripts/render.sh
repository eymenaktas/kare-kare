#!/bin/sh
# Kullanım: render.sh <proje-klasörü> [çıktı.mp4] [fps]
# Proje klasöründe index.html (render(t) içeren), timeline.json (T.end) ve mix.wav olmalı.
set -e
D=$(cd "${1:-.}" && pwd); OUT=${2:-video.mp4}; FPS=${3:-30}; JOBS=${JOBS:-10}
CH=${CHROME:-$(ls -d "$HOME"/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell "$HOME"/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell 2>/dev/null | tail -1)}
[ -x "$CH" ] || { echo "chrome-headless-shell yok: npx playwright install chromium-headless-shell (ya da CHROME=...)"; exit 1; }
W=$(python3 -c "import re;s=open('$D/index.html').read();m=re.search(r'body\{[^}]*width:(\d+)px;height:(\d+)px',s);print(m.group(1)+','+m.group(2) if m else '1080,1920')")
END=$(python3 -c "import json;print(json.load(open('$D/timeline.json'))['T']['end'])")
N=$(python3 -c "print(int($END*$FPS))")
rm -rf "$D/fr"; mkdir "$D/fr"
# Kare başına ayrı betik: macOS xargs -I şablonu 255 baytı aşınca sessizce kare üretmiyor.
cat > "$D/fr/frame.sh" <<F
#!/bin/sh
f="$D/fr/\$(printf %05d \$1).png"; t=\$(awk "BEGIN{print \$1/$FPS}")
for i in 1 2 3; do "$CH" --headless --disable-gpu --hide-scrollbars --window-size=$W --virtual-time-budget=1500 --screenshot="\$f" "file://$D/index.html#\$t" >/dev/null 2>&1; [ -s "\$f" ] && break; done
F
chmod +x "$D/fr/frame.sh"
echo "$N kare, $W, $FPS fps"
seq 0 $((N-1)) | xargs -P "$JOBS" -n 1 "$D/fr/frame.sh"
# ffmpeg %05d dizisi ilk boşlukta durur; eksik kare videoyu sessizce kısaltır.
MISS=$(seq 0 $((N-1)) | while read i; do [ -s "$D/fr/$(printf %05d "$i").png" ] || echo "$i"; done | head -5)
[ -z "$MISS" ] || { echo "Eksik kare: $MISS"; exit 1; }
A=""; [ -f "$D/mix.wav" ] && A="-i $D/mix.wav -c:a aac -b:a 192k -shortest"
ffmpeg -loglevel error -y -framerate "$FPS" -i "$D/fr/%05d.png" $A -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart "$OUT"
echo "DONE $OUT"
