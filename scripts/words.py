#!/usr/bin/env python3
"""Tek parça seslendirmeden satır + kelime zamanları çıkarır.

Kullanım: words.py ses.wav lines.json [--offset 0.5] [--tail 2.6] > timeline.json
  lines.json: {"s1": ["ekran metni", "duygu", "okunuş (ops.)"], ...}
Model: WHISPER_MODEL ortam değişkeni ya da ~/.cache/whisper/ggml-base.bin
Çıktı: {"T": {"s1": [başla, bitir], ..., "end": n}, "W": {"s1": [[başla, bitir, kelime], ...]}}

Yöntem: whisper'ın token zamanları (-ojf, varsa DTW) karakterlere yayılır,
okunuş metni bu karakter akışına SequenceMatcher ile hizalanır. Whisper'ın
kelimeyi yanlış duyması ("Ilevın Labs" → "11 laps") ya da kelime sayısının
tutmaması zamanlamayı bozmaz; her kelime kendi karakterlerinin anına oturur.
Ekran metni okunuştan farklı kelime sayısındaysa ("ElevenLabs" ↔ "Ilevın Labs"),
ekran kelimeleri satır içindeki karakter konumuna göre konuşma zamanına eşlenir.
"""
import argparse, json, os, re, subprocess, sys, tempfile, unicodedata
from difflib import SequenceMatcher
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

def norm(s):
    s = s.replace("İ", "i").replace("I", "ı").lower()
    return "".join(c for c in unicodedata.normalize("NFC", s) if c.isalnum())

def whisper(w16, td, dtw):
    cmd = ["whisper-cli", "-m", model, "-l", a.lang, "-ojf", "-of", f"{td}/o", "-f", w16]
    if dtw: cmd[1:1] = ["-dtw", dtw]
    r = subprocess.run(cmd, capture_output=True)
    return r.returncode == 0 and Path(f"{td}/o.json").exists()

with tempfile.TemporaryDirectory() as td:
    w16 = f"{td}/a.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", a.audio, "-ar", "16000", "-ac", "1", w16], check=True)
    preset = {"ggml-base.bin": "base", "ggml-small.bin": "small", "ggml-medium.bin": "medium",
              "ggml-large-v3.bin": "large.v3", "ggml-tiny.bin": "tiny"}.get(Path(model).name)
    if not (preset and whisper(w16, td, preset)) and not whisper(w16, td, None):
        sys.exit("whisper-cli çalışmadı")
    js = json.loads(Path(f"{td}/o.json").read_text())
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.audio]))

# 1) Token → karakter akışı (her karaktere bir zaman)
hc, ht = [], []
for seg in js["transcription"]:
    for tk in seg.get("tokens", []):
        txt = tk.get("text", "")
        if not txt or txt.startswith("[_") or txt.startswith("<|"): continue
        t0, t1 = tk["offsets"]["from"] / 1000, tk["offsets"]["to"] / 1000
        if tk.get("t_dtw", -1) >= 0:           # DTW: token başlangıcının daha hassas tahmini
            d = tk["t_dtw"] / 100; t1 = max(t1, d); t0 = min(max(d - (t1 - t0) * 0.15, 0), d)
        n = norm(txt)
        for i, ch in enumerate(n):
            hc.append(ch); ht.append(t0 + (t1 - t0) * (i + 0.5) / len(n))
heard = "".join(hc)

# 2) Okunuş metni → karakter akışı, satır ve kelime sınırlarıyla
keys = list(lines)
sc, owner = [], []           # owner[i] = (satır, kelime indeksi)
spoken_words = {}
for k in keys:
    sp = tok(lines[k][2] if len(lines[k]) > 2 else lines[k][0]); spoken_words[k] = sp
    for wi, w in enumerate(sp):
        for ch in norm(w): sc.append(ch); owner.append((k, wi))
said = "".join(sc)

# 3) Hizala; eşleşmeyen karakterlerin zamanını komşulardan doğrusal doldur
st = [None] * len(said)
sm = SequenceMatcher(None, said, heard, autojunk=False)
for blk in sm.get_matching_blocks():
    for i in range(blk.size): st[blk.a + i] = ht[blk.b + i]
known = [i for i, v in enumerate(st) if v is not None]
if len(known) < len(said) * 0.4:
    sys.exit(f"hizalama zayıf ({len(known)}/{len(said)} karakter) — ses lines.json ile uyuşmuyor mu?")
for i in range(len(st)):
    if st[i] is None:
        lo = max((j for j in known if j < i), default=None); hi = min((j for j in known if j > i), default=None)
        if lo is None: st[i] = st[hi]
        elif hi is None: st[i] = st[lo]
        else: st[i] = st[lo] + (st[hi] - st[lo]) * (i - lo) / (hi - lo)
# monoton yap (geri giden zaman olmasın)
for i in range(1, len(st)): st[i] = max(st[i], st[i - 1])

# 4) Kelime zamanları: kelimenin ilk/son karakteri
spans = {}
for i, (k, wi) in enumerate(owner):
    s = spans.setdefault((k, wi), [st[i], st[i]]); s[1] = st[i]
ln = {k: [spans[(k, wi)] for wi in range(len(spoken_words[k])) if (k, wi) in spans] for k in keys}

# 5) Satır başını yakındaki duraklama bitişine oturt (±0.3 sn): cümle girişleri kare doğruluğunda olur
sil = subprocess.run(["ffmpeg", "-i", a.audio, "-af", "silencedetect=n=-35dB:d=0.15", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
sil_end = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", sil)]
T, W, matched = {}, {}, len(known) / len(said)
for k in keys:
    sw = ln[k]; shown = tok(lines[k][0])
    if not sw: sys.exit(f"{k}: boş satır")
    near = min(sil_end, key=lambda x: abs(x - sw[0][0]), default=None)
    if near is not None and abs(near - sw[0][0]) <= 0.3 and near < sw[0][1]: sw[0] = [near, sw[0][1]]
    a0, b0 = sw[0][0], sw[-1][1] + 0.12
    if len(shown) == len(sw):
        ws = [(x, y + 0.08) for x, y in sw]
    else:  # ekran kelimesi ↔ konuşma: satır içindeki karakter oranıyla eşle
        idx = [i for i, (kk, _) in enumerate(owner) if kk == k]
        tot = sum(len(norm(x)) or 1 for x in shown); c, ws = 0, []
        for x in shown:
            n = len(norm(x)) or 1
            i0 = idx[min(int(c / tot * len(idx)), len(idx) - 1)]
            i1 = idx[min(int((c + n) / tot * len(idx)) - 1, len(idx) - 1)]
            ws.append((st[i0], st[i1] + 0.08)); c += n
    T[k] = [round(a.offset + a0, 3), round(a.offset + b0, 3)]
    W[k] = [[round(a.offset + x, 3), round(a.offset + y, 3), w] for (x, y), w in zip(ws, shown)]
    print(f"{k}: {T[k][0]:.2f}–{T[k][1]:.2f}  {' '.join(shown)}", file=sys.stderr)
print(f"hizalanan karakter: %{matched*100:.0f}", file=sys.stderr)
T["end"] = round(a.offset + dur + a.tail, 3)
print(json.dumps({"T": T, "W": W}, ensure_ascii=False, indent=1))
