#!/usr/bin/env python3
"""Helmet frame for the site, from a generated image whose visor is filled with flat chroma green.

Usage:  python3 build_helmet.py <generated.png> [out=img/helmet.webp]
Makes:
  img/helmet.webp     — the frame, visor cut out to transparency (green spill removed)
  img/visor_dist.png  — for the glass shader: distance from the visor edge into the glass,
                        0 at the edge (and on the rim) -> 255 at DMAX of the image width or deeper
"""
import os, subprocess, sys
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

ROOT = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'img', 'helmet.webp')
os.makedirs(os.path.dirname(out), exist_ok=True)

# 1) frame: colorkey pure green -> transparent with a soft band, despill the rim
vf = 'format=rgba,colorkey=0x00FF00:0.30:0.12,despill=type=green:mix=0.6:expand=0.1,format=rgba'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', vf, '-c:v', 'libwebp', '-lossless', '0',
                '-quality', '90', '-alpha_quality', '100', '-frames:v', '1', out], check=True)
print(out, f'{os.path.getsize(out) / 1024:.0f} KB')

# 2) distance map of the glass (where the frame is transparent), small: the shader samples it smoothly
DMAX, W = 0.12, 640
alpha = np.asarray(Image.open(out).convert('RGBA'))[:, :, 3]
H = round(alpha.shape[0] * W / alpha.shape[1])
glass = np.asarray(Image.fromarray(alpha).resize((W, H), Image.BILINEAR)) < 128
d = distance_transform_edt(glass) / (DMAX * W)
dist = os.path.join(os.path.dirname(out), 'visor_dist.png')
Image.fromarray((np.clip(d, 0, 1) * 255).round().astype(np.uint8)).save(dist, optimize=True)
print(dist, f'{W}x{H}', f'{os.path.getsize(dist) / 1024:.0f} KB')
