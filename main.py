#!/usr/bin/env python3
"""news-image-20261117 v3 — "THE WORLD IN ONE PICTURE", a classic broadsheet
front page summing up Tuesday 17 November 2026. Stdlib only, no network.
Renders at 2x into a 2048x2048 buffer and box-downsamples to 1024x1024
so the real TTF glyph outlines read as smooth printed type.
Usage: python3 main.py  (writes /output/entry.png, or $MAKEFUN_OUTPUT_DIR)
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import math
import struct
import zlib

from fontdata import FACES
from serifdata import SERIF
from land import LAND
from stories import LEADS, TILES, STATS, ALSO, PINS

S = 2                      # supersample factor
W, H = 1024, 1024          # output size
PW, PH = W * S, H * S      # buffer size

# --- palette (broadsheet on cream paper) ---
PAPER = (251, 245, 230)
PAPER2 = (255, 253, 246)   # tile / box white
INK = (26, 26, 26)
RED = (200, 16, 46)
NAVY = (31, 58, 95)
BLUE = (46, 95, 163)
GREEN = (31, 122, 76)
ORANGE = (198, 102, 18)
GOLD = (201, 162, 39)
TAN = (232, 217, 176)
TAN_D = (214, 196, 148)
OCEAN = (207, 227, 238)
OCEAN_D = (178, 205, 224)
GREY = (112, 108, 98)
LINEC = (196, 186, 164)
WHITE = (255, 255, 255)

COLORS = {"red": RED, "navy": NAVY, "blue": BLUE, "green": GREEN,
          "orange": ORANGE, "ink": INK, "gold": GOLD}

# --- canvas (bytearray, RGB, PW x PH) ---
BUF = bytearray(PAPER[0:1] * 0)  # placeholder, filled by fill_canvas
BUF = bytearray(bytes(PAPER) * (PW * PH))


def _clip(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def rect(x0, y0, x1, y1, color):
    """Fill rectangle; coords in 1024 units (floats allowed)."""
    ax = _clip(int(math.floor(x0 * S)), 0, PW)
    bx = _clip(int(math.ceil(x1 * S)), 0, PW)
    ay = _clip(int(math.floor(y0 * S)), 0, PH)
    by = _clip(int(math.ceil(y1 * S)), 0, PH)
    if bx <= ax or by <= ay:
        return
    row = bytes(color) * (bx - ax)
    for y in range(ay, by):
        o = (y * PW + ax) * 3
        BUF[o:o + (bx - ax) * 3] = row


def hline(x0, x1, y, w, color):
    rect(x0, y - w / 2.0, x1, y + w / 2.0, color)


def vline(x, y0, y1, w, color):
    rect(x - w / 2.0, y0, x + w / 2.0, y1, color)


def _fill_spans(segs, clip, set_span):
    """Even-odd scanline fill. segs: list of ((x0,y0),(x1,y1)) in buffer px.
    clip: (ax, ay, bx, by) buffer px. set_span(y, xa, xb) paints one run."""
    edges = []
    for (x0, y0), (x1, y1) in segs:
        if y0 == y1:
            continue
        if y0 > y1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        edges.append((y0, y1, x0, (x1 - x0) / (y1 - y0)))
    if not edges:
        return
    ax, ay, bx, by = clip
    ymin = max(ay, int(math.ceil(min(e[0] for e in edges))))
    ymax = min(by - 1, int(math.floor(max(e[1] for e in edges))))
    for y in range(ymin, ymax + 1):
        xs = []
        for (y0, y1, x0, dx) in edges:
            if y0 <= y < y1:
                xs.append(x0 + (y - y0) * dx)
        if len(xs) < 2:
            continue
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            xa = max(ax, int(math.ceil(xs[i])))
            xb = min(bx - 1, int(math.floor(xs[i + 1])))
            if xb >= xa:
                set_span(y, xa, xb)


def fill_poly(pts, color, clip=None):
    """Fill a polygon given as [(x, y), ...] in 1024 units."""
    if clip is None:
        clip = (0, 0, PW, PH)
    segs = []
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        segs.append(((x0 * S, y0 * S), (x1 * S, y1 * S)))
    row = bytes(color)

    def set_span(y, xa, xb):
        o = (y * PW + xa) * 3
        BUF[o:o + (xb - xa + 1) * 3] = row * (xb - xa + 1)

    _fill_spans(segs, clip, set_span)


def fill_circle(cx, cy, r, color):
    """Filled circle, centre/radius in 1024 units."""
    cx2, cy2, r2 = cx * S, cy * S, r * S
    y0 = max(0, int(math.floor(cy2 - r2)))
    y1 = min(PH - 1, int(math.ceil(cy2 + r2)))
    row = bytes(color)
    for y in range(y0, y1 + 1):
        dy = y - cy2
        dx = math.sqrt(max(0.0, r2 * r2 - dy * dy))
        xa = max(0, int(math.ceil(cx2 - dx)))
        xb = min(PW - 1, int(math.floor(cx2 + dx)))
        if xb >= xa:
            o = (y * PW + xa) * 3
            BUF[o:o + (xb - xa + 1) * 3] = row * (xb - xa + 1)


def ring(cx, cy, r, w, color, bg):
    """Circle outline (stroke width w, 1024 units) over background bg."""
    fill_circle(cx, cy, r, color)
    fill_circle(cx, cy, max(0.1, r - w), bg)


def disc(cx, cy, r, color):
    fill_circle(cx, cy, r, color)


def star(cx, cy, r, color, points=8):
    """Multi-point star burst."""
    pts = []
    for i in range(points * 2):
        ang = math.pi * i / points - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    fill_poly(pts, color)


def thick_line(x0, y0, x1, y1, w, color):
    """Thick line as a rotated rectangle, coords in 1024 units."""
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy)
    if ln == 0:
        return
    nx, ny = -dy / ln * w / 2.0, dx / ln * w / 2.0
    fill_poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
               (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], color)


# --- glyph rendering (real TTF outlines, supersampled) ---

def _quad(p0, c, p1, steps):
    out = []
    prev = p0
    for i in range(1, steps + 1):
        t = i / steps
        mt = 1.0 - t
        x = mt * mt * p0[0] + 2 * mt * t * c[0] + t * t * p1[0]
        y = mt * mt * p0[1] + 2 * mt * t * c[1] + t * t * p1[1]
        out.append((prev, (x, y)))
        prev = (x, y)
    return out


def _flatten_contour(pts, scale):
    """One TTF contour (list of (x, y, on_curve) in font units) ->
    list of line segments in buffer px, y flipped (down positive)."""
    segs = []
    n = len(pts)
    if n < 2:
        return segs

    def P(p):
        return (p[0] * scale, -p[1] * scale)

    def mid(a, b):
        return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)

    if pts[0][2]:
        start = P(pts[0])
        idx = 1
    else:
        start = P(mid(pts[-1], pts[0]))
        idx = 0
    cur = start
    for k in range(n):
        p = pts[(idx + k) % n]
        q = pts[(idx + k + 1) % n]
        if p[2]:
            nxt = P(p)
            segs.append((cur, nxt))
            cur = nxt
        else:
            end = P(q) if q[2] else P(mid(p, q))
            chord = math.hypot(end[0] - cur[0], end[1] - cur[1])
            steps = max(2, min(20, int(chord / 4) + 1))
            segs.extend(_quad(cur, P(p), end, steps))
            cur = end
    if cur != start:
        segs.append((cur, start))
    return segs


_GLYPH_CACHE = {}


def _raster_glyph(face, ch, size_px, stroke=0):
    """Rasterize one glyph at buffer-pixel em size `size_px`.
    Returns (sparse, w, h, xoff, yoff, adv_px) where sparse is a list of
    (dx, dy, alpha) with alpha 0..255, and (xoff, yoff) is the bitmap
    top-left relative to the pen position (baseline).
    stroke=1 dilates the bitmap by 1 buffer px (0.5 output px per side),
    a faux-bold that keeps advance widths identical, so wrapping is
    untouched while regular-weight text reads as strong printed type."""
    key = (face is SERIF, ch, size_px, stroke)
    hit = _GLYPH_CACHE.get(key)
    if hit is not None:
        return hit
    upm = face["upm"]
    scale = size_px / upm
    entry = face["glyphs"].get(ch)
    if entry is None:
        entry = face["glyphs"].get("?", (upm // 2, []))
    adv, contours = entry
    segs = []
    for contour in contours:
        segs.extend(_flatten_contour(contour, scale))
    if not segs:
        res = ([], 0, 0, 0, 0, int(round(adv * scale)))
        _GLYPH_CACHE[key] = res
        return res
    xs = [p[0] for s in segs for p in s]
    ys = [p[1] for s in segs for p in s]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    w = int(math.ceil(maxx)) - int(math.floor(minx)) + 1
    h = int(math.ceil(maxy)) - int(math.floor(miny)) + 1
    w = max(w, 1)
    h = max(h, 1)
    ox = -int(math.floor(minx))
    oy = -int(math.floor(miny))
    bmp = bytearray(w * h)
    shifted = [((a[0] + ox, a[1] + oy), (b[0] + ox, b[1] + oy)) for a, b in segs]

    def set_span(y, xa, xb):
        o = y * w + xa
        bmp[o:o + xb - xa + 1] = b"\xff" * (xb - xa + 1)

    _fill_spans(shifted, (0, 0, w, h), set_span)
    xoff = int(math.floor(minx))
    yoff = int(math.floor(miny))
    if stroke:
        nw, nh = w + 2, h + 2
        nb = bytearray(nw * nh)
        for i, a in enumerate(bmp):
            if a:
                bx0, by0 = i % w, i // w
                for ddy in (-1, 0, 1):
                    for ddx in (-1, 0, 1):
                        nb[(by0 + 1 + ddy) * nw + bx0 + 1 + ddx] = 0xFF
        bmp, w, h = nb, nw, nh
        xoff -= 1
        yoff -= 1
    sparse = []
    for i, a in enumerate(bmp):
        if a:
            sparse.append((i % w, i // w, a))
    res = (sparse, w, h, xoff, yoff, int(round(adv * scale)))
    _GLYPH_CACHE[key] = res
    return res


def _blit_glyph(sparse, px, py, color):
    """Paint a rasterized glyph with its top-left at buffer px (px, py)."""
    r, g, b = color
    for dx, dy, a in sparse:
        x = px + dx
        y = py + dy
        if 0 <= x < PW and 0 <= y < PH:
            o = (y * PW + x) * 3
            if a == 255:
                BUF[o] = r
                BUF[o + 1] = g
                BUF[o + 2] = b
            else:
                BUF[o] = (r * a + BUF[o] * (255 - a)) // 255
                BUF[o + 1] = (g * a + BUF[o + 1] * (255 - a)) // 255
                BUF[o + 2] = (b * a + BUF[o + 2] * (255 - a)) // 255


def text_width(text, face, size):
    """Width of text in 1024 units (size = em size in 1024 units)."""
    upm = face["upm"]
    tot = 0.0
    for ch in text:
        entry = face["glyphs"].get(ch)
        if entry is None:
            entry = face["glyphs"].get("?", (upm // 2, []))
        tot += entry[0]
    return tot * size / upm


def draw_text(x, y, text, face, size, color, align="left", stroke=0):
    """Draw text; (x, y) is the top-left of the cap-height box (1024 units).
    align: left / center / right relative to x.
    stroke=1 renders every glyph one buffer px thicker (faux-bold)."""
    if not text:
        return
    w = text_width(text, face, size)
    if align == "center":
        x = x - w / 2.0
    elif align == "right":
        x = x - w
    size_px = size * S
    upm = face["upm"]
    baseline = (y + size * face["cap"] / upm) * S
    pen = x * S
    for ch in text:
        sparse, gw, gh, xoff, yoff, adv = _raster_glyph(face, ch, size_px,
                                                       stroke)
        if sparse:
            _blit_glyph(sparse, int(round(pen)) + xoff,
                        int(round(baseline)) + yoff, color)
        pen += adv


def wrap_text(text, face, size, max_w):
    """Greedy word wrap; returns a list of lines fitting max_w (1024 units)."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, face, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, text, face, size, color, max_w, leading, align="left"):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    for line in wrap_text(text, face, size, max_w):
        draw_text(x, y, line, face, size, color, align=align)
        y += leading
    return y


# --- maps ---

def _proj(lon, lat, bbox, box):
    lon0, lat0, lon1, lat1 = bbox
    x0, y0, x1, y1 = box
    return (x0 + (lon - lon0) / (lon1 - lon0) * (x1 - x0),
            y1 - (lat - lat0) / (lat1 - lat0) * (y1 - y0))


def _poly_bbox(poly):
    lons = [p[0] for p in poly]
    lats = [p[1] for p in poly]
    return (min(lons), min(lats), max(lons), max(lats))


_LAND_BBOX = [_poly_bbox(p) for p in LAND]


def draw_map(box, bbox, labels=(), marks=(), grat_step=5):
    """Draw a flat land/ocean map in box (1024 units) for lon/lat bbox."""
    x0, y0, x1, y1 = box
    lon0, lat0, lon1, lat1 = bbox
    rect(x0, y0, x1, y1, OCEAN)
    # graticule
    lon = math.ceil(lon0 / grat_step) * grat_step
    while lon < lon1:
        gx, _ = _proj(lon, lat0, bbox, box)
        vline(gx, y0, y1, 0.6, OCEAN_D)
        lon += grat_step
    lat = math.ceil(lat0 / grat_step) * grat_step
    while lat < lat1:
        _, gy = _proj(lon0, lat, bbox, box)
        hline(x0, x1, gy, 0.6, OCEAN_D)
        lat += grat_step
    # land
    clip = (int(x0 * S), int(y0 * S), int(x1 * S), int(y1 * S))
    for poly, (plo0, pla0, plo1, pla1) in zip(LAND, _LAND_BBOX):
        if plo1 < lon0 or plo0 > lon1 or pla1 < lat0 or pla0 > lat1:
            continue
        pts = [_proj(p[0], p[1], bbox, box) for p in poly]
        fill_poly(pts, TAN, clip)
    # labels
    for text, lo, la, col in labels:
        lx, ly = _proj(lo, la, bbox, box)
        draw_text(lx, ly - 6, text, FACES["bold"], 11, COLORS[col],
                  align="center")
    # marks
    for mark in marks:
        kind = mark[0]
        if kind == "burst":
            mx, my = _proj(mark[1], mark[2], bbox, box)
            star(mx, my, 8, RED)
            disc(mx, my, 2.6, GOLD)
        elif kind == "dot":
            mx, my = _proj(mark[1], mark[2], bbox, box)
            disc(mx, my, 4, RED)
            ring(mx, my, 4, 1.4, WHITE, RED)
        elif kind == "bridge":
            # Kerch Bridge, struck for a second day: the two decks end in
            # a wide empty gap, a span plunges steeply into the sea, a
            # burst and smoke mark the break, spray shows where it hits.
            for (a, b) in [((35.88, 45.48), (36.26, 45.41)),
                           ((36.92, 45.32), (37.12, 45.26))]:
                p0 = _proj(a[0], a[1], bbox, box)
                p1 = _proj(b[0], b[1], bbox, box)
                thick_line(p0[0], p0[1], p1[0], p1[1], 3.4, INK)
            # fallen span, plunging into the sea
            p0 = _proj(36.30, 45.40, bbox, box)
            p1 = _proj(36.62, 44.99, bbox, box)
            thick_line(p0[0], p0[1], p1[0], p1[1], 3.6, INK)
            # submerged tip
            p0 = _proj(36.62, 44.99, bbox, box)
            p1 = _proj(36.78, 44.95, bbox, box)
            thick_line(p0[0], p0[1], p1[0], p1[1], 2.4, INK)
            # burst at the break
            bx, by = _proj(36.58, 45.38, bbox, box)
            star(bx, by, 12, RED)
            disc(bx, by, 3.2, GOLD)
            # smoke puffs above the gap
            for sx, sy, sr in ((36.42, 45.58, 4.5), (36.62, 45.62, 3.5),
                               (36.55, 45.52, 3.0)):
                px, py = _proj(sx, sy, bbox, box)
                disc(px, py, sr, GREY)
            # splash where the span hits the water
            sx, sy = _proj(36.80, 44.96, bbox, box)
            star(sx, sy, 5, WHITE)
            disc(sx + 6, sy + 2, 1.8, WHITE)
            disc(sx - 6, sy + 3, 1.5, WHITE)
        elif kind == "flags":
            fx, fy = _proj(mark[1], mark[2], bbox, box)
            _flags(fx, fy - 9)
        elif kind == "thunote":
            tx, ty = _proj(mark[1], mark[2], bbox, box)
            draw_text(tx, ty - 6, "THU 19 NOV", FACES["bold"], 11, INK,
                      align="center")


def _flags(x, y):
    """Three mini flags (US, China, Russia), each 26x17, at (x, y)."""
    fw, fh = 26.0, 17.0
    # US
    for i in range(7):
        rect(x, y + i * fh / 7.0, x + fw, y + (i + 1) * fh / 7.0,
             RED if i % 2 == 0 else WHITE)
    rect(x, y, x + fw * 0.42, y + fh * 0.55, NAVY)
    star(x + fw * 0.21, y + fh * 0.27, 2.2, WHITE, points=5)
    # China
    rect(x + fw + 3, y, x + 2 * fw + 3, y + fh, RED)
    star(x + fw + 3 + 6, y + 5.5, 3.0, GOLD, points=5)
    # Russia
    rx = x + 2 * fw + 6
    rect(rx, y, rx + fw, y + fh / 3.0, WHITE)
    rect(rx, y + fh / 3.0, rx + fw, y + 2 * fh / 3.0, BLUE)
    rect(rx, y + 2 * fh / 3.0, rx + fw, y + fh, RED)
    # outline
    for bx in (x, x + fw + 3, rx):
        rect(bx, y, bx + fw, y + 0.8, INK)
        rect(bx, y + fh - 0.8, bx + fw, y + fh, INK)
        rect(bx, y, bx + 0.8, y + fh, INK)
        rect(bx + fw - 0.8, y, bx + fw, y + fh, INK)


# --- pictogram icons (flat, drawn in a square of side s at x, y) ---

def _ellipse_pts(cx, cy, rx, ry, rot, a0, a1, n=20):
    pts = []
    for i in range(n + 1):
        t = math.radians(a0 + (a1 - a0) * i / n)
        ex = rx * math.cos(t)
        ey = ry * math.sin(t)
        pts.append((cx + ex * math.cos(rot) - ey * math.sin(rot),
                    cy + ex * math.sin(rot) + ey * math.cos(rot)))
    return pts


def draw_icon(kind, x, y, s, color):
    """Draw a small flat pictogram; (x, y) top-left, side s (1024 units)."""
    cx, cy = x + s / 2.0, y + s / 2.0
    if kind == "flag":
        vline(x + 4, y + 2, y + s - 2, 2.2, INK)
        fill_poly([(x + 6, y + 3), (x + s - 2, y + 6),
                   (x + s - 6, y + 11), (x + 6, y + 13)], color)
        disc(x + 4, y + 2, 1.8, INK)
    elif kind == "ball":
        disc(cx, cy, s * 0.46, WHITE)
        ring(cx, cy, s * 0.46, 1.6, INK, WHITE)
        fill_poly([(cx, cy - 5), (cx + 5, cy - 1.5), (cx + 3, cy + 4),
                   (cx - 3, cy + 4), (cx - 5, cy - 1.5)], INK)
        for (px, py) in [(cx - 9, cy - 6), (cx + 9, cy - 6), (cx, cy + 9)]:
            disc(px, py, 1.8, INK)
    elif kind == "burst":
        star(cx, cy, s * 0.48, color)
        disc(cx, cy, s * 0.16, GOLD)
    elif kind == "atom":
        disc(cx, cy, 2.4, color)
        for rot in (0.0, math.pi / 3, 2 * math.pi / 3):
            pts = _ellipse_pts(cx, cy, s * 0.44, s * 0.18, rot, 0, 360)
            for a, b in zip(pts, pts[1:]):
                thick_line(a[0], a[1], b[0], b[1], 1.4, color)
    elif kind == "chart":
        bw = s * 0.2
        for i, hfrac in enumerate((0.35, 0.6, 0.9)):
            bx = x + 3 + i * (bw + 2)
            rect(bx, y + s - 3 - s * hfrac, bx + bw, y + s - 3, color)
        thick_line(x + 3, y + 5, x + s - 3, y + 2, 1.6, RED)
    elif kind == "chip":
        rect(x + 4, y + 4, x + s - 4, y + s - 4, INK)
        rect(x + 9, y + 9, x + s - 9, y + s - 9, color)
        for i in range(3):
            off = 8 + i * 6
            rect(x + 1, y + off, x + 4, y + off + 2.4, INK)
            rect(x + s - 4, y + off, x + s - 1, y + off + 2.4, INK)
    elif kind == "storm":
        for r, a0, a1 in ((11, 20, 300), (7.5, 140, 420), (4, 260, 540)):
            pts = _ellipse_pts(cx, cy, r, r, 0, a0, a1, 14)
            for a, b in zip(pts, pts[1:]):
                thick_line(a[0], a[1], b[0], b[1], 1.8, color)
        disc(cx, cy, 1.8, color)
    elif kind == "trophy":
        fill_poly([(x + 4, y + 3), (x + s - 4, y + 3), (x + s - 7, y + 13),
                   (x + 7, y + 13)], GOLD)
        rect(x + s / 2 - 1.5, y + 13, x + s / 2 + 1.5, y + 19, GOLD)
        rect(x + 5, y + 19, x + s - 5, y + 22, GOLD)
        disc(x + 4, y + 7, 2.6, GOLD)
        disc(x + s - 4, y + 7, 2.6, GOLD)
    else:
        disc(cx, cy, s * 0.3, color)


# --- layout ---

BOLD = FACES["bold"]
REG = FACES["regular"]
SERIFB = SERIF

M = 24.0
CW = 976.0  # content width: x 24..1000


def _frame():
    rect(8, 8, 1016, 8 + 2, INK)
    rect(8, 1014, 1016, 1016, INK)
    rect(8, 8, 10, 1016, INK)
    rect(1014, 8, 1016, 1016, INK)


def _masthead():
    draw_text(M, 14, "THE WORLD'S NEWS IN ONE PICTURE", BOLD, 13, RED)
    draw_text(1000, 14, "45 STORIES · 6 CONTINENTS · ALL FROM TUESDAY",
              BOLD, 13, NAVY, align="right")
    draw_text(M, 32, "TUESDAY 17 NOVEMBER 2026", SERIFB, 54, INK)
    hline(M, 1000, 100, 3, INK)
    draw_text(512, 108,
              "Kerch Bridge falls into the sea  ·  Gulf strikes spread  ·  "
              "Trump flies to Shenzhen summit",
              REG, 14, INK, align="center", stroke=1)


def _leads():
    xs = [24.0, 353.0, 682.0]
    w = 318.0
    for lead, x in zip(LEADS, xs):
        col = COLORS[lead["color"]]
        # map
        draw_map((x, 132, x + w, 232), lead["bbox"],
                 labels=lead["labels"], marks=lead["marks"], grat_step=2)
        rect(x, 132, x + w, 132 + 1.2, INK)
        rect(x, 232 - 1.2, x + w, 232, INK)
        rect(x, 132, x + 1.2, 232, INK)
        rect(x + w - 1.2, 132, x + w, 232, INK)
        # section strip
        rect(x, 232, x + w, 252, col)
        draw_text(x + 8, 236.5, lead["section"], BOLD, 12, WHITE)
        # headline (serif bold, max 2 lines)
        lines = wrap_text(lead["headline"], SERIFB, 25, w - 12)
        if len(lines) > 2:
            print("WARN lead headline wraps to", len(lines), "lines:",
                  lead["headline"])
        y = 258.0
        for line in lines[:2]:
            draw_text(x + 6, y, line, SERIFB, 25, INK)
            y += 28
        # deck
        dlines = wrap_text(lead["deck"], REG, 13, w - 12)
        if len(dlines) > 2:
            print("WARN lead deck wraps to", len(dlines), "lines:",
                  lead["deck"])
        y = 318.0
        for line in dlines[:2]:
            draw_text(x + 6, y, line, REG, 13, INK, stroke=1)
            y += 17


def _stats():
    xs = [24.0, 188.0, 351.0, 515.0, 678.0, 842.0]
    w = 157.0
    for (num, label), x in zip(STATS, xs):
        rect(x, 360, x + w, 363, RED)
        rect(x, 360, x + w, 410, PAPER2)
        rect(x, 360, x + 1, 410, LINEC)
        rect(x + w - 1, 360, x + w, 410, LINEC)
        rect(x, 409, x + w, 410, LINEC)
        draw_text(x + w / 2, 368, num, SERIFB, 28, RED, align="center")
        draw_text(x + w / 2, 396, label, BOLD, 9.5, INK, align="center")


def _tiles():
    xs = [24.0, 270.0, 516.0, 762.0]
    ys = [418.0, 511.0, 604.0]
    w, h = 238.0, 86.0
    for i, tile in enumerate(TILES):
        x = xs[i % 4]
        y = ys[i // 4]
        col = COLORS[tile["color"]]
        rect(x, y, x + w, y + h, PAPER2)
        rect(x, y, x + 4, y + h, col)
        rect(x, y, x + w, y + 1, LINEC)
        rect(x, y + h - 1, x + w, y + h, LINEC)
        rect(x + w - 1, y, x + w, y + h, LINEC)
        draw_text(x + 12, y + 7, tile["section"], BOLD, 10, col)
        draw_icon(tile["icon"], x + w - 34, y + 5, 26, col)
        lines = wrap_text(tile["headline"], BOLD, 15, w - 56)
        if len(lines) > 2:
            print("WARN tile headline wraps to", len(lines), "lines:",
                  tile["headline"])
        yy = y + 21
        for line in lines[:2]:
            draw_text(x + 12, yy, line, BOLD, 15, INK)
            yy += 18
        dlines = wrap_text(tile["deck"], REG, 11.5, w - 20)
        if len(dlines) > 2:
            print("WARN tile deck wraps to", len(dlines), "lines:",
                  tile["deck"])
        yy = y + 59
        for line in dlines[:2]:
            draw_text(x + 12, yy, line, REG, 11.5, INK, stroke=1)
            yy += 14


def _bottom():
    # left: world map with numbered pins
    draw_text(M, 698, "WHERE IT HAPPENED", BOLD, 13, RED)
    hline(M, 596, 716, 1.6, RED)
    draw_map((24, 722, 596, 930), (-170, -58, 190, 84), grat_step=30)
    rect(24, 722, 596, 723.2, INK)
    rect(24, 928.8, 596, 930, INK)
    rect(24, 722, 25.2, 930, INK)
    rect(594.8, 722, 596, 930, INK)
    for num, _name, lo, la, dlo, dla in PINS:
        tx, ty = _proj(lo, la, (-170, -58, 190, 84), (24, 722, 596, 930))
        px, py = _proj(lo + dlo, la + dla, (-170, -58, 190, 84),
                       (24, 722, 596, 930))
        if dlo or dla:
            # short leader from the true spot (small dot) to the offset pin
            thick_line(tx, ty, px, py, 1.2, RED)
            disc(tx, ty, 3, RED)
        disc(px, py, 8, RED)
        ring(px, py, 8, 1.4, WHITE, RED)
        draw_text(px, py - 5.5, str(num), BOLD, 10, WHITE, align="center")
    # key under the map: 2 rows x 6
    for i, (num, name, _lo, _la, _dlo, _dla) in enumerate(PINS):
        kx = 24 + (i % 6) * 96
        ky = 938 + (i // 6) * 16
        draw_text(kx, ky, str(num), BOLD, 11, RED)
        draw_text(kx + text_width(str(num), BOLD, 11) + 5, ky, name,
                  BOLD, 11, INK)
    # right: ALSO list, two columns of 15
    draw_text(612, 698, "ALSO ON TUESDAY 17 NOVEMBER", BOLD, 13, NAVY)
    hline(612, 1000, 716, 1.6, NAVY)
    for i, item in enumerate(ALSO):
        col = 0 if i < 15 else 1
        row = i % 15
        x = 612 + col * 198
        y = 724 + row * 16.5
        if text_width(item, REG, 11.5) > 176:
            print("WARN ALSO item too wide:", item)
        disc(x + 4, y + 5.5, 2.4, RED)
        draw_text(x + 12, y, item, REG, 11.5, INK, stroke=1)


def _footer():
    hline(M, 1000, 976, 1.6, INK)
    draw_text(512, 984,
              "Every story happened or was first reported on "
              "Tuesday 17 November 2026.",
              REG, 11, INK, align="center", stroke=1)
    draw_text(512, 999,
              "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN  ·  "
              "Original drawings",
              REG, 11, GREY, align="center", stroke=1)


# --- PNG output ---

def _png_bytes(rgb):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += rgb[yy * W * 3:(yy + 1) * W * 3]
    out = bytearray(b"\x89PNG\r\n\x1a\n")
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    out += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += chunk(b"IEND", b"")
    return bytes(out)


def _downsample():
    out = bytearray(W * H * 3)
    for y in range(H):
        r0 = (2 * y) * PW * 3
        r1 = r0 + PW * 3
        for x in range(W):
            i0 = r0 + x * 6
            i1 = r1 + x * 6
            o = (y * W + x) * 3
            out[o] = (BUF[i0] + BUF[i0 + 3] + BUF[i1] + BUF[i1 + 3]) // 4
            out[o + 1] = (BUF[i0 + 1] + BUF[i0 + 4] + BUF[i1 + 1] +
                          BUF[i1 + 4]) // 4
            out[o + 2] = (BUF[i0 + 2] + BUF[i0 + 5] + BUF[i1 + 2] +
                          BUF[i1 + 5]) // 4
    return bytes(out)


def main():
    import time
    t0 = time.time()
    _frame()
    _masthead()
    _leads()
    _stats()
    _tiles()
    _bottom()
    _footer()
    rgb = _downsample()
    png = _png_bytes(rgb)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    import hashlib
    print("stories:", len(LEADS) + len(TILES) + len(ALSO))
    print("size:", len(png), "bytes; sha256:",
          hashlib.sha256(png).hexdigest())
    print("runtime: %.1fs" % (time.time() - t0))
    print("wrote", path)


if __name__ == "__main__":
    main()
