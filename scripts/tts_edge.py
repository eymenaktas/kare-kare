#!/usr/bin/env python3
"""Ücretsiz Edge TTS ile tüm senaryoyu tek parça seslendirir (pip install edge-tts).
Kullanım: tts_edge.py lines.json vo_full.wav [ses=tr-TR-EmelNeural] [hız=+0%]
Ardından: words.py vo_full.wav lines.json > timeline.json"""
import asyncio, json, subprocess, sys
import edge_tts
lines = json.loads(open(sys.argv[1]).read()); out = sys.argv[2]
voice = sys.argv[3] if len(sys.argv) > 3 else "tr-TR-EmelNeural"; rate = sys.argv[4] if len(sys.argv) > 4 else "+0%"
text = " ".join(v[2] if len(v) > 2 else v[0] for v in lines.values())
async def main():
    await edge_tts.Communicate(text, voice, rate=rate).save(out + ".mp3")
asyncio.run(main())
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", out + ".mp3", "-ar", "48000", "-ac", "1", out], check=True)
print(out)
