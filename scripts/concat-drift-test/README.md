# Concat drift test

Checks whether per-segment extract + `-c copy` concat (what `video-editor/helpers/render.py` does) drifts lip sync, versus a single-pass frame-exact cut.

1. Make a 60 s source with a white flash frame and a 1 kHz beep at every whole second (see the ffmpeg command at the end of this file).
2. `python build_and_cut.py` builds `A.mp4` (per-segment + concat copy) and `B.mp4` (single pass).
3. `python analyze.py` prints audio-minus-video offset at each marker.

Result on 2026-10-16 (12 cuts, ffmpeg 9.0.1): A drifted from 0 to +173 ms by the last cut (about 14 ms per cut). B stayed within 2 ms.

```bash
ffmpeg -y -f lavfi -i "color=c=black:s=320x568:r=30:d=60,geq=lum='if(lt(mod(T,1),0.0334),255,0)':cb=128:cr=128" -f lavfi -i "aevalsrc='if(lt(mod(t,1),0.1),0.8*sin(2*PI*1000*t),0)':s=48000:d=60" -c:v libx264 -crf 12 -g 30 -pix_fmt yuv420p -c:a aac -b:a 192k src.mp4
```
