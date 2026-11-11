#!/usr/bin/env python3
"""Helmet frame: cut the chroma-green visor out of a generated image -> transparent PNG/WebP for the site.

Usage:  python3 build_helmet.py <generated.png|jpg> [out=img/helmet.webp]
The visor area must be filled with flat green (#00FF00) in the source image.
Edges: green-ness is turned into soft alpha and green spill on the rim is removed.
"""
import os, subprocess, sys

src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img', 'helmet.webp')
os.makedirs(os.path.dirname(out), exist_ok=True)
# colorkey: pure green -> transparent, with a soft blend band; despill: neutralise green fringe on the rim
vf = ("format=rgba,colorkey=0x00FF00:0.30:0.12,despill=type=green:mix=0.6:expand=0.1,"
      "format=rgba")
ext = os.path.splitext(out)[1].lower()
codec = ['-c:v', 'libwebp', '-lossless', '0', '-quality', '90', '-alpha_quality', '100'] if ext == '.webp' else []
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', vf, *codec, '-frames:v', '1', out], check=True)
print(out, f'{os.path.getsize(out) / 1024:.0f} KB')
