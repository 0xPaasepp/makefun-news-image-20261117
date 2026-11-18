"""Build-time TTF outline extractor (stdlib only).

Reads a TrueType font file, extracts the ASCII glyph outlines (contours of
on/off-curve points, quadratic beziers) + advances + metrics, and writes
them as fontdata.py into the repo. The entry at runtime only uses the
embedded data -- no font file dependency.

Usage: python3 parse_ttf.py <bold.ttf> <regular.ttf> <out.py>
"""
import struct
import sys

CHARS = [chr(c) for c in range(32, 127)] + ["\u00b7"]  # printable ASCII + middot


def u16(b, o):
    return struct.unpack_from(">H", b, o)[0]


def i16(b, o):
    return struct.unpack_from(">h", b, o)[0]


def u32(b, o):
    return struct.unpack_from(">I", b, o)[0]


class TTF:
    def __init__(self, path):
        self.data = open(path, "rb").read()
        d = self.data
        n = u16(d, 4)
        self.tables = {}
        for i in range(n):
            o = 12 + i * 16
            tag = d[o:o + 4].decode("latin-1")
            self.tables[tag] = (u32(d, o + 8), u32(d, o + 12))
        head = self.tables["head"][0]
        self.upm = u16(d, head + 18)
        self.loc_fmt = i16(d, head + 50)
        self.num_glyphs = u16(d, self.tables["maxp"][0] + 4)
        hhea = self.tables["hhea"][0]
        self.ascent = i16(d, hhea + 4)
        self.descent = i16(d, hhea + 6)
        self.num_hmtx = u16(d, hhea + 34)
        # hmtx advances
        hm = self.tables["hmtx"][0]
        self.adv = []
        for i in range(self.num_glyphs):
            if i < self.num_hmtx:
                self.adv.append(u16(d, hm + i * 4))
            else:
                self.adv.append(self.adv[-1])
        # cmap: prefer format 12, else format 4
        self.cmap = {}
        cm = self.tables["cmap"][0]
        nt = u16(d, cm + 2)
        best4 = best12 = None
        for i in range(nt):
            o = cm + 4 + i * 8
            plat, enc, off = u16(d, o), u16(d, o + 2), u32(d, o + 4)
            fmt = u16(d, cm + off)
            if fmt == 12 and best12 is None:
                best12 = cm + off
            elif fmt == 4 and best4 is None:
                best4 = cm + off
        if best12 is not None:
            o = best12
            ng = u32(d, o + 12)
            for i in range(ng):
                go = o + 16 + i * 12
                s, e, g = u32(d, go), u32(d, go + 4), u32(d, go + 8)
                for c in range(s, e + 1):
                    self.cmap[c] = g + (c - s)
        elif best4 is not None:
            o = best4
            seg = u16(d, o + 6) // 2
            end_o = o + 14
            start_o = end_o + 2 * seg + 2
            delta_o = start_o + 2 * seg
            range_o = delta_o + 2 * seg
            for i in range(seg):
                end = u16(d, end_o + 2 * i)
                start = u16(d, start_o + 2 * i)
                delta = i16(d, delta_o + 2 * i)
                ro = u16(d, range_o + 2 * i)
                for c in range(start, end + 1):
                    if ro == 0:
                        g = (c + delta) & 0xFFFF
                    else:
                        go = range_o + 2 * i + ro + 2 * (c - start)
                        g = u16(d, go)
                        if g:
                            g = (g + delta) & 0xFFFF
                    if g:
                        self.cmap[c] = g
        # loca
        lo = self.tables["loca"][0]
        self.loca = []
        if self.loc_fmt == 0:
            for i in range(self.num_glyphs + 1):
                self.loca.append(u16(d, lo + 2 * i) * 2)
        else:
            for i in range(self.num_glyphs + 1):
                self.loca.append(u32(d, lo + 4 * i))
        # OS/2 cap height
        self.cap = None
        if "OS/2" in self.tables:
            o2, ln = self.tables["OS/2"]
            if ln >= 90:
                self.cap = i16(d, o2 + 88)
        self.glyph_cache = {}

    def glyph(self, gid):
        if gid in self.glyph_cache:
            return self.glyph_cache[gid]
        d = self.data
        go = self.tables["glyf"][0] + self.loca[gid]
        length = self.loca[gid + 1] - self.loca[gid]
        contours = []
        if length == 0:
            self.glyph_cache[gid] = contours
            return contours
        ncont = i16(d, go)
        if ncont >= 0:
            ends = [u16(d, go + 10 + 2 * i) for i in range(ncont)]
            ilen = u16(d, go + 10 + 2 * ncont)
            o = go + 12 + 2 * ncont + ilen
            npts = ends[-1] + 1 if ends else 0
            flags = []
            while len(flags) < npts:
                f = d[o]
                o += 1
                flags.append(f)
                if f & 0x08:
                    rep = d[o]
                    o += 1
                    flags.extend([f] * rep)
            xs = []
            x = 0
            for f in flags:
                if f & 0x02:
                    dx = d[o]
                    o += 1
                    if not (f & 0x10):
                        dx = -dx
                    x += dx
                elif f & 0x10:
                    pass
                else:
                    x += i16(d, o)
                    o += 2
                xs.append(x)
            ys = []
            y = 0
            for f in flags:
                if f & 0x04:
                    dy = d[o]
                    o += 1
                    if not (f & 0x20):
                        dy = -dy
                    y += dy
                elif f & 0x20:
                    pass
                else:
                    y += i16(d, o)
                    o += 2
                ys.append(y)
            pts = [(xs[i], ys[i], 1 if (flags[i] & 0x01) else 0) for i in range(npts)]
            start = 0
            for e in ends:
                contours.append(pts[start:e + 1])
                start = e + 1
        else:
            # composite glyph
            o = go + 10
            while True:
                flags = u16(d, o)
                comp = u16(d, o + 2)
                o += 4
                if flags & 0x0001:
                    if flags & 0x0002:
                        ax, ay = i16(d, o), i16(d, o + 2)
                        o += 4
                    else:
                        ax, ay = d[o], d[o + 1]
                        o += 2
                else:
                    ax = ay = 0
                # transform
                if flags & 0x0008:
                    s = struct.unpack_from(">h", d, o)[0] / 16384.0
                    o += 2
                    m = (s, 0.0, 0.0, s)
                elif flags & 0x0040:
                    sx = struct.unpack_from(">h", d, o)[0] / 16384.0
                    sy = struct.unpack_from(">h", d, o + 2)[0] / 16384.0
                    o += 4
                    m = (sx, 0.0, 0.0, sy)
                elif flags & 0x0080:
                    m = tuple(struct.unpack_from(">h", d, o + 2 * i)[0] / 16384.0 for i in range(4))
                    o += 8
                else:
                    m = (1.0, 0.0, 0.0, 1.0)
                for contour in self.glyph(comp):
                    nc = []
                    for (px, py, on) in contour:
                        nx = m[0] * px + m[2] * py + ax
                        ny = m[1] * px + m[3] * py + ay
                        nc.append((int(round(nx)), int(round(ny)), on))
                    contours.append(nc)
                if not (flags & 0x0020):
                    break
        self.glyph_cache[gid] = contours
        return contours

    def extract(self):
        glyphs = {}
        for ch in CHARS:
            gid = self.cmap.get(ord(ch))
            if gid is None:
                continue
            contours = self.glyph(gid)
            # drop empty contours
            contours = [c for c in contours if len(c) >= 2]
            glyphs[ch] = (self.adv[gid], contours)
        cap = self.cap
        if not cap:
            gid = self.cmap.get(ord("H"))
            cs = self.glyph(gid)
            ys = [p[1] for c in cs for p in c]
            cap = max(ys) if ys else self.upm
        return {"upm": self.upm, "cap": cap, "ascent": self.ascent,
                "descent": self.descent, "glyphs": glyphs}


def emit(face, path):
    with open(path, "w") as f:
        f.write("# Glyph outlines extracted at build time from a freely licensed\n")
        f.write("# font (see README for the source). Runtime code only reads this data.\n\n")
        f.write("FACES = {\n")
        for name, data in face.items():
            f.write("  %r: {\n    'upm': %d, 'cap': %d, 'ascent': %d, 'descent': %d,\n    'glyphs': {\n" % (
                name, data["upm"], data["cap"], data["ascent"], data["descent"]))
            for ch, (adv, contours) in sorted(data["glyphs"].items()):
                f.write("      %r: (%d, [" % (ch, adv))
                parts = []
                for c in contours:
                    parts.append("[" + ",".join("(%d,%d,%d)" % p for p in c) + "]")
                f.write(",".join(parts))
                f.write("]),\n")
            f.write("    },\n  },\n")
        f.write("}\n")
    print("wrote", path)


if __name__ == "__main__":
    bold = TTF(sys.argv[1]).extract()
    reg = TTF(sys.argv[2]).extract()
    emit({"bold": bold, "regular": reg}, sys.argv[3])
    for name, data in (("bold", bold), ("regular", reg)):
        print(name, "upm", data["upm"], "cap", data["cap"], "ascent", data["ascent"],
              "descent", data["descent"], "glyphs", len(data["glyphs"]))
        missing = [c for c in CHARS if c not in data["glyphs"]]
        print("  missing:", missing)
