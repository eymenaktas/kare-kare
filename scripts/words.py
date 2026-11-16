#!/usr/bin/env python3
"""Tek parça seslendirmeden satır + kelime zamanları çıkarır.

Kullanım: words.py ses.wav lines.json [--offset 0.5] [--tail 2.6] > timeline.json
  lines.json: {"s1": ["ekran metni", "duygu", "okunuş (ops.)"], ...}
Model: WHISPER_MODEL ortam değişkeni ya da ~/.cache/whisper/ggml-base.bin
Çıktı: {"T": {"s1": [başla, bitir], ..., "end": n}, "W": {"s1": [[başla, bitir, kelime], ...]}}
"""
import argparse, json, os, re, subprocess, sys, tempfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("audio"); ap.add_argument("lines")
ap.add_argument("--offset", type=float, default=0.5, help="sesin videoda başladığı an")
ap.add_argument("--tail", type=float, default=2.6, help="ses bittikten sonraki kapanış süresi")
ap.add_argument("--lang", default="tr")
a = ap.parse_args()
model = os.environ.get("WHISPER_MODEL", str(Path.home() / ".cache/whisper/ggml-base.bin"))
lines = json.loads(Path(a.lines).read_text())
tok = lambda s: [w for w in re.split(r"\s+", s.strip()) if w]

with tempfile.TemporaryDirectory() as td:
    w16 = f"{td}/a.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", a.audio, "-ar", "16000", "-ac", "1", w16], check=True)
    subprocess.run(["whisper-cli", "-m", model, "-l", a.lang, "-ml", "1", "-sow", "-oj", "-of", f"{td}/o", "-f", w16],
                   check=True, capture_output=True)
    js = json.loads(Path(f"{td}/o.json").read_text())
sp = [(s["offsets"]["from"] / 1000, s["offsets"]["to"] / 1000, s["text"].strip())
      for s in js["transcription"] if s["text"].strip()]
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.audio]))

# Satır sınırları: whisper tokenlarını cümle sonu noktalamasıyla sayarak eşle.
# Her satır için okunuş metnindeki kelime sayısı kadar token alınır; sapma
# olursa satır sonundaki noktalamaya (. ! ? …) en yakın tokena kaydırılır.
T, W, j = {}, {}, 0
keys = list(lines)
for n_k, k in enumerate(keys):
    shown = tok(lines[k][0]); spoken = tok(lines[k][2] if len(lines[k]) > 2 else lines[k][0])
    n = len(spoken)
    if n_k == len(keys) - 1: n = len(sp) - j
    else:
        best = None
        for d in range(-3, 4):
            e = j + n + d - 1
            if 0 <= e < len(sp) and re.search(r"[.!?…]$", sp[e][2]):
                if best is None or abs(d) < abs(best): best = d
        if best is not None: n += best
    seg = sp[j:j + n]; j += n
    if not seg: sys.exit(f"{k}: token kalmadı — lines.json ile ses uyuşmuyor")
    a0, b0 = seg[0][0], seg[-1][1]
    if len(seg) == len(shown): ws = [(x, y) for x, y, _ in seg]
    else:
        print(f"uyarı {k}: {len(seg)} token / {len(shown)} kelime → harf oranıyla bölündü", file=sys.stderr)
        tot = sum(len(x) for x in shown); ws, c = [], a0
        for x in shown: e = c + (b0 - a0) * len(x) / tot; ws.append((c, e)); c = e
    T[k] = [round(a.offset + a0, 3), round(a.offset + b0, 3)]
    W[k] = [[round(a.offset + x, 3), round(a.offset + y, 3), w] for (x, y), w in zip(ws, shown)]
    print(f"{k}: {T[k][0]:.2f}–{T[k][1]:.2f}  {' '.join(t for *_, t in seg)}", file=sys.stderr)
T["end"] = round(a.offset + dur + a.tail, 3)
print(json.dumps({"T": T, "W": W}, ensure_ascii=False, indent=1))
