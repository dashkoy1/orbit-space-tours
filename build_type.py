#!/usr/bin/env python3
"""Headings in Neuropol X as vector outlines (img/type/*.svg) — the font file itself never goes on the site.

Why: the free Neuropol X licence (Typodermic EULA) does not cover web fonts. Until a web licence is bought,
the logo and the big headings are artwork (outlines). With a web licence: load the font via @font-face instead.
Needs fontTools (pip install fonttools) and the font installed: ~/Library/Fonts/neuropol x rg.ttf
Run:  python3 build_type.py
Sizes/tracking from Figma (frame 1:73): 90 px headings and 40 px logo, both with letter-spacing -0.15 em.
Also makes img/type/words.js — every word of the headings/phrases in PHRASES as outlines; index.html sets them
word by word (np(el, text)), so lines wrap like text. A word missing here is shown in the fallback font:
after changing a phrase in index.html add it to PHRASES and run again.
"""
import os, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.expanduser('~/Library/Fonts/neuropol x rg.ttf')
OUT = os.path.join(ROOT, 'img', 'type')
ITEMS = {   # name: (text, color, letter-spacing in em)
    'logo':   ('ORBIT', '#ffffff', -0.15),
    'h1-top': ('ВЫ ВИДЕЛИ ВСЕ НА ЗЕМЛЕ?', '#ffffff', -0.15),
    'h1-bot': ('ТОГДА ПОРА ДАЛЬШЕ!', '#a1a1a1', -0.15),
}

PHRASES = [   # keep in sync with index.html (tour names/destinations, phrases in the helmet, final, boarding pass)
    'ГЛУБИНА', 'ДВА СОЛНЦА', 'СЕВЕРНАЯ ТИШИНА', 'НЕОН 2077', 'KEPLER-22b', 'ЗЕМЛЯ', 'ORBIT',
    'Дышите спокойно. Мы взлетаем.', 'KEPLER-22b. Океан без берегов.', 'Два солнца. Держитесь за караван.',
    'Северная тишина. Слышите? Ничего.', 'Неон 2077. Добро пожаловать.',
    'СИГНАЛ ПОТЕРЯН', 'КУДА ЛЕТИМ?',
]
WORD_TRACK = -0.12   # em, inside words

font = TTFont(FONT)
cmap, gs, hmtx = font.getBestCmap(), font.getGlyphSet(), font['hmtx']
upm = font['head'].unitsPerEm
asc, desc = font['hhea'].ascent, font['hhea'].descent
os.makedirs(OUT, exist_ok=True)

for name, (text, color, track) in ITEMS.items():
    pen, bounds, x = SVGPathPen(gs), BoundsPen(gs), 0
    for i, ch in enumerate(text):
        g = cmap.get(ord(ch))
        if g is None: sys.exit(f'no glyph for {ch!r} in the font')
        # y flipped: font units up -> svg down, baseline at y = ascent
        t = (1, 0, 0, -1, x, asc)
        gs[g].draw(TransformPen(pen, t)); gs[g].draw(TransformPen(bounds, t))
        x += hmtx[g][0] + (track * upm if i < len(text) - 1 else 0)
    x0, y0, x1, y1 = bounds.bounds
    # viewBox: tight horizontally (ink), full ascent..descent vertically so all headings share a baseline
    vb = f'{x0:.0f} 0 {x1 - x0:.0f} {asc - desc}'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{text}">'
           f'<path fill="{color}" d="{pen.getCommands()}"/></svg>\n')
    path = os.path.join(OUT, name + '.svg')
    open(path, 'w', encoding='utf-8').write(svg)
    print(f'{path}  {os.path.getsize(path) / 1024:.1f} KB  ratio {(x1 - x0) / (asc - desc):.3f}  (em height {(asc - desc) / upm:.3f})')

# words for index.html: {word: [advance, path]} in font units, y flipped, baseline at ascent; viewBox height = ascent - descent
words = {}
for w in sorted({w for ph in PHRASES for w in ph.split()}):
    pen, x = SVGPathPen(gs, ntos=lambda v: str(round(v))), 0
    for i, ch in enumerate(w):
        g = cmap.get(ord(ch))
        if g is None: sys.exit(f'no glyph for {ch!r} in the font')
        gs[g].draw(TransformPen(pen, (1, 0, 0, -1, x, asc)))
        x += hmtx[g][0] + (WORD_TRACK * upm if i < len(w) - 1 else 0)
    words[w] = [round(x), pen.getCommands()]
import json
js = ('/* Neuropol X outlines of the words used on the site (build_type.py). Not a font: fixed words only. */\n'
      f'window.NP_TYPE={{h:{asc - desc},desc:{-desc / upm:.3f},words:' + json.dumps(words, ensure_ascii=False, separators=(',', ':')) + '};\n')
path = os.path.join(OUT, 'words.js')
open(path, 'w', encoding='utf-8').write(js)
print(f'{path}  {len(words)} words  {os.path.getsize(path) / 1024:.1f} KB')
