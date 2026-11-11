#!/usr/bin/env python3
"""Montage: all clips (frames/...) -> one film, video/film.mp4, for the scroll player in index.html.

The film is the clips back to back at 24 fps in ORDER (no holds: a "hold" on the site just stays on a frame).
Every frame is a keyframe (all-intra H.264), so seeking anywhere, forwards or backwards, is instant.
ORDER and frame counts must match ORDER / CLIPS in index.html.
Run:  python3 build_video.py
"""
import os, shutil, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(ROOT, '_build')
OUT = os.path.join(ROOT, 'video', 'film.mp4')

ORDER = ['ea', 'eb', 'k1', 'k2', 'k3', 'k4', 'k5', 'k6', 'k7', 'kx', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'dx',
         'i0', 'i1', 'i2', 'i3', 'i4', 'ix', 'n0', 'n1', 'n2', 'n3']
FOLDER = {'k': 'depth', 'd': 'desert', 'i': 'ice', 'n': 'neon'}

def source(k):
    if k == 'ea': return 'frames/a_%03d.webp', 0
    if k == 'eb': return 'frames/b_%03d.webp', 0
    return f'frames/{FOLDER[k[0]]}/{k}_%03d.webp', 1

shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
enc = ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '23', '-preset', 'slow', '-g', '1', '-bf', '0', '-an']
parts = []
for k in ORDER:
    pattern, start = source(k)
    dst = os.path.join(TMP, k + '.mp4')
    src = ['-framerate', '24', '-start_number', str(start), '-i', os.path.join(ROOT, pattern)]
    if k == 'ea':   # Earth: last 8 frames dissolve into the first frame of eb (was done in code before)
        src += ['-loop', '1', '-framerate', '24', '-i', os.path.join(ROOT, 'frames/b_000.webp'),
                '-filter_complex', "[1][0]scale2ref[b][a];[a][b]blend=all_expr='if(gt(N,88),A*(1-(N-88)/8)+B*(N-88)/8,A)':shortest=1"]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *src, *enc, dst], check=True)
    parts.append(dst)
with open(os.path.join(TMP, 'list.txt'), 'w') as f:
    f.writelines(f"file '{p}'\n" for p in parts)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(TMP, 'list.txt'),
                '-c', 'copy', '-movflags', '+faststart', OUT], check=True)
shutil.rmtree(TMP)
n = subprocess.run(['ffprobe', '-v', 'error', '-count_packets', '-show_entries', 'stream=nb_read_packets',
                    '-of', 'csv=p=0', OUT], capture_output=True, text=True).stdout.strip()
print(f'film.mp4: {n} frames, {int(n) / 24:.1f} s, {os.path.getsize(OUT) / 1048576:.1f} MB')
