#!/usr/bin/env python3
"""The World in One Day -- Wednesday 25 November 2026.

Draws a dense newspaper front page (1024x1024 PNG) summing up 36 verified
stories of 25 Nov 2026, using only the Python standard library.
No network, no clock, no unseeded randomness: two runs are byte-identical.
Writes to $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png).
"""
import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ------------------------------------------------------------------ palette
PAPER = (247, 242, 228)
INK = (24, 24, 22)
RED = (176, 36, 28)
NAVY = (30, 56, 94)
TEAL = (14, 116, 108)
GOLD = (174, 122, 0)
GREY = (108, 106, 98)
LIGHT = (233, 227, 211)
SKY = (170, 206, 226)
SEA = (44, 96, 138)
GRASS = (120, 156, 90)
SAND = (214, 196, 150)
WHITE = (255, 255, 255)
SMOKE = (148, 146, 138)
ORANGE = (214, 110, 30)
BROWN = (146, 104, 62)
STEEL = (96, 104, 116)

# ------------------------------------------- single-stroke vector font (mine)
# Glyphs are polylines on a 5 wide x 7 tall grid (y grows downward).
# Each glyph below is my own stroke design, drawn for this entry.
FONT = {
    "A": (((0, 7), (2.5, 0), (5, 7)), ((1.3, 4.4), (3.7, 4.4))),
    "B": (((0.5, 0), (0.5, 7), (3.8, 7), (4.8, 5.8), (4.2, 4), (0.5, 4)),
           ((0.5, 0), (3.8, 0), (4.8, 1.2), (4.2, 4))),
    "C": (((4.8, 1.4), (3.6, 0), (1.4, 0), (0, 1.6), (0, 5.4), (1.4, 7),
            (3.6, 7), (4.8, 5.6)),),
    "D": (((0.5, 0), (0.5, 7), (3.4, 7), (5, 5.2), (5, 1.8), (3.4, 0), (0.5, 0)),),
    "E": (((4.6, 0), (0.5, 0), (0.5, 7), (4.6, 7)), ((0.5, 3.5), (3.8, 3.5))),
    "F": (((0.5, 0), (0.5, 7)), ((0.5, 0), (4.6, 0)), ((0.5, 3.5), (3.8, 3.5))),
    "G": (((4.8, 1.4), (3.6, 0), (1.4, 0), (0, 1.6), (0, 5.4), (1.4, 7),
            (3.6, 7), (4.8, 5.6), (4.8, 3.8), (2.6, 3.8)),),
    "H": (((0.5, 0), (0.5, 7)), ((4.5, 0), (4.5, 7)), ((0.5, 3.5), (4.5, 3.5))),
    "I": (((2.5, 0), (2.5, 7)), ((1, 0), (4, 0)), ((1, 7), (4, 7))),
    "J": (((1.2, 0), (4.8, 0)), ((3.8, 0), (3.8, 5.2), (2.8, 7), (1.2, 7), (0.6, 5.6))),
    "K": (((0.5, 0), (0.5, 7)), ((4.6, 0), (0.5, 3.6)), ((2.4, 4.6), (4.6, 7))),
    "L": (((0.5, 0), (0.5, 7), (4.6, 7)),),
    "M": (((0.5, 7), (0.5, 0), (2.5, 3.8), (4.5, 0), (4.5, 7)),),
    "N": (((0.5, 7), (0.5, 0), (4.5, 7), (4.5, 0)),),
    "O": (((1.2, 0), (3.8, 0), (5, 1.6), (5, 5.4), (3.8, 7), (1.2, 7),
            (0, 5.4), (0, 1.6), (1.2, 0)),),
    "P": (((0.5, 7), (0.5, 0), (4, 0), (5, 1.4), (4.2, 3.6), (0.5, 3.6)),),
    "Q": (((1.2, 0), (3.8, 0), (5, 1.6), (5, 5.4), (3.8, 7), (1.2, 7),
            (0, 5.4), (0, 1.6), (1.2, 0)), ((3.2, 5), (5, 7))),
    "R": (((0.5, 7), (0.5, 0), (4, 0), (5, 1.4), (4.2, 3.6), (0.5, 3.6)),
           ((2.4, 3.8), (4.8, 7))),
    "S": (((4.6, 1.4), (3.4, 0), (1.6, 0), (0.4, 1.2), (0.8, 2.8), (2.4, 3.6),
            (4, 4.2), (4.6, 5.6), (3.4, 7), (1.6, 7), (0.4, 5.8)),),
    "T": (((0.5, 0), (4.5, 0)), ((2.5, 0), (2.5, 7))),
    "U": (((0.5, 0), (0.5, 5.2), (1.6, 7), (3.4, 7), (4.5, 5.2), (4.5, 0)),),
    "V": (((0.5, 0), (2.5, 7), (4.5, 0)),),
    "W": (((0.5, 0), (1.3, 7), (2.5, 3.6), (3.7, 7), (4.5, 0)),),
    "X": (((0.5, 0), (4.5, 7)), ((4.5, 0), (0.5, 7))),
    "Y": (((0.5, 0), (2.5, 3.4), (4.5, 0)), ((2.5, 3.4), (2.5, 7))),
    "Z": (((0.5, 0), (4.5, 0), (0.5, 7), (4.5, 7)),),
    "0": (((1.2, 0), (3.8, 0), (5, 1.6), (5, 5.4), (3.8, 7), (1.2, 7),
            (0, 5.4), (0, 1.6), (1.2, 0)),),
    "1": (((1.4, 1.4), (2.8, 0), (2.8, 7)), ((1, 7), (4.4, 7))),
    "2": (((0.6, 1.6), (1.6, 0), (3.6, 0), (4.6, 1.2), (4.6, 2.6), (0.6, 7), (4.6, 7)),),
    "3": (((0.6, 0.8), (1.8, 0), (3.6, 0), (4.6, 1), (4.6, 2.8), (3.2, 3.6),
            (4.6, 4.4), (4.6, 5.8), (3.6, 7), (1.8, 7), (0.6, 6.2)),),
    "4": (((3.8, 0), (3.8, 7)), ((0.4, 4.6), (4.6, 4.6)), ((3.8, 0), (0.4, 4.6))),
    "5": (((4.6, 0), (0.6, 0), (0.6, 3.4), (3.6, 3.4), (4.6, 4.6), (4.6, 5.8),
            (3.6, 7), (1.6, 7), (0.6, 6)),),
    "6": (((4.4, 1), (3.2, 0), (1.2, 0), (0.4, 1.6), (0.4, 5.4), (1.4, 7),
            (3.2, 7), (4.6, 5.6), (4.6, 3.8), (3.2, 3), (1, 3.4)),),
    "7": (((0.6, 0), (4.6, 0), (2.2, 7)),),
    "8": (((1.2, 0.2), (3.8, 0.2), (4.8, 1.6), (3.8, 3.4), (1.2, 3.4),
            (0.2, 1.6), (1.2, 0.2)),
           ((1.2, 3.6), (3.8, 3.6), (4.8, 5.2), (3.8, 6.8), (1.2, 6.8),
            (0.2, 5.2), (1.2, 3.6))),
    "9": (((0.6, 6), (1.8, 7), (3.8, 7), (4.8, 5.4), (4.8, 1.6), (3.8, 0),
            (1.8, 0), (0.4, 1.4), (0.4, 3.2), (1.8, 3.8), (4.2, 3.4)),),
    ".": (((2.2, 6.2), (2.8, 6.2), (2.8, 7), (2.2, 7)),),
    ",": (((2.6, 5.8), (2.4, 7)),),
    ":": (((2.2, 1.6), (2.8, 1.6), (2.8, 2.4), (2.2, 2.4)),
           ((2.2, 5), (2.8, 5), (2.8, 5.8), (2.2, 5.8))),
    ";": (((2.2, 1.6), (2.8, 1.6), (2.8, 2.4), (2.2, 2.4)), ((2.6, 4.8), (2.4, 7))),
    "!": (((2.5, 0), (2.5, 4.8)), ((2.2, 6.2), (2.8, 6.2), (2.8, 7), (2.2, 7))),
    "?": (((1, 1.4), (2, 0), (3.6, 0), (4.6, 1), (4.4, 2.6), (2.5, 3.6), (2.5, 4.6)),
           ((2.2, 6.2), (2.8, 6.2), (2.8, 7), (2.2, 7))),
    "-": (((0.6, 3.6), (4.4, 3.6)),),
    "\u2014": (((0.2, 3.6), (4.8, 3.6)),),
    "/": (((4.2, 0), (0.8, 7)),),
    "%": (((4.2, 0), (0.8, 7)),
           ((0.6, 1), (1.8, 1), (1.8, 2.2), (0.6, 2.2), (0.6, 1)),
           ((3.2, 4.8), (4.4, 4.8), (4.4, 6), (3.2, 6), (3.2, 4.8))),
    "$": (((2.5, 0), (2.5, 7)),
           ((4.4, 1.4), (3.2, 0.2), (1.4, 0.6), (0.6, 2), (1.4, 3.4),
            (3.6, 3.8), (4.4, 5), (3.2, 6.8), (1.6, 6.6), (0.6, 5.4))),
    "&": (((4.2, 0.6), (3.2, 0), (1.6, 0.6), (1.4, 2.4), (3.6, 4.4), (4.6, 6),
            (4.4, 7), (2.8, 7), (1.2, 5.6), (2.2, 3.4), (4.6, 1.8)),),
    "+": (((2.5, 1), (2.5, 6)), ((0.6, 3.5), (4.4, 3.5))),
    "=": (((0.6, 2.4), (4.4, 2.4)), ((0.6, 4.8), (4.4, 4.8))),
    "(": (((3.8, 0), (2.4, 1.8), (2.4, 5.2), (3.8, 7)),),
    ")": (((1.2, 0), (2.6, 1.8), (2.6, 5.2), (1.2, 7)),),
    '"': (((1.6, 0), (1.6, 2)), ((3.4, 0), (3.4, 2))),
    "'": (((2.5, 0), (2.5, 2)),),
    "*": (((2.5, 0.6), (2.5, 6.4)), ((0.6, 2), (4.4, 5)), ((4.4, 2), (0.6, 5))),
    "\u2022": (((1.8, 2.8), (3.2, 2.8), (3.2, 4.2), (1.8, 4.2)),),
    "[": (((4.2, 0), (0.8, 0), (0.8, 7), (4.2, 7)),),
    "]": (((0.8, 0), (4.2, 0), (4.2, 7), (0.8, 7)),),
    "~": (((0.6, 4), (1.6, 2.6), (3, 4), (4.4, 2.6)),),
    " ": (),
}
STEP = 6.0  # glyph advance in grid units


def text_width(s, size):
    return len(s) * STEP * size / 7.0


def wrap_text(s, size, max_w):
    """Greedy word wrap; returns lines, each fitting max_w."""
    out, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, size) <= max_w or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


# ------------------------------------------------------------------- canvas
class Page:
    """An RGB canvas plus the registries the self-checks use."""

    def __init__(self):
        self.buf = bytearray(bytes(PAPER) * (W * H))
        self.boxes = []   # (x0, y0, x1, y1, label) every drawn text line
        self.pins = []    # (x, y, n) every map pin

    def set_px(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.buf[i:i + 3] = bytes(c)

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            self.buf[i:i + len(row)] = row

    def frame(self, x, y, w, h, c, t=1):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def _blob(self, x, y, c, r):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r + r:
                    self.set_px(x + dx, y + dy, c)

    def segment(self, x0, y0, x1, y1, c, t=1):
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        r = max(0, (t - 1) // 2)
        for i in range(steps + 1):
            x = round(x0 + dx * i / steps)
            y = round(y0 + dy * i / steps)
            if t <= 1:
                self.set_px(x, y, c)
            else:
                self._blob(x, y, c, r)

    def path(self, pts, c, t=1, close=False):
        for i in range(len(pts) - 1):
            self.segment(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], c, t)
        if close and len(pts) > 2:
            self.segment(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1], c, t)

    def fill_poly(self, pts, c):
        """Scanline fill of a simple polygon (even-odd pairing)."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa, xb = int(math.ceil(xs[k])), int(math.floor(xs[k + 1]))
                if xb >= xa:
                    self.fill(xa, y, xb - xa + 1, 1, c)

    def disc(self, cx, cy, r, c, filled=True):
        if filled:
            for y in range(cy - r, cy + r + 1):
                half = int(math.sqrt(max(0, r * r - (y - cy) ** 2)))
                self.fill(cx - half, y, half * 2 + 1, 1, c)
        else:
            for a in range(360):
                th = math.radians(a)
                self.set_px(cx + int(r * math.cos(th)), cy + int(r * math.sin(th)), c)

    # ---------------------------------------------------------------- text
    def draw_glyph(self, ch, x, y, size, c):
        if ch not in FONT:
            raise ValueError("glyph missing from font: %r" % ch)
        sc = size / 7.0
        thick = 1 if size < 11 else (2 if size < 22 else max(2, int(size / 9)))
        for stroke in FONT[ch]:
            for (ax, ay), (bx, by) in zip(stroke, stroke[1:]):
                self.segment(round(x + ax * sc), round(y + ay * sc),
                             round(x + bx * sc), round(y + by * sc), c, thick)

    def draw_text(self, x, y, s, size, c, align="left"):
        """Draw one line; top-left (x, y) unless centred/right. Registers box."""
        s = s.upper()  # the hand-drawn font is caps-only; normalise here
        w = text_width(s, size)
        if align == "center":
            x = round(x - w / 2)
        elif align == "right":
            x = round(x - w)
        for i, ch in enumerate(s):
            if ch == " ":
                continue
            self.draw_glyph(ch, x + i * STEP * size / 7.0, y, size, c)
        self.boxes.append((x, y, x + int(math.ceil(w)), y + size, s[:24]))
        return w

    def draw_para(self, x, y, s, size, c, max_w, leading, max_lines=None):
        lines = wrap_text(s, size, max_w)
        if max_lines is not None and len(lines) > max_lines:
            raise ValueError("text overflows: %r wraps to %d lines (max %d)"
                             % (s[:40], len(lines), max_lines))
        for i, ln in enumerate(lines):
            self.draw_text(x, y + i * leading, ln, size, c)
        return len(lines)


# ---------------------------------------------------------------------- PNG
def _png_chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, pg):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += pg.buf[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += _png_chunk(b"IDAT", comp)
    png += _png_chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------------------- stories
# (number, kicker, headline, sub-line, scene key) -- all verified 25 Nov 2026
MAIN = [
    (1, "HORMUZ", "IRGC SAYS TWO TANKERS HIT MINES",
     "IRGC says two tankers struck mines and caught fire in the Strait of Hormuz", "strait"),
    (2, "GAZA", "HAMAS SECURITY CHIEF KILLED",
     "Dawn strike on al-Shati camp kills Mohammad Abuelouf, wife and two teenage daughters", "gaza"),
    (3, "UKRAINE", "REFINERIES ABLAZE IN SAMARA",
     "Drones hit two Rosneft refineries in Samara; 1 killed; Odesa strike kills 2", "refinery"),
    (4, "MARKETS", "ASIA SELLOFF; DOW TOPS 50,000",
     "Kospi -6.16%, Nikkei -2.78%; Dow closes above 50,000 for the first time", "chart"),
    (5, "SPACE", "PAKISTAN'S FIRST ASTRONAUT",
     "Shenzhou-24 docks with Tiangong; first foreign visitor aboard for 5-10 days", "rocket"),
    (6, "COLOMBIA", "HOSTAGES FREED IN CARTAGENA",
     "Security forces storm Exito; about 20 freed, one captor killed", "market"),
    (7, "SUDAN", "19 KILLED IN BLUE NILE STRIKES",
     "RSF drone strikes kill 19 in Damazin and Roseires, wound about 20", "drones"),
    (8, "PACIFIC", "SOLOMONS TREATY BARS FOREIGN BASES",
     "Australia and Solomons sign treaty barring any foreign military base", "treaty"),
    (9, "SAUDI", "HOUTHIS CLAIM REFINERY HIT",
     "Houthis say Ras Tanura refinery hit; coalition says it downed 7 drones", "tanks"),
    (10, "BANGLADESH", "GARMENT WAGE UP 36% TO 17,000 TAKAS",
     "Minimum wage raised to 17,000 takas after weeks of violent protests", "factory"),
    (11, "NORTH KOREA", "SWISS DIPLOMAT EXPELLED",
     "Pyongyang orders Swiss envoy out over sanctions on a Russian youth camp", "embassy"),
    (12, "LIBYA", "TWO LIBYAN OFFICERS DIE",
     "Two naval officers die of wounds from sea-drone attack on Russian corvette", "harbour"),
    (13, "DENMARK", "DENMARK BANS HEADSCARVES FOR PROSECUTORS",
     "Denmark bans headscarves for prosecutors as religious-dress debate grows", "court"),
]

ALSO = [
    "1. Amnesty urges ICC probe over births in Gaza",
    "2. UK to send Ukraine 1,000+ drones, GBP 260m package",
    "3. Zelensky: Ukraine hit Russian ship in Gulf of Finland",
    "4. Trump open to resuming talks with Kim Jong-un",
    "5. Trump awards Rudy Giuliani the Medal of Freedom",
    "6. Unclassified CIA system breached in US cyber incident",
    "7. Abrego Garcia leaves US voluntarily for Spain",
    "8. Colombia car bomb injures 23 in Villavicencio",
    "9. Landmine casualties hit 5-year high of ~7,000",
    "10. Dell record Q3: revenue $54.9bn (+103%); AI servers $22.0bn (+291%)",
    "11. Nvidia's Huang in therapy, sorry for 'terrible mistakes'",
    "12. Pope Leo XIV voices concern over COP31 failure",
    "13. WHO evacuates Ebola staff from DR Congo hospital",
    "14. Denmark top court upholds 'ghetto law' evictions",
    "15. UK's biggest police force still institutionally racist",
    "16. Real Madrid beat PSV 5-1; Mbappe scores twice",
    "17. REPORTED: China's Shanghai party chief under investigation",
    "18. Europe's rights court backs migrant pushbacks",
    "19. Coastal storm threatens US East Coast flooding",
    "20. UK moves military aircraft to hangars at night",
    "21. Burnham vows to end NDAs shielding rich abusers",
    "22. China sentences official Ma to death over 35 leaks",
    "23. Thomas Markle indicted on child sex abuse image charges",
]

DATECHECK = [
    "Huawei convicted on 10 of 12 counts - 24 Nov",
    "Houthi strike on Riyadh tower, 11 hurt - 24 Nov",
    "Trump pardons turkeys Freedom, Feathers - 24 Nov",
    "Parastoo Ahmadi flogged 74 lashes - 23-24 Nov",
    "Indonesia candy factory fire toll 26 - 24 Nov",
    "490,334 Russian soldiers dead since 2022 - 24 Nov",
    "Saudi national kidnapped in Niger - 21-22 Nov",
    "COP31 collapses with no deal - 23 Nov",
    "FIFA names 2031 Women's Cup hosts - 24 Nov",
    "Huang reinstated as Nvidia CEO - 24 Nov",
]

NUM1 = "KOSPI -6.16%  \u2022  NIKKEI -2.78%  \u2022  TAIEX ~-5%  \u2022  DOW 50,018.70 \u2014 FIRST CLOSE ABOVE 50,000"
NUM2 = "NVIDIA -5.9%  \u2022  SOFTBANK -14.8%  \u2022  SAMSUNG -9.9%  \u2022  SUDAN 19 KILLED  \u2022  BANGLADESH WAGE +36% TO 17,000 TAKAS"
SOURCES = ("Sources: AP, Reuters, BBC, SCMP, Just Security, UN News, Xinhua, "
           "The Independent, TradingKey, dailysummaryof - verified 25 Nov 2026.")

# Map pins: (number, x, y) in canvas coords, hand-placed so none collide.
PINS = [(1, 478, 712), (2, 424, 714), (3, 462, 682), (4, 580, 704),
        (5, 546, 688), (6, 170, 772), (7, 398, 762), (8, 632, 772),
        (9, 448, 730), (10, 522, 724), (11, 600, 688), (12, 402, 720),
        (13, 378, 678)]


# -------------------------------------------------------------------- scenes
def _flame(pg, x, y, s):
    """Small flame: orange outer triangle, yellow core. (x, y) is the base."""
    pg.fill_poly([(x - s, y), (x, y - s * 2), (x + s, y)], ORANGE)
    pg.fill_poly([(x - s // 2, y), (x, y - s), (x + s // 2, y)], GOLD)


def _puff(pg, x, y, c=SMOKE):
    pg.disc(x, y, 3, c)
    pg.disc(x + 3, y - 4, 4, c)
    pg.disc(x + 1, y - 8, 4, c)


def _windows(pg, x, y, w, h, c):
    for wy in range(y + 3, y + h - 2, 6):
        for wx in range(x + 3, x + w - 3, 8):
            pg.fill(wx, wy, 3, 3, c)


def draw_scene(pg, key, x, y, w, h):
    """Small flat vector scene inside rect (x, y, w, h). No faces, no logos."""
    if key == "rocket":
        pg.fill(x, y, w, h, NAVY)
    elif key == "chart":
        pg.fill(x, y, w, h, LIGHT)
    else:
        pg.fill(x, y, w, h, SKY)

    if key == "strait":
        # sea, a dark tanker with a clear bow, two spiked mines, flame
        pg.fill(x, y + h // 2, w, h - h // 2, SEA)
        pg.fill(x + 14, y + h - 15, w - 90, 9, NAVY)
        pg.fill_poly([(x + w - 76, y + h - 15), (x + w - 58, y + h - 15),
                      (x + w - 64, y + h - 6), (x + w - 76, y + h - 6)], NAVY)
        pg.fill(x + 22, y + h - 23, 9, 8, RED)
        pg.fill(x + 38, y + h - 21, 16, 6, WHITE)
        _flame(pg, x + w // 2 - 10, y + h - 15, 4)
        for mx, my in ((x + w - 22, y + h - 5), (x + 8, y + h - 4)):
            pg.disc(mx, my, 5, INK)
            pg.segment(mx - 8, my, mx + 8, my, INK, 1)
            pg.segment(mx, my - 8, mx, my + 8, INK, 1)
        pg.segment(x + 4, y + h - 2, x + w - 4, y + h - 2, WHITE, 1)
    elif key == "gaza":
        pg.fill(x, y + h - 10, w, 10, SAND)
        for i, bh in enumerate((14, 20, 12, 17)):
            bx = x + 4 + i * (w // 4)
            pg.fill(bx, y + h - 10 - bh, w // 4 - 6, bh, NAVY)
            _windows(pg, bx, y + h - 10 - bh, w // 4 - 6, bh, GOLD)
        # cracked building: red diagonals across the second block
        pg.segment(x + w // 4 + 6, y + h - 26, x + w // 4 + 20, y + h - 12, RED, 2)
        pg.segment(x + w // 4 + 20, y + h - 28, x + w // 4 + 8, y + h - 14, RED, 2)
        _puff(pg, x + w - 16, y + 8)
        _puff(pg, x + 20, y + 6)
    elif key == "refinery":
        pg.fill(x, y + h - 8, w, 8, SAND)
        for i, tx in enumerate((x + 10, x + w // 2 - 4)):
            pg.frame(tx, y + 4, 22, h - 12, INK, 2)
            pg.segment(tx, y + 12, tx + 22, y + 12, INK, 1)
            pg.segment(tx, y + 20, tx + 22, y + 20, INK, 1)
        pg.segment(x + 32, y + h - 12, x + w - 10, y + h - 12, INK, 2)
        _flame(pg, x + w // 2 + 7, y + h - 8, 6)
        _puff(pg, x + w - 14, y + 6)
    elif key == "chart":
        pg.segment(x + 6, y + h - 7, x + w - 6, y + h - 7, INK, 2)
        pg.segment(x + 6, y + h - 7, x + 6, y + 5, INK, 2)
        rise = [(x + 8, y + h - 12), (x + 26, y + h - 16), (x + 44, y + h - 24),
                (x + 62, y + h - 20), (x + 80, y + h - 30), (x + w - 12, y + 8)]
        pg.path(rise, TEAL, 3)
        pg.path([(x + w - 12, y + 8), (x + w - 20, y + 10), (x + w - 12, y + 8),
                 (x + w - 14, y + 16)], TEAL, 2)
        fall = [(x + 8, y + 10), (x + 26, y + 14), (x + 44, y + 12),
                (x + 62, y + 20), (x + 80, y + 24), (x + w - 12, y + h - 12)]
        pg.path(fall, RED, 3)
        pg.disc(x + 44, y + h - 24, 3, RED)
    elif key == "rocket":
        # stars, a big white rocket with red nose, a station block
        for sx, sy in ((8, 6), (30, 10), (w - 12, 8), (w - 30, 14), (16, h - 6),
                       (w // 2 + 22, 6), (w - 52, h - 8), (w // 2 - 40, 8)):
            pg.disc(x + sx, y + sy, 1, WHITE)
        cx = x + w // 2 - 14
        pg.fill_poly([(cx - 7, y + h - 6), (cx - 7, y + 10), (cx, y + 2),
                      (cx + 7, y + 10), (cx + 7, y + h - 6)], WHITE)
        pg.fill_poly([(cx - 7, y + 10), (cx, y + 2), (cx + 7, y + 10)], RED)
        pg.fill_poly([(cx - 12, y + h - 10), (cx - 7, y + h - 6),
                      (cx - 7, y + h - 2)], RED)
        pg.fill_poly([(cx + 12, y + h - 10), (cx + 7, y + h - 6),
                      (cx + 7, y + h - 2)], RED)
        pg.fill(cx - 7, y + h // 2, 14, 3, TEAL)
        pg.fill_poly([(cx - 5, y + h - 6), (cx, y + h - 1), (cx + 5, y + h - 6)],
                     ORANGE)
        pg.fill_poly([(cx - 2, y + h - 6), (cx, y + h - 2), (cx + 2, y + h - 6)],
                     GOLD)
        pg.fill(x + w - 36, y + 6, 28, 7, GOLD)
        pg.fill(x + w - 30, y + 15, 16, 6, STEEL)
        pg.segment(x + w - 36, y + 9, x + w - 8, y + 9, INK, 1)
    elif key == "market":
        pg.fill(x, y + h - 8, w, 8, SAND)
        pg.fill(x + 6, y + 8, w - 12, h - 16, WHITE)
        pg.frame(x + 6, y + 8, w - 12, h - 16, INK, 1)
        # striped awning: alternating red and white bands
        for i in range(8):
            pg.fill(x + 6 + i * ((w - 12) // 8), y + 8, (w - 12) // 8, 6,
                    RED if i % 2 == 0 else WHITE)
        pg.fill(x + 10, y + h - 16, 12, 8, NAVY)
        _windows(pg, x + w - 34, y + 10, 26, h - 20, SKY)
        # shopping cart
        pg.frame(x + w - 26, y + h - 12, 18, 6, INK, 1)
        pg.disc(x + w - 22, y + h - 4, 2, INK)
        pg.disc(x + w - 12, y + h - 4, 2, INK)
    elif key == "drones":
        pg.fill(x, y + h - 10, w, 10, SAND)
        for i, bh in enumerate((12, 18, 10, 15)):
            bx = x + 4 + i * (w // 4)
            pg.fill(bx, y + h - 10 - bh, w // 4 - 6, bh, BROWN)
        _puff(pg, x + w - 18, y + 10)
        for dx, dy in ((x + w // 3, y + 8), (x + 2 * w // 3, y + 14)):
            pg.segment(dx - 6, dy - 3, dx + 6, dy + 3, INK, 2)
            pg.segment(dx - 6, dy + 3, dx + 6, dy - 3, INK, 2)
            pg.disc(dx - 7, dy - 4, 2, INK)
            pg.disc(dx + 7, dy - 4, 2, INK)
    elif key == "treaty":
        # two flag poles, a signed document with a red seal between them
        pg.fill(x, y + h - 8, w, 8, GRASS)
        pg.segment(x + 12, y + 4, x + 12, y + h - 8, INK, 2)
        pg.fill_poly([(x + 12, y + 4), (x + 38, y + 9), (x + 12, y + 14)], TEAL)
        pg.segment(x + w - 12, y + 4, x + w - 12, y + h - 8, INK, 2)
        pg.fill_poly([(x + w - 12, y + 4), (x + w - 38, y + 9), (x + w - 12, y + 14)], GOLD)
        pg.fill(x + w // 2 - 20, y + 8, 40, h - 18, WHITE)
        pg.frame(x + w // 2 - 20, y + 8, 40, h - 18, INK, 1)
        pg.segment(x + w // 2 - 15, y + 13, x + w // 2 + 15, y + 13, INK, 1)
        pg.segment(x + w // 2 - 15, y + 18, x + w // 2 + 15, y + 18, INK, 1)
        pg.disc(x + w // 2 + 12, y + h - 14, 4, RED)
    elif key == "tanks":
        pg.fill(x, y + h - 8, w, 8, SAND)
        for i, tx in enumerate((x + 6, x + w // 2 - 14, x + w - 34)):
            pg.fill(tx, y + 12, 28, h - 20, WHITE)
            pg.frame(tx, y + 12, 28, h - 20, INK, 1)
            pg.segment(tx, y + 12, tx + 28, y + 12, INK, 2)
        _flame(pg, x + w // 2, y + 12, 4)
        pg.disc(x + w // 2 + 14, y + 6, 3, SMOKE)
        pg.disc(x + w // 2 + 18, y + 2, 4, SMOKE)
        pg.segment(x + 6, y + h - 12, x + w - 6, y + h - 12, TEAL, 2)
    elif key == "factory":
        pg.fill(x, y + h - 8, w, 8, GRASS)
        # sawtooth roof + block, chimney with smoke, a shirt outline
        pg.fill_poly([(x + 6, y + 12), (x + 26, y + 4), (x + 46, y + 12),
                      (x + 66, y + 4), (x + 86, y + 12), (x + 86, y + h - 8),
                      (x + 6, y + h - 8)], NAVY)
        _windows(pg, x + 8, y + 14, 76, h - 22, SKY)
        pg.fill(x + w // 2 - 6, y + h - 18, 12, 10, RED)
        pg.fill(x + w - 16, y + 2, 8, h - 10, BROWN)
        pg.disc(x + w - 12, y + 8, 4, SMOKE)
        pg.disc(x + w - 8, y + 4, 3, SMOKE)
    elif key == "embassy":
        pg.fill(x, y + h - 8, w, 8, SAND)
        pg.fill(x + 8, y + 8, w - 40, h - 16, STEEL)
        pg.frame(x + 8, y + 8, w - 40, h - 16, INK, 1)
        _windows(pg, x + 8, y + 8, w - 40, h - 16, SKY)
        pg.fill(x + w // 2 - 5, y + h - 16, 10, 8, NAVY)
        pg.segment(x + w - 18, y + 4, x + w - 18, y + h - 8, INK, 2)
        pg.fill_poly([(x + w - 18, y + 4), (x + w - 2, y + 8), (x + w - 18, y + 12)], RED)
    elif key == "harbour":
        pg.fill(x, y + h // 2, w, h - h // 2, SEA)
        pg.fill(x, y + h - 8, w, 8, BROWN)
        # grey corvette: taller hull with bow, white superstructure, mast, flag
        pg.fill(x + 12, y + h - 20, w - 70, 10, STEEL)
        pg.fill_poly([(x + w - 58, y + h - 20), (x + w - 40, y + h - 20),
                      (x + w - 46, y + h - 10), (x + w - 58, y + h - 10)], STEEL)
        pg.fill(x + w // 2 - 14, y + h - 30, 28, 10, WHITE)
        pg.frame(x + w // 2 - 14, y + h - 30, 28, 10, INK, 1)
        mx = x + w // 2 + 8
        pg.segment(mx, y + h - 30, mx, y + 2, INK, 2)
        pg.fill_poly([(mx, y + 2), (mx + 16, y + 5), (mx, y + 8)], RED)
        pg.fill(x + w // 2 - 26, y + h - 28, 6, 8, INK)
        pg.disc(x + w // 2 - 23, y + h - 32, 4, SMOKE)
        pg.segment(x + 4, y + h - 3, x + w - 4, y + h - 3, WHITE, 1)
    elif key == "court":
        # bench, columns, judge's block, a big gavel + gold sound block
        pg.fill(x + 6, y + h - 12, w - 12, 8, BROWN)
        for cx in (x + 10, x + w - 16):
            pg.fill(cx, y + 4, 6, h - 16, STEEL)
            pg.fill(cx - 2, y + 2, 10, 3, STEEL)
        pg.fill(x + w // 2 - 20, y + 6, 40, 10, NAVY)
        pg.fill(x + w // 2 - 20, y + 16, 40, 4, GOLD)
        pg.segment(x + w // 2 - 2, y + h - 18, x + w // 2 + 14, y + h - 26, BROWN, 3)
        pg.fill(x + w // 2 + 12, y + h - 30, 12, 7, BROWN)
        pg.fill(x + w // 2 - 14, y + h - 15, 14, 3, GOLD)


# ---------------------------------------------------------------------- map
def draw_map(pg, x, y, w, h):
    pg.fill(x, y, w, h, (224, 236, 228))
    pg.frame(x, y, w, h, INK, 1)
    land = (196, 208, 170)
    # simplified continents (abstract shapes, no precise borders)
    pg.fill_poly([(x + 14, y + 14), (x + 120, y + 8), (x + 180, y + 26),
                  (x + 160, y + 64), (x + 110, y + 74), (x + 56, y + 60),
                  (x + 12, y + 40)], land)                                   # N America
    pg.fill_poly([(x + 150, y + 92), (x + 210, y + 86), (x + 232, y + 122),
                  (x + 206, y + 158), (x + 172, y + 128)], land)             # S America
    pg.fill_poly([(x + 296, y + 20), (x + 372, y + 12), (x + 392, y + 30),
                  (x + 356, y + 48), (x + 306, y + 42)], land)               # Europe
    pg.fill_poly([(x + 316, y + 58), (x + 392, y + 54), (x + 412, y + 92),
                  (x + 384, y + 136), (x + 344, y + 128), (x + 318, y + 92)], land)  # Africa
    pg.fill_poly([(x + 404, y + 14), (x + 552, y + 8), (x + 612, y + 30),
                  (x + 592, y + 76), (x + 532, y + 92), (x + 472, y + 74),
                  (x + 414, y + 56)], land)                                  # Asia
    pg.fill_poly([(x + 536, y + 114), (x + 594, y + 108), (x + 604, y + 128),
                  (x + 556, y + 136)], land)                                 # Australia
    pg.fill_poly([(x + 616, y + 104), (x + 632, y + 100), (x + 640, y + 110),
                  (x + 624, y + 116)], land)                                 # Solomons speck
    for gy in range(y + 28, y + h, 28):
        pg.segment(x, gy, x + w, gy, (200, 212, 206), 1)
    for n, px, py in PINS:
        pg.disc(px, py, 9, RED)
        pg.disc(px, py, 9, WHITE)
        pg.disc(px, py, 8, RED)
        lab = str(n)
        lw = text_width(lab, 8)
        bx = px - lw / 2
        for i, ch in enumerate(lab):
            pg.draw_glyph(ch, bx + i * STEP * 8 / 7.0, py - 4, 8, WHITE)
        pg.pins.append((px, py, n))


# -------------------------------------------------------------------- layout
def build():
    pg = Page()
    pg.fill(0, 0, W, H, PAPER)
    pg.frame(2, 2, W - 4, H - 4, INK, 2)

    # masthead
    pg.draw_text(512, 10, "THE WORLD IN ONE DAY", 42, INK, align="center")
    pg.fill(40, 56, 944, 2, RED)
    pg.draw_text(512, 62, "WEDNESDAY 25 NOVEMBER 2026  \u2022  36 STORIES",
                 15, RED, align="center")

    # numbers strip
    pg.fill(8, 82, 1008, 40, NAVY)
    pg.draw_text(512, 87, NUM1, 10, WHITE, align="center")
    pg.draw_text(512, 103, NUM2, 10, WHITE, align="center")

    # main panels: 3 columns; col 1 has 5, cols 2-3 have 4
    cols = [(8, 328, [0, 1, 2, 3, 4]), (344, 328, [5, 6, 7, 8]),
            (680, 336, [9, 10, 11, 12])]
    kick_cols = [RED, NAVY, TEAL, GOLD, RED, NAVY, TEAL, GOLD, RED,
                 NAVY, TEAL, GOLD, RED]
    for cx, cw, idxs in cols:
        n = len(idxs)
        ph = 100 if n == 5 else 125
        gap = 3 if n == 5 else 4
        big = (n == 4)
        hs = 12.5 if big else 11.5
        ss = 9 if big else 8
        slh = 11 if big else 10
        for k, i in enumerate(idxs):
            num, kick, head, sub, skey = MAIN[i]
            py = 126 + k * (ph + gap)
            pg.fill(cx, py, cw, ph, WHITE)
            pg.frame(cx, py, cw, ph, INK, 1)
            pg.fill(cx + 6, py + 4, 4, 10, kick_cols[i])
            pg.draw_text(cx + 14, py + 4, "%02d \u2022 %s" % (num, kick),
                         8.5, kick_cols[i])
            pg.draw_para(cx + 6, py + 17, head, hs, INK, cw - 12,
                         15 if big else 14, max_lines=2)
            pg.draw_para(cx + 6, py + 48 if big else py + 44, sub, ss,
                         (60, 60, 58), cw - 12, slh, max_lines=2)
            sh = 36 if big else 24
            draw_scene(pg, skey, cx + 6, py + ph - sh - 4, cw - 12, sh)

    # map + date check
    pg.draw_text(8, 644, "WHERE IT HAPPENED - 25 NOV 2026", 10, INK)
    draw_map(pg, 8, 660, 648, 168)
    dx = 664
    pg.fill(dx, 644, 352, 184, (250, 238, 220))
    pg.frame(dx, 644, 352, 184, RED, 2)
    pg.draw_text(dx + 10, 650, "DATE CHECK - NOT TODAY, LEFT OUT", 10, RED)
    pg.draw_text(dx + 10, 666, "These happened on other days - not 25 Nov:",
                 8, INK)
    for i, ln in enumerate(DATECHECK):
        ly = 682 + i * 14
        pg.fill(dx + 10, ly + 2, 4, 4, RED)
        pg.draw_text(dx + 18, ly, ln, 7.5, INK)

    # ALSO list
    pg.fill(8, 834, 1008, 2, INK)
    pg.draw_text(8, 840, "ALSO - 23 MORE STORIES FROM 25 NOVEMBER", 11, INK)
    for i, ln in enumerate(ALSO):
        col = 0 if i < 12 else 1
        row = i if i < 12 else i - 12
        pg.draw_text(8 + col * 512, 858 + row * 12, ln, 8, INK)

    # sources
    pg.draw_text(512, 1006, SOURCES, 7.5, GREY, align="center")
    return pg


# -------------------------------------------------------------------- checks
def self_check(pg, size):
    for (x0, y0, x1, y1, lab) in pg.boxes:
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            raise ValueError("text box outside canvas: %r" % lab)
    for i, a in enumerate(pg.boxes):
        for b in pg.boxes[i + 1:]:
            if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                raise ValueError("text boxes overlap: %r vs %r" % (a[4], b[4]))
    for i, a in enumerate(pg.pins):
        for b in pg.pins[i + 1:]:
            d = math.hypot(a[0] - b[0], a[1] - b[1])
            if d < 16:
                raise ValueError("map pins collide: %d and %d (%.1f px)"
                                 % (a[2], b[2], d))
    if size >= 1048576:
        raise ValueError("PNG too big: %d bytes" % size)
    if len(pg.pins) != 13:
        raise ValueError("expected 13 pins, got %d" % len(pg.pins))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if len(sys.argv) > 1:
        out_dir = sys.argv[1]
    if not out_dir:
        out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    pg = build()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, pg)
    self_check(pg, size)
    print("wrote %s (%d bytes, %d text boxes, %d pins)"
          % (path, size, len(pg.boxes), len(pg.pins)))


if __name__ == "__main__":
    main()
