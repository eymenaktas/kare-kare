#!/usr/bin/env python3
"""Sakin arka plan müziği: yumuşak pad akorları + seyrek piyano notaları, vurmalı yok.
Deterministik ve telifsiz. Kullanım: music.py <süre_sn> music.wav"""
import sys, wave
import numpy as np

SR = 48000
dur = float(sys.argv[1]); out = sys.argv[2]
n = int(dur * SR); t = np.arange(n) / SR
hz = lambda m: 440 * 2 ** ((m - 69) / 12)

# Am9 – Fmaj7 – Cmaj7 – G6, her akor 4 vuruş @ 72 BPM (~3.33 sn), yavaş geçiş
chords = [[45, 57, 60, 64, 71], [41, 57, 60, 64, 69], [48, 55, 59, 64, 67], [43, 55, 59, 62, 64]]
bar = 60 / 72 * 4
L = np.zeros(n); R = np.zeros(n)
for ci in range(int(dur / bar) + 2):
    ch = chords[ci % 4]; s0 = ci * bar
    env = np.clip((t - s0 + 0.8) / 1.6, 0, 1) * np.clip((s0 + bar + 0.8 - t) / 1.6, 0, 1)
    env = np.sin(env * np.pi / 2) ** 2
    if not env.any(): continue
    for j, m in enumerate(ch):
        f = hz(m); amp = (0.5 if j == 0 else 0.22) * env
        for det, side in ((-0.12, 0), (0.12, 1)):           # hafif detune → geniş stereo
            w = np.sin(2 * np.pi * (f + det) * t + j) + 0.18 * np.sin(4 * np.pi * (f + det) * t)
            (L if side == 0 else R)[:] += amp * w

# Seyrek piyano: akor tonlarından, yarım vuruşta bir değil, iki vuruşta bir
rng = np.random.default_rng(7)
beat = 60 / 72
for bi in range(int(dur / (beat * 2))):
    s0 = bi * beat * 2 + 0.05
    ch = chords[int(s0 / bar) % 4]; m = ch[rng.integers(2, 5)] + 12
    i0 = int(s0 * SR); seg = np.arange(min(int(3 * SR), n - i0)) / SR
    if len(seg) <= 0: continue
    f = hz(m); e = np.exp(-seg * 2.2) * np.clip(seg / 0.01, 0, 1)
    note = e * (np.sin(2 * np.pi * f * seg) + 0.3 * np.sin(4 * np.pi * f * seg) * np.exp(-seg * 3))
    pan = 0.35 + 0.3 * rng.random()
    L[i0:i0 + len(seg)] += 0.16 * note * (1 - pan); R[i0:i0 + len(seg)] += 0.16 * note * pan

# Basit yankı (iki gecikme) + tek kutuplu alçak geçiren → sıcak, yumuşak
for d, g in ((0.29, 0.28), (0.53, 0.18)):
    k = int(d * SR); L[k:] += g * R[:-k]; R[k:] += g * L[:-k]
def lp(x, fc=2200):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); acc = 0.0
    # vektörel yaklaşım: kısa blok içinde döngü
    for i in range(len(x)): acc = (1 - a) * x[i] + a * acc; y[i] = acc
    return y
L, R = lp(L), lp(R)
fade = np.clip(t / 2.0, 0, 1) * np.clip((dur - t) / 3.0, 0, 1)
st = np.stack([L * fade, R * fade], 1); st /= np.abs(st).max() * 1.12
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype("<i2").tobytes())
print(out, f"{dur:.2f} sn")
