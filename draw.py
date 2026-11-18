"""Canvas: 2x supersampled shape layer + 1x text layer, palette colors.

Shape layer: polygons/lines drawn at 2048 into a binary alpha buffer, and
at 1024 into a palette-index color buffer. Downsampling the alpha buffer
gives smooth shape edges. Text is drawn separately at 1024 with analytic
anti-aliasing (see font.py).
"""

import math

PAPER = (247, 243, 232)
PALETTE = {
    0: PAPER,
    1: (17, 17, 17),      # ink
    2: (192, 32, 32),     # red
    3: (30, 79, 160),     # blue
    4: (46, 125, 50),     # green
    5: (208, 96, 0),      # orange
    6: (222, 196, 150),   # land tan
    7: (178, 214, 232),   # sea blue
    8: (200, 225, 240),   # pale sea
    9: (30, 60, 110),     # dark blue
    10: (120, 120, 115),  # grey
    11: (240, 200, 60),   # yellow
    12: (255, 255, 255),  # white
    13: (140, 20, 20),    # dark red
    14: (235, 220, 190),  # light tan
    15: (90, 140, 90),    # muted green
    16: (60, 60, 60),     # dark grey
}

INK, RED, BLUE, GREEN, ORANGE = 1, 2, 3, 4, 5
LAND, SEA, PALESEA, DBLUE = 6, 7, 8, 9
GREY, YELLOW, WHITE, DRED, LTAN = 10, 11, 12, 13, 14

S = 2  # supersample factor for shapes


class Canvas:
    def __init__(self, w=1024, h=1024):
        self.W, self.H = w, h
        self.ashape = [bytearray(w * S) for _ in range(h * S)]
        self.cshape = [bytearray(w) for _ in range(h)]
        self.atext = [bytearray(w) for _ in range(h)]
        self.ctext = [bytearray(w) for _ in range(h)]

    # ---- scanline polygon fill (works on any bytearray-row buffer)
    def _fill_poly_rows(self, rows, pts, value, scale):
        # pts: list of (x, y) in the buffer's own pixel coords
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        y0 = max(0, int(math.floor(min(ys))))
        y1 = min(len(rows) - 1, int(math.ceil(max(ys))))
        n = len(pts)
        for y in range(y0, y1 + 1):
            yc = y + 0.5
            xs = []
            for i in range(n):
                x1, y1p = pts[i]
                x2, y2p = pts[(i + 1) % n]
                if (y1p <= yc < y2p) or (y2p <= yc < y1p):
                    t = (yc - y1p) / (y2p - y1p)
                    xs.append(x1 + t * (x2 - x1))
            xs.sort()
            row = rows[y]
            for i in range(0, len(xs) - 1, 2):
                xa = max(0, int(math.ceil(xs[i])))
                xb = min(len(row) - 1, int(math.floor(xs[i + 1])))
                if xb >= xa:
                    row[xa:xb + 1] = bytes([value]) * (xb - xa + 1)

    def fill_poly(self, pts, color):
        """pts in final-pixel coords. Fills at 2x into ashape, 1x into cshape."""
        pts2 = [(x * S, y * S) for (x, y) in pts]
        self._fill_poly_rows(self.ashape, pts2, 255, S)
        self._fill_poly_rows(self.cshape, list(pts), color, 1)

    def fill_rect(self, x, y, w, h, color):
        self.fill_poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], color)

    def fill_circle(self, cx, cy, r, color, n=28):
        pts = []
        for i in range(n):
            a = 2.0 * math.pi * i / n
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        self.fill_poly(pts, color)

    def ring(self, cx, cy, r, width, color):
        # ring as filled circle minus inner circle: draw outer, then erase
        # inner with paper-colored alpha hole is complex; instead draw as
        # a thick stroked circle via polygon segments.
        n = 28
        outer = []
        inner = []
        for i in range(n + 1):
            a = 2.0 * math.pi * i / n
            outer.append((cx + (r + width / 2) * math.cos(a), cy + (r + width / 2) * math.sin(a)))
            inner.append((cx + (r - width / 2) * math.cos(a), cy + (r - width / 2) * math.sin(a)))
        # build a closed quad-strip polygon: outer forward, inner backward
        poly = outer + inner[::-1]
        self.fill_poly(poly, color)

    def thick_line(self, x1, y1, x2, y2, width, color):
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        if L < 0.01:
            self.fill_circle(x1, y1, width / 2, color)
            return
        nx, ny = -dy / L * width / 2, dx / L * width / 2
        self.fill_poly([(x1 + nx, y1 + ny), (x2 + nx, y2 + ny),
                        (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)], color)
        self.fill_circle(x1, y1, width / 2, color)
        self.fill_circle(x2, y2, width / 2, color)

    def line(self, x1, y1, x2, y2, width, color):
        self.thick_line(x1, y1, x2, y2, width, color)

    # ---- downsample + compose
    def _downsample(self, rows2):
        w, h = self.W, self.H
        out = []
        for y in range(h):
            r0 = rows2[2 * y]
            r1 = rows2[2 * y + 1]
            orow = bytearray(w)
            for x in range(w):
                orow[x] = (r0[2 * x] + r0[2 * x + 1] + r1[2 * x] + r1[2 * x + 1] + 2) >> 2
            out.append(orow)
        return out

    def render_rgb(self):
        ashape1 = self._downsample(self.ashape)
        W, H = self.W, self.H
        pal = PALETTE
        paper = PAPER
        raw = bytearray()
        for y in range(H):
            raw.append(0)
            sa = ashape1[y]
            sc = self.cshape[y]
            ta = self.atext[y]
            tc = self.ctext[y]
            for x in range(W):
                a = sa[x]
                if a:
                    col = pal[sc[x]] if sc[x] else paper
                    if a == 255:
                        r, g, b = col
                    else:
                        r = (paper[0] * (255 - a) + col[0] * a) // 255
                        g = (paper[1] * (255 - a) + col[1] * a) // 255
                        b = (paper[2] * (255 - a) + col[2] * a) // 255
                else:
                    r, g, b = paper
                t = ta[x]
                if t:
                    col = pal[tc[x]] if tc[x] else pal[INK]
                    if t == 255:
                        r, g, b = col
                    else:
                        r = (r * (255 - t) + col[0] * t) // 255
                        g = (g * (255 - t) + col[1] * t) // 255
                        b = (b * (255 - t) + col[2] * t) // 255
                raw.append(r)
                raw.append(g)
                raw.append(b)
        return bytes(raw)


# ------------------------------------------------------------------- flags

def flag_rect(cv, x, y, w, h, stripes, canton=None):
    """stripes: list of colors top->bottom (equal height). canton: (color, w, h)."""
    n = len(stripes)
    for i, col in enumerate(stripes):
        cv.fill_rect(x, y + i * h / n, w, h / n + 0.6, col)
    if canton:
        ccol, cw, ch = canton
        cv.fill_rect(x, y, cw, ch, ccol)


def flag_us(cv, x, y, w, h):
    flag_rect(cv, x, y, w, h, [DRED, WHITE] * 7, canton=(DBLUE, w * 0.4, h * 7 / 13))
    # stars as tiny dots
    for r in range(4):
        for cix in range(5):
            cv.fill_circle(x + w * 0.05 + cix * w * 0.07, y + h * 0.08 + r * h * 0.14, max(0.8, w * 0.012), WHITE)


def flag_jp(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.fill_circle(x + w / 2, y + h / 2, h * 0.3, DRED)


def flag_in(cv, x, y, w, h):
    flag_rect(cv, x, y, w, h, [5, WHITE, 4])
    cv.ring(x + w / 2, y + h / 2, h * 0.16, max(1.0, h * 0.04), DBLUE)


def flag_au(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, DBLUE)
    cv.fill_rect(x, y, w * 0.5, h * 0.5, DBLUE)
    cv.thick_line(x, y, x + w * 0.5, y + h * 0.5, max(1.0, h * 0.08), WHITE)
    cv.thick_line(x + w * 0.5, y, x, y + h * 0.5, max(1.0, h * 0.08), WHITE)
    cv.fill_circle(x + w * 0.8, y + h * 0.3, h * 0.07, WHITE)
    cv.fill_circle(x + w * 0.65, y + h * 0.7, h * 0.07, WHITE)
    cv.fill_circle(x + w * 0.85, y + h * 0.75, h * 0.07, WHITE)


def flag_cn(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, DRED)
    cv.fill_circle(x + w * 0.18, y + h * 0.28, h * 0.12, YELLOW)
    for sx, sy in ((0.38, 0.12), (0.46, 0.28), (0.46, 0.46), (0.38, 0.60)):
        cv.fill_circle(x + w * sx, y + h * sy, h * 0.05, YELLOW)


def flag_ru(cv, x, y, w, h):
    flag_rect(cv, x, y, w, h, [WHITE, BLUE, DRED])


def flag_ua(cv, x, y, w, h):
    flag_rect(cv, x, y, w, h, [BLUE, YELLOW])


# ------------------------------------------------------------------- icons
# Each icon draws inside a box (x, y, s) where s is the box size in px.

def _star(cv, cx, cy, r, color, points=8):
    pts = []
    for i in range(points * 2):
        a = math.pi * i / points - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    cv.fill_poly(pts, color)


def icon(cv, name, x, y, s, color):
    u = s / 28.0
    cx, cy = x + s / 2, y + s / 2
    if name == "boom":
        _star(cv, cx, cy, 12 * u, 5)
        _star(cv, cx, cy, 6 * u, 11)
    elif name == "flag":
        cv.thick_line(x + 8 * u, y + 3 * u, x + 8 * u, y + 25 * u, 2 * u, color)
        cv.fill_poly([(x + 8 * u, y + 3 * u), (x + 23 * u, y + 7 * u), (x + 8 * u, y + 12 * u)], RED)
    elif name == "ball":
        cv.fill_circle(cx, cy, 11 * u, color)
        cv.fill_circle(cx, cy, 4 * u, WHITE)
    elif name == "trophy":
        cv.fill_poly([(x + 8 * u, y + 4 * u), (x + 20 * u, y + 4 * u), (x + 18 * u, y + 15 * u), (x + 10 * u, y + 15 * u)], color)
        cv.thick_line(x + 14 * u, y + 15 * u, x + 14 * u, y + 21 * u, 2.5 * u, color)
        cv.fill_rect(x + 9 * u, y + 21 * u, 10 * u, 3 * u, color)
    elif name == "chart":
        for i, h in enumerate((8, 14, 10, 18)):
            cv.fill_rect(x + (4 + i * 6) * u, y + (24 - h) * u, 4 * u, h * u, color)
    elif name == "coin":
        cv.fill_circle(cx, cy, 11 * u, color)
        cv.ring(cx, cy, 8 * u, 1.5 * u, WHITE)
    elif name == "chip":
        cv.fill_rect(x + 7 * u, y + 7 * u, 14 * u, 14 * u, color)
        cv.fill_rect(x + 11 * u, y + 11 * u, 6 * u, 6 * u, WHITE)
        for i in range(3):
            cv.fill_rect(x + (9 + i * 5) * u, y + 3 * u, 2 * u, 4 * u, color)
            cv.fill_rect(x + (9 + i * 5) * u, y + 21 * u, 2 * u, 4 * u, color)
    elif name == "bolt":
        cv.fill_poly([(x + 16 * u, y + 2 * u), (x + 8 * u, y + 15 * u), (x + 13 * u, y + 15 * u),
                      (x + 11 * u, y + 26 * u), (x + 20 * u, y + 12 * u), (x + 15 * u, y + 12 * u)], color)
    elif name == "warn":
        cv.fill_poly([(x + 14 * u, y + 3 * u), (x + 26 * u, y + 24 * u), (x + 2 * u, y + 24 * u)], color)
        cv.fill_rect(x + 13 * u, y + 10 * u, 2 * u, 8 * u, WHITE)
        cv.fill_circle(cx, y + 21 * u, 1.4 * u, WHITE)
    elif name == "bank":
        cv.fill_poly([(x + 2 * u, y + 12 * u), (x + 14 * u, y + 4 * u), (x + 26 * u, y + 12 * u)], color)
        for i in range(4):
            cv.fill_rect(x + (5 + i * 6) * u, y + 14 * u, 2.5 * u, 8 * u, color)
        cv.fill_rect(x + 3 * u, y + 23 * u, 22 * u, 2.5 * u, color)
    elif name == "ship":
        cv.fill_poly([(x + 4 * u, y + 14 * u), (x + 24 * u, y + 14 * u), (x + 20 * u, y + 22 * u), (x + 8 * u, y + 22 * u)], color)
        cv.fill_rect(x + 12 * u, y + 6 * u, 4 * u, 8 * u, color)
    elif name == "globe":
        cv.fill_circle(cx, cy, 11 * u, color)
        cv.ring(cx, cy, 11 * u, 1.2 * u, WHITE)
        cv.thick_line(x + 3 * u, cy, x + 25 * u, cy, 1.2 * u, WHITE)
        cv.fill_poly([(x + 10 * u, y + 4 * u), (x + 13 * u, y + 4 * u), (x + 13 * u, y + 24 * u), (x + 10 * u, y + 24 * u)], WHITE)
    elif name == "leaf":
        cv.fill_poly([(x + 5 * u, y + 20 * u), (x + 5 * u, y + 10 * u), (x + 14 * u, y + 4 * u),
                      (x + 23 * u, y + 10 * u), (x + 23 * u, y + 20 * u)], color)
        cv.thick_line(x + 14 * u, y + 6 * u, x + 14 * u, y + 24 * u, 1.5 * u, WHITE)
    elif name == "court":
        cv.thick_line(x + 6 * u, y + 8 * u, x + 20 * u, y + 16 * u, 4 * u, color)
        cv.thick_line(x + 18 * u, y + 16 * u, x + 24 * u, y + 24 * u, 2 * u, color)
        cv.fill_rect(x + 4 * u, y + 23 * u, 12 * u, 2.5 * u, color)
    elif name == "medal":
        cv.fill_circle(cx, y + 17 * u, 8 * u, color)
        cv.fill_circle(cx, y + 17 * u, 3.5 * u, WHITE)
        cv.thick_line(x + 10 * u, y + 4 * u, x + 14 * u, y + 11 * u, 2 * u, RED)
        cv.thick_line(x + 18 * u, y + 4 * u, x + 14 * u, y + 11 * u, 2 * u, RED)
    elif name == "plane":
        cv.fill_poly([(x + 14 * u, y + 3 * u), (x + 18 * u, y + 12 * u), (x + 25 * u, y + 14 * u),
                      (x + 17 * u, y + 16 * u), (x + 15 * u, y + 25 * u), (x + 12 * u, y + 25 * u),
                      (x + 11 * u, y + 16 * u), (x + 3 * u, y + 14 * u), (x + 10 * u, y + 12 * u)], color)
    elif name == "flame":
        cv.fill_poly([(x + 14 * u, y + 2 * u), (x + 20 * u, y + 12 * u), (x + 23 * u, y + 18 * u),
                      (x + 18 * u, y + 25 * u), (x + 9 * u, y + 25 * u), (x + 5 * u, y + 18 * u),
                      (x + 8 * u, y + 12 * u)], color)
    elif name == "doc":
        cv.fill_poly([(x + 7 * u, y + 3 * u), (x + 19 * u, y + 3 * u), (x + 21 * u, y + 6 * u),
                      (x + 21 * u, y + 25 * u), (x + 7 * u, y + 25 * u)], color)
        cv.fill_rect(x + 10 * u, y + 8 * u, 8 * u, 2 * u, WHITE)
        cv.fill_rect(x + 10 * u, y + 13 * u, 8 * u, 2 * u, WHITE)
        cv.fill_rect(x + 10 * u, y + 18 * u, 5 * u, 2 * u, WHITE)
    elif name == "health":
        cv.fill_rect(x + 11 * u, y + 4 * u, 6 * u, 20 * u, color)
        cv.fill_rect(x + 4 * u, y + 11 * u, 20 * u, 6 * u, color)
    elif name == "star":
        _star(cv, cx, cy, 11 * u, color)
    elif name == "music":
        cv.fill_circle(x + 8 * u, y + 21 * u, 3.5 * u, color)
        cv.fill_circle(x + 20 * u, y + 19 * u, 3.5 * u, color)
        cv.thick_line(x + 11 * u, y + 20 * u, x + 11 * u, y + 5 * u, 2 * u, color)
        cv.thick_line(x + 23 * u, y + 18 * u, x + 23 * u, y + 3 * u, 2 * u, color)
        cv.thick_line(x + 11 * u, y + 5 * u, x + 23 * u, y + 3 * u, 2 * u, color)
    else:  # dot fallback
        cv.fill_circle(cx, cy, 5 * u, color)
