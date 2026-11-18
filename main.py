# THE WORLD IN ONE DAY — Tuesday, 17 November 2026.
# Draws the front page with pure-stdlib code and writes /output/entry.png.
# v2: 41 stories, big condensed headlines (scale 3 tall) with one drawn
# pictogram per story, no deck lines except the lead.
# v3: stroke font (clean printed type) replaces the 5x7 pixel font.
# Headlines are cap 18, section headers cap 24, masthead cap 40.
import os
import sys

from draw import (Canvas, PAPER, INK, RED, NAVY, SKY, SEA, GREY, GOLD,
                  ORANGE, draw_text, text_w, text_block, encode_png)
from icons import draw_icon
from stories import LEAD_HEAD, LEAD_DECK, COLUMNS, story_count

W = 1024
H = 1024
MARGIN = 24
COL_W = 304
COL_X = [24, 360, 696]
BODY_TOP = 312
BODY_BOTTOM = 986
ICON = 24
ICON_GAP = 6
TEXT_X = ICON + ICON_GAP  # 30
STORY_GAP = 7


def draw_globe(cv, cx, cy, r):
    cv.circle(cx, cy, r, NAVY, fill=False)
    cv.hline(cx - r, cy, 2 * r, NAVY)
    cv.vline(cx, cy - r, 2 * r, NAVY)
    cv.line(cx - r + 6, cy - r + 8, cx + r - 6, cy + r - 8, NAVY)
    cv.line(cx + r - 6, cy - r + 8, cx - r + 6, cy + r - 8, NAVY)


def draw_bridge_scene(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    sea_y = y + int(h * 0.68)
    cv.rect(x, sea_y, w, h - int(h * 0.68), SEA)
    deck_y = y + int(h * 0.52)
    # explosion plume above the bridge centre
    mx = x + w // 2
    cv.circle(mx - 18, deck_y - 26, 14, ORANGE)
    cv.circle(mx + 6, deck_y - 34, 17, RED)
    cv.circle(mx + 26, deck_y - 22, 11, ORANGE)
    cv.circle(mx - 2, deck_y - 48, 12, GREY)
    cv.circle(mx + 18, deck_y - 52, 9, GREY)
    # towers and deck
    cv.rect(x + 60, deck_y - 58, 10, 58, INK)
    cv.rect(x + w - 70, deck_y - 58, 10, 58, INK)
    cv.rect(x, deck_y, w, 8, INK)
    cv.line(x + 65, deck_y - 58, mx, deck_y, INK)
    cv.line(x + w - 65, deck_y - 58, mx, deck_y, INK)
    cv.line(x + 65, deck_y - 58, x + 10, deck_y, INK)
    cv.line(x + w - 65, deck_y - 58, x + w - 10, deck_y, INK)
    # two ships on the water
    cv.poly([(x + 30, sea_y + 22), (x + 90, sea_y + 22),
             (x + 80, sea_y + 34), (x + 40, sea_y + 34)], INK)
    cv.vline(x + 60, sea_y + 6, 16, INK)
    cv.poly([(x + w - 110, sea_y + 30), (x + w - 40, sea_y + 30),
             (x + w - 50, sea_y + 42), (x + w - 100, sea_y + 42)], INK)
    cv.vline(x + w - 75, sea_y + 14, 16, INK)


def draw_tanker(cv, x, y, s):
    # s = icon size in px (about 30)
    cv.poly([(x, y + s - 8), (x + s, y + s - 8),
             (x + s - 6, y + s), (x + 6, y + s)], INK)
    cv.rect(x + 4, y + s - 20, 12, 12, RED)
    cv.rect(x + 18, y + s - 16, 8, 8, NAVY)
    cv.circle(x + s - 8, y + 4, 4, ORANGE)
    cv.circle(x + s - 4, y + 8, 3, RED)


def draw_cyclone(cv, x, y, r):
    for k, rr in enumerate((r, r - 4, r - 8)):
        cv.circle(x + k * 2, y + k, rr, NAVY, fill=False)
    cv.circle(x, y, 3, RED)


def draw_chip(cv, x, y, s):
    cv.rect(x + 5, y + 5, s - 10, s - 10, INK)
    cv.rect(x + 9, y + 9, s - 18, s - 18, GOLD)
    for i in range(3):
        d = 9 + i * 8
        cv.rect(x + d, y, 3, 5, INK)
        cv.rect(x + d, y + s - 5, 3, 5, INK)
        cv.rect(x, y + d, 5, 3, INK)
        cv.rect(x + s - 5, y + d, 5, 3, INK)


ICONS = {'tanker': draw_tanker, 'cyclone': draw_cyclone, 'chip': draw_chip}


def masthead(cv):
    draw_globe(cv, 56, 48, 26)
    title = "THE WORLD IN ONE DAY"
    tw = text_w(title, 40)
    draw_text(cv, (W - tw) // 2, 24, title, 40, INK, thick=3)
    cv.hline(MARGIN, 80, W - 2 * MARGIN, RED, thick=4)
    date = "TUESDAY, 17 NOVEMBER 2026"
    dw = text_w(date, 28)
    draw_text(cv, (W - dw) // 2, 92, date, 28, INK, thick=3)
    strap = "41 STORIES · SIX CONTINENTS · ONE DAY"
    sw = text_w(strap, 14)
    draw_text(cv, (W - sw) // 2, 130, strap, 14, NAVY, thick=2)
    cv.hline(MARGIN, 152, W - 2 * MARGIN, INK, thick=2)


def lead(cv):
    draw_text(cv, MARGIN, 162, "LEAD STORY", 14, RED, thick=2)
    y = 184
    y += text_block(cv, MARGIN, y, LEAD_HEAD, 540, 28, INK, thick=3,
                    pitch=40)
    y += 4
    y += text_block(cv, MARGIN, y, LEAD_DECK, 620, 14, INK, thick=2,
                    pitch=20)
    draw_bridge_scene(cv, 668, 164, 328, 128)
    return y


def section_header(cv, x, y, title, icon):
    draw_text(cv, x, y, title, 24, NAVY, thick=3)
    if icon and icon in ICONS:
        fn = ICONS[icon]
        if icon == 'cyclone':
            fn(cv, x + COL_W - 16, y + 10, 11)
        else:
            fn(cv, x + COL_W - 30, y - 2, 30)
    cv.hline(x, y + 30, COL_W, NAVY, thick=2)
    return 34


def story(cv, x, y, headline, icon):
    draw_icon(cv, x, y, icon)
    h = text_block(cv, x + TEXT_X, y, headline, COL_W - TEXT_X, 19,
                   INK, thick=2, pitch=28)
    return max(ICON, h) + STORY_GAP


def columns(cv, top):
    heights = []
    for ci, sections in enumerate(COLUMNS):
        x = COL_X[ci]
        y = top
        for title, icon, stories in sections:
            y += section_header(cv, x, y, title, icon)
            for headline, icon in stories:
                y += story(cv, x, y, headline, icon)
        heights.append(y - top)
        if y > BODY_BOTTOM:
            print("OVERFLOW col %d by %d px" % (ci, y - BODY_BOTTOM),
                  file=sys.stderr)
    return heights


def footer(cv):
    cv.hline(MARGIN, 990, W - 2 * MARGIN, INK, thick=2)
    line = "As reported on 17 November 2026"
    lw = text_w(line, 14)
    draw_text(cv, (W - lw) // 2, 998, line, 14, GREY, thick=2)


def build():
    cv = Canvas(W, H)
    masthead(cv)
    end = lead(cv)
    cv.hline(MARGIN, end + 8, W - 2 * MARGIN, INK, thick=2)
    heights = columns(cv, end + 20)
    footer(cv)
    return cv, heights


def main():
    cv, heights = build()
    print("stories:", story_count(), "| column heights:", heights)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(encode_png(cv))
    print("wrote", path)


if __name__ == "__main__":
    main()
