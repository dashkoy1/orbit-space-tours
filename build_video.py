#!/usr/bin/env python3
"""Encode every clip's frames (frames/...) into video/<clip>.mp4 for the scroll player in index.html.

All-intra H.264 (every frame is a keyframe): seeking to any frame, forwards or backwards, is instant.
Run from anywhere:  python3 build_video.py            (all clips)
                    python3 build_video.py d6 dx      (only these)
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'video')

clips = {'ea': ('frames/a_%03d.webp', 0), 'eb': ('frames/b_%03d.webp', 0)}
for folder, ids in [('depth', 'k1 k2 k3 k4 k5 k6 k7 kx'), ('desert', 'd1 d2 d3 d4 d5 d6 dx'),
                    ('ice', 'i0 i1 i2 i3 i4 ix'), ('neon', 'n0 n1 n2 n3')]:
    for k in ids.split():
        clips[k] = (f'frames/{folder}/{k}_%03d.webp', 1)

os.makedirs(OUT, exist_ok=True)
for k in sys.argv[1:] or clips:
    pattern, start = clips[k]
    dst = os.path.join(OUT, k + '.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '24', '-start_number', str(start),
                    '-i', os.path.join(ROOT, pattern), '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-crf', '23', '-preset', 'slow', '-g', '1', '-bf', '0', '-movflags', '+faststart',
                    '-an', dst], check=True)
    print(f'{k}: {os.path.getsize(dst) / 1048576:.1f} MB')
