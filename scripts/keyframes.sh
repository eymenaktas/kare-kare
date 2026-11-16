#!/bin/sh
# Kullanım: keyframes.sh index.html t1 t2 ... → keyframes.png (yan yana, küçültülmüş)
set -e
H=$(cd "$(dirname "$1")" && pwd)/$(basename "$1"); shift
CH=${CHROME:-$(ls -d "$HOME"/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell "$HOME"/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell 2>/dev/null | tail -1)}
W=$(python3 -c "import re;s=open('$H').read();m=re.search(r'body\{[^}]*width:(\d+)px;height:(\d+)px',s);print(m.group(1)+','+m.group(2) if m else '1080,1920')")
T=$(mktemp -d); i=0
for t in "$@"; do i=$((i+1)); "$CH" --headless --disable-gpu --hide-scrollbars --window-size="$W" --virtual-time-budget=1500 --screenshot="$T/$(printf %03d $i).png" "file://$H#$t" >/dev/null 2>&1 & done; wait
ffmpeg -loglevel error -y -pattern_type glob -i "$T/*.png" -vf "scale=-2:420,drawtext=text='%{n}':x=8:y=8:fontsize=28:fontcolor=red,tile=${i}x1" -frames:v 1 keyframes.png 2>/dev/null \
 || ffmpeg -loglevel error -y -pattern_type glob -i "$T/*.png" -vf "scale=-2:420,tile=${i}x1" -frames:v 1 keyframes.png
echo "keyframes.png  (sıra: $*)"
