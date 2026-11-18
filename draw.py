# Canvas + drawing primitives + PNG encoder. Pure stdlib only.
import struct
import zlib

from font import FONT, normalize

PAPER = (0xF7, 0xF3, 0xEA)
INK = (0x1A, 0x1A, 0x1A)
RED = (0xB9, 0x1C, 0x1C)
NAVY = (0x1E, 0x3A, 0x5F)
SKY = (0xBF, 0xD9, 0xE8)
SEA = (0x2C, 0x5F, 0x7C)
GREY = (0x6B, 0x6B, 0x6B)
GOLD = (0xC8, 0x96, 0x2E)
ORANGE = (0xE8, 0x6A, 0x1B)


class Canvas:
    def __init__(self, width, height, bg=PAPER):
        self.w = width
        self.h = height
        self.buf = bytearray(width * height * 3)
        for i in range(0, len(self.buf), 3):
            self.buf[i] = bg[0]
            self.buf[i + 1] = bg[1]
            self.buf[i + 2] = bg[2]

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, color)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0, y0, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if fill:
                    if d <= r * r:
                        self.px(xx, yy, color)
                else:
                    if r * r - 2 * r <= d <= r * r:
                        self.px(xx, yy, color)

    def poly(self, pts, color):
        # scanline fill for a simple polygon
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.px(x, y, color)


def char_w(scale):
    return 6 * scale


def text_w(text, scale):
    return len(normalize(text)) * char_w(scale)


def draw_text(cv, x, y, text, scale, color, bold=False):
    """Draw one line at (x, y) top-left. Returns width drawn."""
    text = normalize(text)
    cx = x
    off = max(1, scale // 2) if bold else 0
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            cx += char_w(scale)
            continue
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    for dy in range(scale):
                        for dx in range(scale):
                            cv.px(cx + col * scale + dx, y + row * scale + dy, color)
                            if bold:
                                cv.px(cx + col * scale + dx + off,
                                      y + row * scale + dy, color)
        cx += char_w(scale)
    return cx - x


def wrap(text, max_chars):
    """Greedy word wrap. Returns a list of lines, each <= max_chars."""
    words = normalize(text).split(' ')
    lines = []
    cur = ''
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += ' ' + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(cv, x, y, text, max_w, scale, color, bold=False, pitch=None):
    """Wrapped text block. Returns the height used in px."""
    if pitch is None:
        pitch = 7 * scale + 3
    max_chars = max(1, max_w // char_w(scale))
    lines = wrap(text, max_chars)
    yy = y
    for ln in lines:
        draw_text(cv, x, yy, ln, scale, color, bold=bold)
        yy += pitch
    return yy - y


def _chunk(kind, data):
    out = struct.pack('>I', len(data)) + kind + data
    out += struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 9)
    png = b'\x89PNG\r\n\x1a\n'
    png += _chunk(b'IHDR', ihdr)
    png += _chunk(b'IDAT', idat)
    png += _chunk(b'IEND', b'')
    return png
