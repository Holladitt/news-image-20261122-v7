#!/usr/bin/env python3
"""news-image-20261122 v7 — The World in One Day, Sunday 22 November 2026.
Draws one 1024x1024 broadsheet PNG to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).
Stdlib + Pillow only, no network, no clock, no randomness without a fixed seed:
running twice gives byte-identical output.
Design: top-1 skeleton (giant serif date, numbers strip, region bar, UTC strip,
3 labelled scene leads, 12 scene secondaries, dark dotted map, ALSO list,
red DATE CHECK, readable legend footer) with v6's verified stories, honest
COP31 framing, and every v6 defect fixed.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 242, 231)
PAPER = (250, 246, 236)
NAVY = (16, 36, 68)
NAVY2 = (24, 52, 92)
RED = (178, 34, 34)
DARKRED = (139, 21, 21)
INK = (24, 24, 24)
GREY = (90, 90, 90)
TEAL = (15, 118, 110)
GREEN = (30, 122, 70)
GOLD = (212, 175, 55)
ORANGE = (180, 83, 9)
BLUE = (29, 78, 216)
PURPLE = (109, 40, 217)
LIGHTMAP = (18, 42, 74)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIFB = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIFI = "/usr/share/fonts/truetype/noto/NotoSerif-BoldItalic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_fonts = {}


def F(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def fit(path, text, start, maxw):
    """Largest size <= start whose text fits maxw."""
    s = start
    while s > 6:
        f = F(path, s)
        if f.getlength(text) <= maxw:
            return f
        s -= 1
    return F(path, 6)


def wrap(text, font, width):
    lines, cur = [], ""
    for word in text.split(" "):
        t = (cur + " " + word).strip()
        if font.getlength(t) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text(d, xy, s, font, fill, anchor="la"):
    d.text(xy, s, font=font, fill=fill, anchor=anchor)


def chip(d, x, y, s, bg, fg=(255, 255, 255), size=11, pad=4):
    """Small label chip; returns its width."""
    f = F(SANSB, size)
    w = int(f.getlength(s)) + pad * 2
    h = size + pad + 1
    d.rounded_rectangle([x, y, x + w, y + h], radius=2, fill=bg)
    d.text((x + pad, y + 2), s, font=f, fill=fg)
    return w


TAGC = {
    "CONFIRMED": GREEN,
    "REPORTED": TEAL,
    "CLAIM": RED,
    "ONGOING": ORANGE,
    "PENDING": BLUE,
    "FORECAST": PURPLE,
}


def tag(d, x, y, s, size=10):
    return chip(d, x, y, s, TAGC[s], size=size)


def stars(d, box, seed, n=14, color=(255, 255, 255)):
    r = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x = r.randint(x0 + 2, x1 - 2)
        y = r.randint(y0 + 2, y1 - 2)
        d.point((x, y), fill=color)


def skyline(d, box, seed, lit=0.55, base=None):
    """Night skyline: dark blocks with lit windows. box=(x0,y0,x1,y1)."""
    r = random.Random(seed)
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(10, 18, 36))
    x = x0
    while x < x1:
        bw = r.randint(14, 30)
        bh = r.randint(18, int((y1 - y0) * 0.75))
        by = y1 - bh
        d.rectangle([x, by, min(x + bw, x1), y1], fill=(16, 26, 48))
        for wy in range(by + 4, y1 - 4, 8):
            for wx in range(x + 3, min(x + bw, x1) - 3, 7):
                if r.random() < lit:
                    d.rectangle([wx, wy, wx + 3, wy + 4],
                                fill=(255, 214, 130) if r.random() < 0.7 else (180, 220, 255))
        x += bw + r.randint(0, 4)
    if base is not None:
        d.rectangle([x0, y1 - 4, x1, y1], fill=base)


def flames(d, x, y, s, seed=7):
    """Small flame cluster centred at (x, y), scale s. No big discs."""
    r = random.Random(seed)
    for _ in range(7):
        fx = x + r.randint(-int(s * 0.7), int(s * 0.7))
        fh = r.randint(int(s * 0.8), int(s * 1.6))
        fw = r.randint(3, max(4, int(s * 0.4)))
        col = r.choice([(255, 120, 20), (255, 170, 40), (230, 60, 20)])
        d.polygon([(fx - fw, y), (fx + fw, y), (fx, y - fh)], fill=col)


def smoke(d, x, y, s, seed=11):
    r = random.Random(seed)
    for i in range(5):
        r0 = int(s * (0.4 + i * 0.22))
        d.ellipse([x - r0 + i * 3, y - i * int(s * 0.5) - r0,
                   x + r0 + i * 3, y - i * int(s * 0.5) + r0],
                  fill=(120, 120, 120))

# ---------------- lead scenes ----------------

def scene_cop31(d, box, variant=1):
    """COP31 hall, frame fully filled: flags, table, delegates, globe, clock, document."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(196, 164, 120))           # warm hall wall
    d.rectangle([x0, y0, x1, y0 + int(h * 0.30)], fill=(222, 196, 150))
    # bunting flags along the top
    cols = [(178, 34, 34), (16, 36, 68), (30, 122, 70), (212, 175, 55), (120, 60, 140)]
    for i in range(9):
        fx = x0 + 8 + i * int((w - 16) / 8)
        d.polygon([(fx, y0 + 4), (fx + 14, y0 + 4), (fx + 7, y0 + 18)], fill=cols[i % 5])
    # globe (left) and clock (right) on the wall
    d.ellipse([x0 + 14, y0 + 26, x0 + 52, y0 + 64], fill=(70, 130, 180))
    d.ellipse([x0 + 22, y0 + 32, x0 + 44, y0 + 58], fill=(90, 170, 90))
    d.ellipse([x1 - 52, y0 + 26, x1 - 14, y0 + 64], fill=(250, 246, 236))
    d.ellipse([x1 - 52, y0 + 26, x1 - 14, y0 + 64], outline=NAVY, width=2)
    d.line([x1 - 33, y0 + 45, x1 - 33, y0 + 32], fill=NAVY, width=2)
    d.line([x1 - 33, y0 + 45, x1 - 22, y0 + 50], fill=NAVY, width=2)
    # long table
    ty = y0 + int(h * 0.62)
    d.rectangle([x0 + 6, ty, x1 - 6, y1 - 6], fill=(120, 72, 32))
    d.rectangle([x0 + 6, ty, x1 - 6, ty + 6], fill=(150, 96, 48))
    # delegates behind the table (v2: fewer, bigger figures)
    skin = [(222, 184, 150), (190, 140, 100), (240, 200, 170)]
    suits = [(16, 36, 68), (178, 34, 34), (30, 122, 70), (90, 60, 20), (60, 60, 60)]
    ndel = 5 if variant == 2 else 7
    for i in range(ndel):
        cx = x0 + 30 + i * int((w - 60) / max(1, ndel - 1))
        r = 12 if variant == 2 else 9
        d.ellipse([cx - r, ty - 38, cx + r, ty - 16], fill=skin[i % 3])
        d.polygon([(cx - 16, ty - 16), (cx + 16, ty - 16), (cx + 19, ty + 2), (cx - 19, ty + 2)],
                  fill=suits[i % 5])
        d.rectangle([cx - 2, ty - 16, cx + 2, ty + 2], fill=(250, 246, 236))
    # name plates in front of each delegate
    for i in range(ndel):
        cx = x0 + 30 + i * int((w - 60) / max(1, ndel - 1)) if variant == 2 else x0 + 26 + i * int((w - 52) / 6)
        d.rectangle([cx - 12, ty + 8, cx + 12, ty + 18], fill=(250, 246, 236))
    # draft document on the table + NO DEAL stamp, raised off the frame edge
    d.rectangle([x0 + int(w * 0.42), ty + 8, x0 + int(w * 0.58), y1 - 22], fill=(250, 246, 236))
    for j in range(3):
        d.line([x0 + int(w * 0.44), ty + 14 + j * 6, x0 + int(w * 0.56), ty + 14 + j * 6],
               fill=(120, 120, 120), width=1)
    d.rectangle([x1 - 92, ty + 22, x1 - 12, ty + 38], outline=RED, width=2)
    d.text((x1 - 88, ty + 23), "NO DEAL", font=F(SANSB, 11), fill=RED)


def scene_bahrain(d, box, variant=1):
    """Bahrain night: radar dome + mast, Patriot launcher, missile trails, lit skyline."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(12, 20, 44))
    stars(d, box, 21, 18)
    d.ellipse([x1 - 30, y0 + 6, x1 - 12, y0 + 24], fill=(240, 236, 210))  # small moon
    # radar dome centre-left
    cx, cy = x0 + int(w * 0.42), y0 + int(h * 0.52)
    d.rectangle([cx - 3, cy - 34, cx + 3, cy + 10], fill=(160, 160, 160))
    d.line([cx, cy - 34, cx + 12, cy - 46], fill=(200, 200, 200), width=2)
    d.pieslice([cx - 34, cy - 26, cx + 34, cy + 42], 180, 360, fill=(190, 190, 190))
    d.pieslice([cx - 34, cy - 26, cx + 34, cy + 42], 180, 360, outline=(120, 120, 120), width=2)
    # Patriot launcher bottom-left, bigger
    lx, ly = x0 + 16, y1 - 36
    d.rectangle([lx, ly, lx + 64, ly + 18], fill=(60, 90, 50))
    for i in range(4):
        d.line([lx + 10 + i * 15, ly, lx + 26 + i * 15, ly - 32], fill=(96, 128, 84), width=6)
    # missile trajectories: polylines diving toward the dome, with warhead dots
    import math as _m
    def _traj(pts, col, wd):
        for a, b in zip(pts, pts[1:]):
            d.line([a, b], fill=col, width=wd)
    _traj([(x1 - 8, y0 + 34), (x0 + int(w * 0.78), y0 + 44), (cx + 26, cy - 30), (cx + 8, cy - 12)],
          (255, 80, 60), 3)
    _traj([(x1 - 30, y0 + 58), (x0 + int(w * 0.70), y0 + 62), (cx + 30, cy - 8)],
          (255, 140, 60), 2)
    d.ellipse([x1 - 12, y0 + 30, x1 - 4, y0 + 38], fill=(255, 200, 80))
    d.ellipse([x1 - 34, y0 + 54, x1 - 26, y0 + 62], fill=(255, 170, 80))
    # lit skyline along the bottom
    skyline(d, (x0, y1 - 30, x1, y1), 33, lit=0.6)


def scene_kyiv(d, box, variant=1):
    """Kyiv night: skyline, searchlight beam, drone silhouettes, small star bursts.
    No big orange circles: explosions are thin white/yellow star bursts only."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(10, 16, 34))
    stars(d, box, 55, 22)
    # crescent moon top-right
    d.ellipse([x1 - 44, y0 + 8, x1 - 16, y0 + 36], fill=(240, 236, 210))
    d.ellipse([x1 - 38, y0 + 6, x1 - 12, y0 + 32], fill=(10, 16, 34))
    # searchlight beam (v2: from the left, wider)
    if variant == 2:
        d.polygon([(x0 + 52, y1 - 30), (x0 + 70, y1 - 30), (x0 + int(w * 0.58), y0 + 6),
                   (x0 + int(w * 0.52), y0 + 6)], fill=(214, 216, 190))
    else:
        d.polygon([(x1 - 52, y1 - 30), (x1 - 36, y1 - 30), (x0 + int(w * 0.52), y0 + 6),
                   (x0 + int(w * 0.47), y0 + 6)], fill=(214, 216, 190))
    # drone silhouettes with lights
    drones = [(x0 + 40, y0 + 26, 9), (x0 + 120, y0 + 44, 7), (x0 + 210, y0 + 20, 8)]
    if variant == 2:
        drones = [(x0 + 60, y0 + 30, 9), (x0 + 150, y0 + 52, 7), (x0 + 240, y0 + 24, 8),
                  (x0 + 190, y0 + 66, 6), (x0 + 100, y0 + 14, 6)]
    for (dx, dy, s) in drones:
        d.line([dx - s, dy, dx + s, dy], fill=(220, 220, 220), width=2)
        d.line([dx, dy - 3, dx, dy + 3], fill=(220, 220, 220), width=2)
        d.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(255, 80, 60))
    # small star-burst explosions (thin lines, not discs)
    bursts = [(x0 + 70, y0 + 70, 12), (x0 + 250, y0 + 90, 10)]
    if variant == 2:
        bursts = [(x0 + 90, y0 + 78, 13), (x0 + 200, y0 + 60, 11), (x0 + 280, y0 + 96, 9)]
    for (ex, ey, r) in bursts:
        for ang in range(0, 360, 45):
            import math
            a = math.radians(ang)
            d.line([ex, ey, ex + r * math.cos(a), ey + r * math.sin(a)],
                   fill=(255, 210, 90), width=2)
        d.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=(255, 240, 180))
    skyline(d, (x0, y1 - 34, x1, y1), 77, lit=0.6)


# ---------------- secondary scenes ----------------

def scene_hk(d, box, variant=1):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(200, 220, 235))
    d.rectangle([x0, y0 + 18, x1, y1], fill=(120, 140, 170))
    for i, bx in enumerate(range(x0 + 6, x1 - 20, 22)):
        d.rectangle([bx, y0 + 26 - (i % 3) * 6, bx + 16, y1], fill=(70, 90, 120))
    d.rectangle([x0 + int((x1 - x0) * 0.55), y1 - 34, x0 + int((x1 - x0) * 0.85), y1 - 8],
                fill=(178, 34, 34))
    d.text((x0 + int((x1 - x0) * 0.58), y1 - 33), "VOTE", font=F(SANSB, 13), fill=(255, 255, 255))


def scene_cricket(d, box, variant=1):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(140, 190, 120))
    d.ellipse([x0 + 8, y0 + 6, x0 + 60, y0 + 26], fill=(250, 246, 236))
    d.text((x0 + 12, y0 + 8), "720/9", font=F(SANSB, 12), fill=NAVY)
    d.rectangle([x0, y1 - 18, x1, y1], fill=(90, 140, 80))
    # batsman
    d.ellipse([x0 + 90, y0 + 26, x0 + 102, y0 + 38], fill=(222, 184, 150))
    d.polygon([(x0 + 88, y0 + 38), (x0 + 104, y0 + 38), (x0 + 108, y1 - 20), (x0 + 84, y1 - 20)],
              fill=(250, 250, 250))
    d.line([x0 + 104, y0 + 46, x0 + 126, y1 - 24], fill=(180, 140, 90), width=3)
    for i in range(3):
        d.line([x0 + 26 + i * 5, y1 - 34, x0 + 26 + i * 5, y1 - 18], fill=(255, 220, 120), width=2)


def scene_f1(d, box, variant=1):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(16, 20, 44))
    for i in range(6):
        d.rectangle([x0 + i * 12, y0 + 4, x0 + i * 12 + 6, y0 + 12],
                    fill=(255, 255, 255) if i % 2 == 0 else (20, 20, 20))
    d.rectangle([x0, y1 - 26, x1, y1], fill=(60, 60, 70))
    d.polygon([(x0 + 30, y1 - 30), (x0 + 120, y1 - 30), (x0 + 128, y1 - 16), (x0 + 22, y1 - 16)],
              fill=(200, 30, 30))
    d.ellipse([x0 + 44, y1 - 16, x0 + 58, y1 - 2], fill=(20, 20, 20))
    d.ellipse([x0 + 104, y1 - 16, x0 + 118, y1 - 2], fill=(20, 20, 20))
    d.rectangle([x0 + 84, y1 - 40, x0 + 92, y1 - 28], fill=(30, 30, 30))


def scene_basket(d, box, variant=1):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(240, 180, 110))
    d.rectangle([x0, y1 - 22, x1, y1], fill=(200, 120, 60))
    d.ellipse([x0 + 62, y0 + 4, x0 + 102, y0 + 28], fill=(250, 246, 236))
    d.text((x0 + 68, y0 + 7), "50", font=F(SANSB, 15), fill=RED)
    # hoop
    d.line([x1 - 34, y0 + 8, x1 - 34, y0 + 34], fill=(120, 120, 120), width=3)
    d.ellipse([x1 - 46, y0 + 30, x1 - 22, y0 + 40], outline=RED, width=2)
    # player dunking
    d.ellipse([x0 + 78, y0 + 16, x0 + 90, y0 + 28], fill=(120, 80, 50))
    d.polygon([(x0 + 76, y0 + 28), (x0 + 92, y0 + 28), (x0 + 96, y1 - 22), (x0 + 72, y1 - 22)],
              fill=(30, 60, 120))
    d.line([x0 + 88, y0 + 30, x1 - 34, y0 + 32], fill=(120, 80, 50), width=3)


def scene_tanker(d, box, variant=1):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(150, 190, 210))
    d.rectangle([x0, y1 - 22, x1, y1], fill=(40, 90, 130))
    d.rectangle([x0 + 16, y1 - 40, x0 + 110, y1 - 22], fill=(120, 40, 30))
    d.rectangle([x0 + 20, y1 - 52, x0 + 46, y1 - 40], fill=(200, 200, 200))
    smoke(d, x0 + 60, y1 - 48, 7, seed=5)
    flames(d, x0 + 92, y1 - 40, 8, seed=6)
    # mine
    d.ellipse([x1 - 30, y1 - 34, x1 - 14, y1 - 18], fill=(40, 40, 40))
    for ang in range(0, 360, 45):
        import math
        a = math.radians(ang)
        d.line([x1 - 22, y1 - 26, x1 - 22 + 9 * math.cos(a), y1 - 26 + 9 * math.sin(a)],
               fill=(40, 40, 40), width=2)


def scene_patriot(d, box, variant=1):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(190, 200, 210))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(120, 140, 110))
    d.rectangle([x0 + 20, y1 - 34, x0 + 80, y1 - 16], fill=(60, 90, 50))
    for i in range(4):
        d.line([x0 + 28 + i * 14, y1 - 34, x0 + 44 + i * 14, y1 - 58], fill=(90, 120, 80), width=5)
    d.polygon([(x0 + 108, y0 + 8), (x0 + 132, y0 + 8), (x0 + 120, y0 + 26)], fill=(178, 34, 34))
    d.text((x0 + 110, y0 + 28), "US", font=F(SANSB, 11), fill=NAVY)


def scene_jet(d, box, variant=1):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(170, 200, 225))
    d.ellipse([x0 + 10, y0 + 8, x0 + 50, y0 + 20], fill=(250, 250, 250))
    d.ellipse([x0 + 90, y0 + 16, x0 + 140, y0 + 28], fill=(240, 240, 240))
    d.polygon([(x0 + 40, y0 + 30), (x0 + 120, y0 + 34), (x0 + 100, y0 + 42), (x0 + 50, y0 + 42)],
              fill=(90, 100, 110))
    d.polygon([(x0 + 70, y0 + 30), (x0 + 82, y0 + 18), (x0 + 90, y0 + 30)], fill=(70, 80, 90))
    d.polygon([(x0 + 30, y0 + 36), (x0 + 40, y0 + 28), (x0 + 46, y0 + 38)], fill=(70, 80, 90))
    d.line([x0 + 96, y0 + 40, x0 + 130, y0 + 50], fill=(200, 60, 40), width=2)


def scene_fbi(d, box, variant=1):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(210, 220, 235))
    d.rectangle([x0 + 20, y0 + 14, x0 + 100, y1 - 8], fill=(90, 110, 140))
    d.polygon([(x0 + 20, y0 + 14), (x0 + 60, y0 - 2), (x0 + 100, y0 + 14)], fill=(70, 90, 120))
    for r in range(3):
        for c in range(4):
            d.rectangle([x0 + 30 + c * 18, y0 + 24 + r * 14, x0 + 42 + c * 18, y0 + 34 + r * 14],
                        fill=(255, 220, 130))
    d.ellipse([x1 - 46, y0 + 10, x1 - 16, y0 + 40], outline=NAVY, width=3)
    d.line([x1 - 20, y0 + 36, x1 - 8, y0 + 50], fill=NAVY, width=3)
    d.text((x1 - 42, y0 + 18), "FBI", font=F(SANSB, 10), fill=NAVY)


def scene_icu(d, box, variant=1):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(220, 235, 230))
    d.rectangle([x0 + 8, y0 + 8, x0 + 56, y0 + 34], fill=(30, 60, 80))
    d.line([x0 + 12, y0 + 21, x0 + 22, y0 + 21, x0 + 26, y0 + 13, x0 + 32, y0 + 28,
            x0 + 38, y0 + 21, x0 + 52, y0 + 21], fill=(80, 220, 120), width=2)
    d.rectangle([x0 + 16, y1 - 26, x0 + 130, y1 - 14], fill=(240, 240, 240))
    d.ellipse([x0 + 20, y1 - 40, x0 + 34, y1 - 26], fill=(222, 184, 150))
    d.rectangle([x0 + 34, y1 - 30, x0 + 120, y1 - 14], fill=(180, 200, 220))
    d.line([x1 - 16, y0 + 6, x1 - 16, y1 - 26], fill=(150, 150, 150), width=2)
    d.rectangle([x1 - 22, y1 - 34, x1 - 10, y1 - 22], fill=(200, 220, 240))


def scene_house(d, box, variant=1):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(200, 215, 235))
    # Capitol dome
    d.pieslice([x0 + 40, y0 + 4, x0 + 92, y0 + 44], 180, 360, fill=(250, 250, 250))
    d.rectangle([x0 + 36, y0 + 24, x0 + 96, y1 - 18], fill=(240, 240, 240))
    d.rectangle([x0 + 30, y1 - 18, x0 + 102, y1 - 10], fill=(220, 220, 220))
    # seat bars
    for i, h in enumerate([14, 22, 18]):
        d.rectangle([x1 - 44 + i * 12, y1 - 10 - h, x1 - 34 + i * 12, y1 - 10],
                    fill=(16, 36, 68) if i != 1 else (178, 34, 34))
    d.rectangle([x0 + 8, y1 - 26, x0 + 30, y1 - 10], fill=(178, 34, 34))
    d.text((x0 + 11, y1 - 24), "VOTE", font=F(SANSB, 8), fill=(255, 255, 255))


def scene_talks(d, box, variant=1):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(210, 200, 180))
    d.rectangle([x0 + 10, y1 - 30, x0 + 130, y1 - 12], fill=(120, 72, 32))
    d.rectangle([x0 + 50, y1 - 44, x0 + 90, y1 - 30], fill=(250, 246, 236))
    d.polygon([(x0 + 22, y0 + 10), (x0 + 38, y0 + 10), (x0 + 30, y0 + 30)], fill=(30, 122, 70))
    d.polygon([(x0 + 104, y0 + 10), (x0 + 120, y0 + 10), (x0 + 112, y0 + 30)], fill=(178, 34, 34))
    d.ellipse([x0 + 60, y0 + 8, x0 + 74, y0 + 22], fill=(222, 184, 150))
    d.ellipse([x0 + 82, y0 + 8, x0 + 96, y0 + 22], fill=(190, 140, 100))


def scene_serang(d, box, variant=1):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(60, 60, 70))
    d.rectangle([x0 + 10, y0 + 22, x0 + 110, y1 - 8], fill=(120, 100, 80))
    d.rectangle([x0 + 10, y0 + 22, x0 + 110, y0 + 30], fill=(90, 70, 55))
    for i in range(3):
        d.rectangle([x0 + 20 + i * 30, y0 + 36, x0 + 40 + i * 30, y0 + 52], fill=(255, 200, 90))
    smoke(d, x0 + 60, y0 + 18, 8, seed=9)
    flames(d, x0 + 40, y1 - 8, 10, seed=8)
    flames(d, x0 + 90, y1 - 8, 8, seed=10)

# ---------------- dotted world map ----------------
# 48 x 24 coarse land grid ('#' = land). Drawn as dots on a dark navy panel.
MAP_GRID = [
    "....######....................##########........",
    "....########..................##############....",
    "..##########................########################",
    "..###########....###.........########################",
    "...##########...#####.......#########################",
    "....#########....####......##########################",
    ".....########....###.......######..##################",
    "......#######....##........#####....#################",
    ".......######.............####......########..########",
    "........#####.............###........######....#######",
    ".........####...........####.........#####.....######",
    "..........###..........#####..........###......#####",
    "...........##..........######..........##.......####",
    "............#..........#######.........##........###",
    ".......................#######.........#.........##",
    ".......................######...................###",
    "........................#####...................####",
    ".........................####....................##",
    "..........................###....................#",
    "...........................##.......................",
    "........................................................",
    "........................................................",
    "........................................................",
    "........................................................",
]
MAP_GRID = [r.ljust(48, ".")[:48] for r in MAP_GRID]

# story number -> (grid col, row) for the map pins
PINS = {
    1: (25, 7), 2: (31, 8), 3: (24, 4), 4: (40, 8), 5: (44, 17),
    6: (5, 7), 7: (7, 9), 8: (33, 10), 9: (21, 3), 10: (27, 3),
    11: (9, 6), 12: (13, 13), 13: (12, 5), 14: (28, 8), 15: (40, 11),
}


def draw_map(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(18, 38, 74))
    gw, gh = 48, 24
    cw = (x1 - x0) / gw
    ch = (y1 - y0) / gh
    for r, row in enumerate(MAP_GRID):
        for c, ch_ in enumerate(row):
            if ch_ == "#":
                cx = x0 + (c + 0.5) * cw
                cy = y0 + (r + 0.5) * ch
                d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6], fill=(96, 138, 186))
    # pins, with a deterministic nudge pass so none overlap or clip
    placed = []
    for n in sorted(PINS):
        c, r = PINS[n]
        px = x0 + (c + 0.5) * cw
        py = y0 + (r + 0.5) * ch
        for _ in range(4):
            ok = all((px - qx) ** 2 + (py - qy) ** 2 >= 15 ** 2 for qx, qy in placed)
            ok = ok and (x0 + 8 <= px <= x1 - 8) and (y0 + 8 <= py <= y1 - 8)
            if ok:
                break
            py += 7
        placed.append((px, py))
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED, outline=(255, 255, 255), width=1)
        f = F(SANSB, 9)
        tw = f.getlength(str(n))
        d.text((px - tw / 2, py - 5), str(n), font=f, fill=(255, 255, 255))


# ---------------- story data ----------------

LEADS = [
    dict(n=1, place="ANTALYA, TÜRKIYE", topic="CLIMATE", tag="PENDING",
         chip="COP31: FINAL TEXT", chip_bg=NAVY,
         headline="COP31's final text lands at dawn — with no mention of fossil fuels",
         body="Final text lands at dawn in Antalya; rejected the same day over its silence on fossil fuels. Adaptation side deals adopted; approval still pending. (Reuters, BBC, The Guardian)",
         scene="cop31"),
    dict(n=2, place="MANAMA, BAHRAIN", topic="IRAN", tag="CLAIM",
         chip="CLAIM VS DENIAL", chip_bg=RED,
         headline="Iran claims two US radars hit; Bahrain denies it",
         body="IRGC says it destroyed two Patriot radars on Saturday night. Bahrain says a civilian plant was hit, two hurt. US: no damage. (AFP, Reuters, Al Jazeera)",
         scene="bahrain"),
    dict(n=3, place="KYIV REGION, UKRAINE", topic="WAR", tag="REPORTED",
         chip="186 DRONES OVERNIGHT", chip_bg=RED,
         headline="Russia fires 186 drones; a Kyiv-region block is destroyed",
         body="Air defences down or jam 161 of 186 strike drones (72 jet-powered) from eight directions. One destroyed a five-storey block in Dymer: up to seven feared trapped, two injured, nine evacuated. (Ukrainian Air Force)",
         scene="kyiv"),
]

SECONDARIES = [
    dict(n=4, place="HONG KONG", topic="ELECTION", tag="CONFIRMED", chip="856 CANDIDATES",
         headline="Hong Kong elects its Election Committee",
         body="856 candidates, 723 seats; 98.79% turnout by 5 pm. (SCMP)", scene="hk"),
    dict(n=5, place="WELLINGTON", topic="CRICKET", tag="CONFIRMED", chip="720/9 DECLARED",
         headline="India declare on 720/9, a record in NZ",
         body="Rahul 136, Pant 128; hosts 119/2, trailing by 233. (ESPN)", scene="cricket"),
    dict(n=6, place="LAS VEGAS", topic="FORMULA 1", tag="CONFIRMED", chip="VERSTAPPEN WINS",
         headline="Verstappen takes the Las Vegas GP",
         body="0.639 s clear of Norris; 75th win. (F1 / FIA)", scene="f1"),
    dict(n=7, place="SAN ANTONIO", topic="NBA", tag="CONFIRMED", chip="50 POINTS",
         headline="Wembanyama scores 50 as the Spurs roll on",
         body="50 pts, 19 rebounds; 114–91 over New Orleans. (Reuters)", scene="basket"),
    dict(n=8, place="HORMUZ", topic="SEA", tag="CLAIM", chip="SHIP ABLAZE",
         headline="Iran: two tankers hit near Hormuz",
         body="Both catch fire in the strait. (Wires)", scene="tanker"),
    dict(n=9, place="KYIV", topic="WAR", tag="REPORTED", chip="PATRIOT PLEA",
         headline="Zelenskyy urges US to send Patriots",
         body="Partners paid; US yet to deliver. (Wires)", scene="patriot"),
    dict(n=10, place="UKRAINE", topic="WAR", tag="CONFIRMED", chip="GUN KILL",
         headline="Mirage downs drone with cannon fire",
         body="Gun kill over Ukraine. (Wires)", scene="jet"),
    dict(n=11, place="WASHINGTON", topic="CYBER", tag="REPORTED", chip="FBI PROBE",
         headline="FBI probes hack of its crime database",
         body="State pauses gun-dealer checks; breach assessed. (AP)", scene="fbi"),
    dict(n=12, place="BRASILIA", topic="HEALTH", tag="CONFIRMED", chip="IN ICU",
         headline="Bolsonaro stable in intensive care",
         body="Ex-President under observation. (Reuters)", scene="icu"),
    dict(n=13, place="WASHINGTON", topic="POLITICS", tag="REPORTED", chip="HOUSE FLIPS",
         headline="Democrats win House majority",
         body="Largest since 1992: NC recount. (Wires)", scene="house"),
    dict(n=14, place="GAZA CITY", topic="CONFLICT", tag="REPORTED", chip="TALKS SOUGHT",
         headline="Hamas seeks urgent talks",
         body="Three die in a strike on a food vehicle. (Al Jazeera)",
         scene="talks"),
    dict(n=15, place="SERANG", topic="DISASTER", tag="CONFIRMED", chip="36 MISSING",
         headline="Serang fire: 3 dead, 36 missing",
         body="Candy factory blaze in Cikande. (Detiknews)", scene="serang"),
]

ALSO = [
    (16, "Drone hits home in Dymer, two injured", "REPORTED"),
    (17, "Ex-police chief found dead amid Sicily inquiry", "REPORTED"),
    (18, "Nepal PM Shah lands in Delhi on first visit", "CONFIRMED"),
    (19, "Iran unveils dual-missile launcher, missile city", "REPORTED"),
    (20, "Saudis intercept Houthi drone and missile", "REPORTED"),
    (21, "IRGC: US MQ-1 drone downed", "CLAIM"),
    (22, "Trump: Iran killed 81,000 protesters", "REPORTED"),
    (23, "Side deals adopted, adaptation", "CONFIRMED"),
    (24, "Belgium controllers join Monday strike", "REPORTED"),
    (25, "S. Korea minister resigns", "REPORTED"),
    (26, "Drone strike hits Russian ship at Benghazi", "REPORTED"),
    (27, "COP32: Addis Ababa, Nov 2027", "CONFIRMED"),
    (28, "Basel Reserve record falls after 31 years", "CONFIRMED"),
    (29, "Guterres 'deeply disappointed' by COP31", "CONFIRMED"),
    (30, "90+ nations sign electrification pledge", "CONFIRMED"),
    (31, "Antalya: longest COP on record", "CONFIRMED"),
    (32, "Bitcoin back near $55,000", "CONFIRMED"),
    (33, "Gold holds near $5,355", "CONFIRMED"),
    (34, "ATP Finals host, Turin", "FORECAST"),
    (35, "Liverpool host Manchester United", "FORECAST"),
]

NUMBERS = [
    ("186", "drones fired overnight"),
    ("161", "downed or suppressed"),
    ("35%", "electricity goal 2035, kept"),
    ("$120bn", "adaptation target dropped"),
    ("720/9", "India's record Test total"),
    ("50", "Wembanyama pts, 19 reb"),
]

REGIONS = [
    ("EUROPE", 10, (16, 36, 68)),
    ("MIDDLE EAST", 6, (178, 34, 34)),
    ("AMERICAS", 6, (30, 90, 140)),
    ("ASIA-PACIFIC", 4, (120, 90, 20)),
    ("AFRICA", 2, (120, 90, 20)),
    ("OCEANIA", 1, (15, 118, 110)),
    ("WORLD", 6, (90, 90, 90)),
]

UTC_ITEMS = ("01:00 HK polls open", "03:00 COP31 objections close", "05:11 Hamas seeks talks",
             "05:30 Verstappen wins", "06:00 COP31 approval due")

DATE_CHECK = ("Wires read up to 07:00 UTC. Every story here happened, or was first reported, "
              "on Sunday 22 November 2026. Left out on purpose: Peru quake (Fri 20 Nov) · "
              "110-missile attack (19–20 Nov) · 148-drone night · Kryvyi Rih double-tap "
              "(Fri 20–Sat 21) · 'El Chapo Isidro' captured (Fri) · Baysela boat, 24 dead (Fri) · "
              "Myanmar genocide ruling (Thu 19 Nov) · Sparta II (Sat 21 Nov) · Shenzhen summit "
              "(19–20 Nov). Tonight's real count: 186 drones, not 400.")

SCENES = {"cop31": scene_cop31, "bahrain": scene_bahrain, "kyiv": scene_kyiv,
          "hk": scene_hk, "cricket": scene_cricket, "f1": scene_f1, "basket": scene_basket,
          "tanker": scene_tanker, "patriot": scene_patriot, "jet": scene_jet,
          "fbi": scene_fbi, "icu": scene_icu, "house": scene_house,
          "talks": scene_talks, "serang": scene_serang}

# ---------------- page layout ----------------

def draw_page(variant=1):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # outer frame
    d.rectangle([4, 4, W - 5, H - 5], outline=NAVY, width=2)
    # top strip: paper name small, counts right
    d.rectangle([6, 6, W - 7, 22], fill=NAVY)
    text(d, (12, 9), "THE WORLD IN ONE DAY", F(SANSB, 11), (255, 255, 255))
    text(d, (W - 12, 9), "35 STORIES · 7 REGIONS · EVERY ONE DATED SUNDAY 22 NOVEMBER 2026",
         F(SANSB, 10), (255, 255, 255), anchor="ra")
    # giant date — the biggest type on the page
    df = fit(SERIFB, "Sunday 22 November 2026", 96, 980)
    text(d, (W // 2, 24), "Sunday 22 November 2026", df, NAVY, anchor="ma")
    # red italic subhead
    sf = fit(SERIFI, "186 drones over Ukraine in the night · COP31's deal names no fossil fuels · "
             "Iran's radar claim meets Bahrain's denial", 20, 980)
    text(d, (W // 2, 118), "186 drones over Ukraine in the night · COP31's deal names no fossil "
         "fuels · Iran's radar claim meets Bahrain's denial", sf, RED, anchor="ma")
    d.line([14, 140, W - 15, 140], fill=NAVY, width=1)
    # numbers strip
    y0, y1 = 142, 194
    cw = 996 / 6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = 14 + i * cw
        if i:
            d.line([cx, y0 + 4, cx, y1 - 4], fill=(200, 190, 170), width=1)
        nf = fit(SERIFB, num, 34, cw - 10)
        text(d, (cx + cw / 2, y0 + 2), num, nf, RED, anchor="ma")
        text(d, (cx + cw / 2, y0 + 38), cap, F(SANS, 9), INK, anchor="ma")
    # region bar
    widths = [270, 165, 165, 115, 60, 56, 165]
    x = 14
    for (name, cnt, col), wd in zip(REGIONS, widths):
        d.rectangle([x, 196, x + wd - 1, 218], fill=col)
        lab = "%s %d" % (name, cnt)
        f = fit(SANSB, lab, 11, wd - 6)
        text(d, (x + wd / 2, 201), lab, f, (255, 255, 255), anchor="ma")
        x += wd
    # UTC timeline strip
    d.rectangle([14, 220, W - 15, 244], fill=NAVY)
    text(d, (20, 225), "THE DAY IN UTC", F(SANSB, 11), GOLD)
    items = "  ·  ".join(UTC_ITEMS)
    text(d, (150, 226), items, F(SANS, 10), (255, 255, 255))
    text(d, (W - 20, 225), "PRESS TIME 09:45 UTC", F(SANSB, 11), GOLD, anchor="ra")
    # leads
    for i, L in enumerate(LEADS):
        lx = 14 + i * 336
        lw = 324
        SCENES[L["scene"]](d, (lx, 248, lx + lw, 378), variant=variant)
        chip(d, lx + 6, 254, L["chip"], L["chip_bg"], size=11)
        # dateline + tag
        dl = "%d %s · %s" % (L["n"], L["place"], L["topic"])
        text(d, (lx, 382), dl, F(SANSB, 11), NAVY)
        tw = F(SANSB, 10).getlength(L["tag"]) + 8
        tag(d, lx + lw - tw, 381, L["tag"], size=10)
        for j, ln in enumerate(wrap(L["headline"], F(SERIFB, 19), lw)):
            text(d, (lx, 398 + j * 22), ln, F(SERIFB, 19), INK)
        for j, ln in enumerate(wrap(L["body"], F(SANS, 10), lw)):
            text(d, (lx, 468 + j * 13), ln, F(SANS, 10), INK)
    # secondaries: 6 cols x 2 rows
    for i, S in enumerate(SECONDARIES):
        col, row = i % 6, i // 6
        sx = 14 + col * 168
        sy = 522 + row * 124
        sw = 157
        SCENES[S["scene"]](d, (sx, sy, sx + sw, sy + 54), variant=variant)
        chip(d, sx + 4, sy + 4, S["chip"], RED, size=8)
        tw2 = int(F(SANSB, 8).getlength(S["tag"])) + 8
        tag(d, sx + sw - tw2, sy + 38, S["tag"], size=8)
        dl = "%d %s · %s" % (S["n"], S["place"], S["topic"])
        text(d, (sx, sy + 58), dl, F(SANSB, 9), NAVY)
        for j, ln in enumerate(wrap(S["headline"], F(SERIFB, 13), sw)):
            text(d, (sx, sy + 71 + j * 15), ln, F(SERIFB, 13), INK)
        for j, ln in enumerate(wrap(S["body"], F(SANS, 10), sw)):
            text(d, (sx, sy + 101 + j * 12), ln, F(SANS, 10), INK)
    # map + ALSO
    text(d, (14, 774), "WHERE IT HAPPENED", F(SANSB, 12), NAVY)
    text(d, (314, 776), "pins match story numbers", F(SANS, 9), GREY, anchor="ra")
    draw_map(d, (14, 792, 314, 912))
    text(d, (326, 774), "ALSO ON SUNDAY 22 NOVEMBER — 20 MORE STORIES", F(SANSB, 12), NAVY)
    for i, (n, item, tg) in enumerate(ALSO):
        ax = 326 + (i // 10) * 346
        ay = 794 + (i % 10) * 11.5
        text(d, (ax, ay), "%d  %s" % (n, item), F(SANS, 10), INK)
        tag(d, ax + 268, ay - 1, tg, size=7)
    # DATE CHECK
    d.rectangle([14, 916, W - 15, 976], outline=RED, width=2)
    chip(d, 20, 920, "DATE CHECK — READ THIS FIRST", RED, size=11)
    for j, ln in enumerate(wrap(DATE_CHECK, F(SANS, 10.5), 980)):
        text(d, (20, 940 + j * 13), ln, F(SANS, 10.5), INK)
    # footer: readable legend + sources
    text(d, (14, 978), "HOW TO READ THE TAGS — CONFIRMED: carried by the day's wires · REPORTED: "
         "one source's account, not yet confirmed · CLAIM: one side's account, labelled as such",
         F(SANS, 10), INK)
    text(d, (14, 991), "ONGOING: still developing · PENDING: not settled yet · FORECAST: still to "
         "happen when drawn",
         F(SANS, 10), INK)
    text(d, (14, 1004), "Sources: Reuters · BBC · AP · AFP · Al Jazeera · The Guardian · UN News · "
         "Anadolu · Formula 1 · Cricinfo · China Daily — Scenes are drawn illustrations of reported "
         "events, not photographs.",
         F(SANS, 9), GREY)
    d.line([14, 1018, W - 15, 1018], fill=NAVY, width=2)
    return img


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    draw_page(variant=2).save(os.path.join(out, "entry.png"), optimize=True)


if __name__ == "__main__":
    main()
