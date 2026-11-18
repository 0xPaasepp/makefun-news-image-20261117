#!/usr/bin/env python3
"""Build-time only: simplify Natural Earth 110m country polygons (public
domain data) into a compact land-polygon data file for the entry.
Output: LAND = list of polygons; each polygon is a list of (lon, lat) pairs.
Two resolutions are kept in one list by storing detail points and letting
the renderer decimate further for the small world map."""
import json

SRC = "/tmp/countries.geo.json"
OUT = "/home/hatch/workspace/makefun/news-image-20261117/repo/land.py"


def decimate(ring, mind):
    """Keep points at least `mind` degrees apart (plus first/last)."""
    out = []
    lx = ly = None
    for x, y in ring:
        if lx is None or abs(x - lx) >= mind or abs(y - ly) >= mind:
            out.append((round(x, 2), round(y, 2)))
            lx, ly = x, y
    if out and out[0] != out[-1]:
        out.append(out[0])
    return out


def walk(geom, polys):
    t = geom["type"]
    if t == "Polygon":
        for ring in geom["coordinates"]:
            if len(ring) >= 4:
                polys.append(ring)
    elif t == "MultiPolygon":
        for poly in geom["coordinates"]:
            for ring in poly:
                if len(ring) >= 4:
                    polys.append(ring)


data = json.load(open(SRC))
polys = []
for feat in data["features"]:
    walk(feat["geometry"], polys)

# Drop Antarctica (south of -60) and keep everything else.
kept = []
for ring in polys:
    if all(y < -60 for _, y in ring):
        continue
    d = decimate(ring, 0.25)
    if len(d) >= 4:
        kept.append(d)

total_pts = sum(len(p) for p in kept)
with open(OUT, "w") as f:
    f.write("# Land polygons from Natural Earth 110m country data (public domain),\n")
    f.write("# simplified at build time. Runtime code only reads this data.\n\n")
    f.write("LAND = [\n")
    for p in kept:
        f.write("  %r,\n" % (p,))
    f.write("]\n")

print("wrote", OUT, "polygons:", len(kept), "points:", total_pts)
