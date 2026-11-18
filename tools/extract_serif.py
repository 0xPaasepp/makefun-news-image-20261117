#!/usr/bin/env python3
"""Build-time only: extract DejaVu Serif Bold glyph outlines into a data file
in the same format as fontdata.py (FACES dict, contours of (x, y, on_curve)).
Not part of the entry runtime."""
import sys
from fontTools.ttLib import TTFont

SRC = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
OUT = "/home/hatch/workspace/makefun/news-image-20261117/repo/serifdata.py"

font = TTFont(SRC)
cmap = font.getBestCmap()
hmtx = font["hmtx"]
glyf = font["glyf"]
head = font["head"]
os2 = font["OS/2"]
hhea = font["hhea"]

glyphs = {}
for code in range(32, 127):
    ch = chr(code)
    name = cmap.get(code)
    if name is None:
        continue
    g = glyf[name]
    adv, _lsb = hmtx[name]
    contours = []
    if g.numberOfContours > 0 and not g.isComposite():
        coords, ends, flags = g.getCoordinates(glyf)
        start = 0
        for end in ends:
            contour = []
            for i in range(start, end + 1):
                x, y = coords[i]
                contour.append((x, y, 1 if (flags[i] & 1) else 0))
            contours.append(contour)
            start = end + 1
    elif g.isComposite():
        # Simple composites: only needed chars are ASCII; if any composite
        # appears, record it as empty and let the renderer skip it.
        contours = []
    glyphs[ch] = (adv, contours)

cap_h = 0
_h = glyf[cmap[ord("H")]]
if _h.numberOfContours > 0:
    _coords, _ends, _flags = _h.getCoordinates(glyf)
    cap_h = max(y for _, y in _coords)

with open(OUT, "w") as f:
    f.write("# Serif glyph outlines extracted at build time from DejaVu Serif Bold\n")
    f.write("# (freely licensed). Runtime code only reads this data.\n\n")
    f.write("SERIF = {\n")
    f.write("  'upm': %d, 'cap': %d, 'ascent': %d, 'descent': %d,\n" % (
        head.unitsPerEm, cap_h, hhea.ascent, hhea.descent))
    f.write("  'glyphs': {\n")
    for ch in sorted(glyphs):
        adv, contours = glyphs[ch]
        f.write("    %r: (%d, %r),\n" % (ch, adv, contours))
    f.write("  },\n}\n")

print("wrote", OUT, "glyphs:", len(glyphs))
print("upm", head.unitsPerEm, "cap", cap_h,
      "ascent", hhea.ascent, "descent", hhea.descent)
