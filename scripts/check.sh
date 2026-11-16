#!/bin/sh
# Kullanım: check.sh video.mp4 [beklenen_süre]
V=$1; ok=1
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V"); echo "süre: ${d}s"
[ -n "$2" ] && python3 -c "import sys;sys.exit(abs($d-$2)>0.5)" || { [ -n "$2" ] && { echo "  ✗ beklenen $2"; ok=0; }; }
a=$(ffprobe -v error -select_streams a -show_entries stream=codec_name -of csv=p=0 "$V"); [ -n "$a" ] && echo "ses: $a" || { echo "  ✗ ses akışı yok"; ok=0; }
python3 - "$V" <<'PY' || ok=0
import subprocess,sys
raw=subprocess.run(["ffmpeg","-v","error","-i",sys.argv[1],"-vframes","1","-vf","scale=64:64,format=gray","-f","rawvideo","-"],capture_output=True).stdout
m=sum(raw)/len(raw); var=sum((x-m)**2 for x in raw)/len(raw)
print(f"ilk kare: parlaklık {m:.0f}, varyans {var:.0f}")
if var<40 or m<8: print("  ✗ ilk kare boş/düz görünüyor"); sys.exit(1)
PY
L=$(ffmpeg -i "$V" -af ebur128 -f null - 2>&1 | grep -A1 Integrated | tail -1 | grep -o '\-*[0-9.]*')
echo "ses yüksekliği: $L LUFS"; [ -n "$L" ] && python3 -c "import sys;sys.exit(abs($L+16)>1.5)" || { echo "  ✗ hedef -16±1.5"; ok=0; }
[ $ok = 1 ] && echo "TAMAM — sesi yine de kullanıcı dinlemeli" || { echo "SORUN VAR"; exit 1; }
