#!/usr/bin/env python3
"""Montage: the original Kling clips (Lexy) -> one film, video/film.mp4, for the scroll player in index.html.

Source = the original mp4 of every scene from Lexy (CLIPS below: scene -> generation id), cached in _src/lexy/.
Clips go back to back at 24 fps in ORDER (no holds: a "hold" on the site just stays on a frame).
Near-lossless H.264 (crf 13, PSNR ~54 dB vs original) with a keyframe every 8 frames, so seeking stays quick.
ORDER and frame counts (97 for Earth, 73 for the rest) must match index.html.
Run:  python3 build_video.py
"""
import os, shutil, subprocess, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, '_src', 'lexy')
TMP = os.path.join(ROOT, '_build')
OUT = os.path.join(ROOT, 'video', 'film.mp4')

CLIPS = {   # scene -> Lexy generation id (https://lexygpt.com/generation/<id>)
    'ea': 'c95c0c1f-2418-4135-a837-87432a7296e6', 'eb': 'd9949f63-d2b8-4354-869b-33df4c940396',
    'k1': '8bd44c32-6e71-4a5c-acf2-8d19359de9ba', 'k2': 'f50aa81b-692e-44b7-a449-71b52782be58',
    'k3': 'e80fb394-c14c-4481-9d08-f40f17da8728', 'k4': 'd9450aee-eafb-4362-b3ec-536eb627ab96',
    'k5': '7dda3fcb-e719-4afe-a7b6-45f87be2721f', 'k6': '2a70df4e-2766-484c-9eb6-0f13d7f1829d',
    'k7': '686d87e4-3634-4cc4-a3ab-12fd02fbe9e0', 'kx': 'f7ed418e-6c39-48a7-ad9b-71c8c35108f7',
    'd1': '41e25328-2ae2-439f-9d08-bb39326ec4af', 'd2': '6d1fda4f-9410-41ad-b86e-3337e319a0e2',
    'd3': 'bec9ac0f-e411-46bd-8301-ae9586b14b8d', 'd4': 'ee952118-3089-46bc-b0c7-bd0608220839',
    'd5': '8a709066-39c3-48b7-824c-d5e686606083', 'd6': '91e628ab-8165-4ca2-9391-58983f759248',
    'dx': 'dfa8b2df-0eda-4edd-b770-a3166b0babc6',
    'i0': '357ca4e5-0500-4e3f-9684-41a93a5093f4', 'i1': '7347f922-b007-4946-9078-161c1d5bf872',
    'i2': '102dd426-bfa1-4e2d-94e0-392c485b82b7', 'i3': 'c702dc37-2a74-45f1-b3d1-a85e7d790c84',
    'i4': '95db1e4c-980b-4e7b-880d-a9addc9e2ab4', 'ix': 'c6dfc71f-7e4e-4dee-88be-7e70a1134a82',
    'n0': '79ebe047-2ed8-457a-b7b4-8061128af563', 'n1': '59c54cea-ef9f-44cd-9316-3d843c44eec2',
    'n2': 'ce948591-4505-4498-bccd-9d7762f21f9f', 'n3': '79637099-e1dc-4171-bee6-7b7150daeaa0',
}
ORDER = list(CLIPS)

def original(k):
    path = os.path.join(SRC, CLIPS[k] + '.mp4')
    if not os.path.exists(path):
        os.makedirs(SRC, exist_ok=True)
        urllib.request.urlretrieve(f'https://static.lexygpt.com/ugc/{CLIPS[k]}.mp4', path)
    return path

shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
enc = ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '13', '-preset', 'slow', '-g', '8', '-bf', '0',
       '-r', '24', '-an']
# Earth: the last 8 frames of ea dissolve into the first frame of eb
eb0 = os.path.join(TMP, 'eb0.png')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', original('eb'), '-frames:v', '1', eb0], check=True)
parts = []
for k in ORDER:
    src = ['-i', original(k)]
    if k == 'ea':
        src += ['-loop', '1', '-framerate', '24', '-i', eb0, '-filter_complex',
                "[1][0]scale2ref[b][a];[a][b]blend=all_expr='if(gt(N,88),A*(1-(N-88)/8)+B*(N-88)/8,A)':shortest=1"]
    dst = os.path.join(TMP, k + '.mp4')
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
