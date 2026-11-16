# Ses mixi

## Katmanlar
| Katman | Seviye | Ne zaman |
|---|---|---|
| Seslendirme | 1.0 | `--offset` anından itibaren tek parça |
| Müzik | 0.25–0.35 | Çözüm anında girer (sorun kısmı müziksiz/drone), 1.2 sn fade-in, sonda 1.8 sn fade-out |
| Drone / tik-tak | 0.2–0.5 | Yalnızca sorun kısmı (gerilim) |
| Whoosh | 0.5–0.8 | Sahne geçişleri, geçişten 0.1 sn önce |
| Click | 0.35–0.6 | Kart/tik/araç çağrısı belirdiğinde |
| Chime | 0.3 | Başarı anı (bağlandı, tamamlandı) |
| Klavye | 0.3 | Yazı efekti süresince, 1.6 sn'ye kırp |
| Kutu/kapanış | 0.6 | Logo anında |

## Örnek ffmpeg filtresi (Python'dan kurulur)
```python
inp, flt, mix = [], [], []
def add(path, at, vol=1.0, extra=""):
    i = len(inp)//2; inp += ["-i", str(path)]          # dikkat: //2, "-i" de sayılıyor
    flt.append(f"[{i}]{extra}volume={vol},adelay={int(at*1000)}|{int(at*1000)}[a{i}]"); mix.append(f"[a{i}]")
add("vo_full.wav", 0.5, 1.0, "aresample=48000,pan=stereo|c0=c0|c1=c0,")
add("audio/whoosh.mp3", T["s2"][0]-0.1, 0.7)
add("audio/music.mp3", T["s2"][0]-0.2, 0.3, f"atrim=8:{8+mlen},afade=t=in:d=1.2,afade=t=out:st={mlen-1.8}:d=1.8,")
fc = ";".join(flt)+";"+"".join(mix)+f"amix=inputs={len(mix)}:normalize=0,atrim=0:{end},loudnorm=I=-16:TP=-1.5:LRA=11[out]"
subprocess.run(["ffmpeg","-y",*inp,"-filter_complex",fc,"-map","[out]","-ar","48000","mix.wav"], check=True)
```

## Kaynaklar
- Efekt: Freesound, yalnızca **CC0** filtresiyle (atıf gerekmez).
- Müzik: Kevin MacLeod / incompetech (CC BY — açıklamada atıf şart), YouTube Audio Library.
- Drone ve tik-tak'ı ffmpeg ile sentezle:
  `ffmpeg -f lavfi -i "sine=f=55:d=8" -af "volume=0.4,tremolo=f=0.3" drone.wav`
