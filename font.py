"""Text rendering from embedded filled glyph outlines.

Glyph outlines were extracted at build time from Liberation Sans (SIL OFL,
Arial-metric-compatible) -- see fontdata.py. Each glyph is a set of filled
contours (outer + holes) with quadratic curves, exactly like a real font.
Rasterization: flatten curves, scanline-fill with non-zero winding at 4x
supersampling, box-downsample to 1x. The result is normal printed type:
filled letterforms with real curves, smooth edges, no strokes, no pixels.
"""

import math

import fontdata

SS = 4  # glyph supersampling factor


def _flatten_contour(contour):
    """Contour = list of (x, y, on). Returns a list of (x, y) polyline points
    (font units, y up), closed implicitly."""
    n = len(contour)
    if n == 0:
        return []
    if n == 1:
        return [contour[0][:2]]
    # start point
    pts = [p[:2] for p in contour]
    on = [p[2] for p in contour]
    if on[0]:
        start = pts[0]
        idx = 0
    elif on[-1]:
        start = pts[-1]
        idx = n - 1
    else:
        start = ((pts[-1][0] + pts[0][0]) / 2.0, (pts[-1][1] + pts[0][1]) / 2.0)
        idx = 0
    out = [start]
    i = idx
    cur = start
    # walk the contour starting after the start point
    order = [(i + k) % n for k in range(1, n + 1)]
    k = 0
    while k < len(order):
        j = order[k]
        if on[j]:
            out.append(pts[j])
            cur = pts[j]
            k += 1
        else:
            # off-curve control point: next point decides
            nj = order[(k + 1) % len(order)] if k + 1 < len(order) else idx
            if on[nj]:
                end = pts[nj]
                _quad(out, cur, pts[j], end)
                cur = end
                k += 2
            else:
                mid = ((pts[j][0] + pts[nj][0]) / 2.0, (pts[j][1] + pts[nj][1]) / 2.0)
                _quad(out, cur, pts[j], mid)
                cur = mid
                k += 1
    return out


def _quad(out, p0, p1, p2):
    n = 12
    for i in range(1, n + 1):
        t = i / n
        u = 1.0 - t
        out.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))


_cache = {}


def rasterize(ch, cap_px, bold):
    """Return (rows, x0, y0, advance_px): coverage rows (bytearray 0-255) of
    the glyph at cap height cap_px. x0/y0 = bitmap origin in final pixels
    relative to the glyph origin (baseline, left)."""
    key = (ch, round(cap_px, 2), bold)
    hit = _cache.get(key)
    if hit is not None:
        return hit
    face = fontdata.FACES["bold" if bold else "regular"]
    adv, contours = face["glyphs"][ch]
    scale = cap_px / face["cap"]
    # flatten to pixel-space segments (y down)
    segs = []
    minx = miny = 1e9
    maxx = maxy = -1e9
    for contour in contours:
        pts = _flatten_contour(contour)
        if len(pts) < 2:
            continue
        px = [(p[0] * scale, -p[1] * scale) for p in pts]
        for i in range(len(px)):
            ax, ay = px[i]
            bx, by = px[(i + 1) % len(px)]
            segs.append((ax, ay, bx, by))
            minx = min(minx, ax, bx)
            maxx = max(maxx, ax, bx)
            miny = min(miny, ay, by)
            maxy = max(maxy, ay, by)
    if not segs:
        result = ([], 0, 0, adv * scale)
        _cache[key] = result
        return result
    # 4x bitmap bounds
    x0 = int(math.floor(minx)) - 1
    y0 = int(math.floor(miny)) - 1
    x1 = int(math.ceil(maxx)) + 1
    y1 = int(math.ceil(maxy)) + 1
    bw = max(1, x1 - x0)
    bh = max(1, y1 - y0)
    bw4 = bw * SS
    bh4 = bh * SS
    rows4 = [bytearray(bw4) for _ in range(bh4)]
    ox = -x0 * SS
    oy = -y0 * SS
    segs4 = [((ax - x0) * SS, (ay - y0) * SS, (bx - x0) * SS, (by - y0) * SS)
             for (ax, ay, bx, by) in segs]
    for gy in range(bh4):
        yc = gy + 0.5
        crosses = []
        for (ax, ay, bx, by) in segs4:
            if (ay <= yc < by) or (by <= yc < ay):
                t = (yc - ay) / (by - ay)
                crosses.append((ax + t * (bx - ax), 1 if ay < by else -1))
        if not crosses:
            continue
        crosses.sort(key=lambda c: c[0])
        wind = 0
        row = rows4[gy]
        for i, (cx, w) in enumerate(crosses):
            if wind != 0 and i > 0:
                xa = max(0, int(math.ceil(crosses[i - 1][0])))
                xb = min(bw4 - 1, int(math.floor(cx)))
                if xb >= xa:
                    row[xa:xb + 1] = b"\x01" * (xb - xa + 1)
            wind += w
    # downsample 4x4 -> coverage
    rows = []
    for y in range(bh):
        orow = bytearray(bw)
        for x in range(bw):
            s = 0
            for dy in range(SS):
                r4 = rows4[y * SS + dy]
                base = x * SS
                s += r4[base] + r4[base + 1] + r4[base + 2] + r4[base + 3]
            orow[x] = (s * 255) // 16 if s else 0
        rows.append(orow)
    result = (rows, x0, y0, adv * scale)
    _cache[key] = result
    return result


# ---------------------------------------------------------------- text API

def char_advance(ch, cap_px, bold):
    face = fontdata.FACES["bold" if bold else "regular"]
    if ch not in face["glyphs"]:
        return 0.0
    return face["glyphs"][ch][0] * cap_px / face["cap"]


def text_width(s, cap_px, bold=False, spacing=0.0):
    tot = 0.0
    for ch in s:
        tot += char_advance(ch, cap_px, bold) + spacing
    return tot - spacing if s else 0.0


def draw_text(canvas, x, y_base, s, cap_px, color, bold=False, align="l", spacing=0.0):
    """Draw text with baseline at y_base (final-pixel coords, y down).
    color is a palette index (int). Returns the drawn width."""
    w = text_width(s, cap_px, bold, spacing)
    if align == "c":
        x -= w / 2.0
    elif align == "r":
        x -= w
    cx = x
    for ch in s:
        if ch not in fontdata.FACES["bold" if bold else "regular"]["glyphs"]:
            continue
        rows, gx0, gy0, adv = rasterize(ch, cap_px, bold)
        ox = int(round(cx)) + gx0
        oy = int(round(y_base)) + gy0
        for ry, row in enumerate(rows):
            ty = oy + ry
            if ty < 0 or ty >= canvas.H:
                continue
            arow = canvas.atext[ty]
            crow = canvas.ctext[ty]
            for rx, v in enumerate(row):
                if v == 0:
                    continue
                tx = ox + rx
                if tx < 0 or tx >= canvas.W:
                    continue
                if v > arow[tx]:
                    arow[tx] = v
                if v > 127:
                    crow[tx] = color
        cx += adv + spacing
    return w


def wrap_text(s, cap_px, max_w, bold=False, spacing=0.0):
    """Greedy word wrap; returns a list of lines."""
    words = s.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, cap_px, bold, spacing) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines
