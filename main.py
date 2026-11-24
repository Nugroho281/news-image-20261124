#!/usr/bin/env python3
"""THE WORLD IN ONE PAGE - Tuesday 24 November 2026.

Pure-stdlib renderer: draws a 1024x1024 newspaper front page summing up
24 November 2026 world news (44 stories, 16 pictured, 9 regions), rendered
at 2x supersample (2048x2048) and box-downscaled to 1024x1024.

All text uses a hand-built 5x7 pixel font. All pictures are flat coloured
shapes drawn in code - no text inside any illustration. No network, no
third-party packages, deterministic: two runs write byte-identical entry.png.

Usage:  MAKEFUN_OUTPUT_DIR=out python3 main.py
        VARIANT=A MAKEFUN_OUTPUT_DIR=outA python3 main.py   (alt layout)
"""
import os
import struct
import zlib

S = 2                      # supersample factor
W = 1024 * S
H = 1024 * S
VARIANT = os.environ.get("VARIANT", "B").upper()

# ---------------------------------------------------------------- font -----
# 5x7 pixel glyphs, "#" = on. Uppercase + digits + punctuation only;
# every string drawn is upper-cased by draw_text().
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    ">": ("00000", "01000", "00100", "00010", "00100", "01000", "00000"),
    "<": ("00000", "00010", "00100", "01000", "00100", "00010", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "·": ("00000", "00000", "00000", "01100", "01100", "00000", "00000"),
    "•": ("00000", "00000", "01110", "01110", "01110", "00000", "00000"),
    "°": ("01100", "10010", "01100", "00000", "00000", "00000", "00000"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
    "—": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "–": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "’": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "‘": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "“": ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "”": ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "×": ("00000", "10001", "01010", "00100", "01010", "10001", "00000"),
    "→": ("00000", "00100", "00010", "11111", "00010", "00100", "00000"),
    "★": ("00100", "00100", "11111", "01110", "01010", "10001", "10001"),
    "✓": ("00000", "00001", "00010", "10100", "01000", "00100", "00000"),
}

# ------------------------------------------------------------- canvas ------
# RGB bytearray, W*H*3. Geometry helpers take FINAL (1024) coordinates and
# scale them by S internally, so the layout reads in final pixels.
buf = bytearray(W * H * 3)


def fill(rgb):
    r, g, b = rgb
    row = bytes((r, g, b)) * W
    for y in range(H):
        buf[y * W * 3:(y + 1) * W * 3] = row


def rect(x, y, w, h, rgb):
    """Filled rectangle, clipped to canvas. x,y,w,h in final pixels."""
    x0 = max(0, int(x * S))
    y0 = max(0, int(y * S))
    x1 = min(W, int((x + w) * S))
    y1 = min(H, int((y + h) * S))
    if x1 <= x0 or y1 <= y0:
        return
    r, g, b = rgb
    row = bytes((r, g, b)) * (x1 - x0)
    for yy in range(y0, y1):
        buf[yy * W * 3 + x0 * 3: yy * W * 3 + x1 * 3] = row


def hline(x, y, w, rgb, th=1):
    rect(x, y, w, th, rgb)


def vline(x, y, h, rgb, th=1):
    rect(x, y, th, h, rgb)


def circle(cx, cy, r, rgb):
    """Filled circle, centre/radius in final pixels."""
    cx2, cy2, r2 = int(cx * S), int(cy * S), int(r * S)
    rr = r2 * r2
    for yy in range(cy2 - r2, cy2 + r2 + 1):
        dy = yy - cy2
        dx = int((rr - dy * dy) ** 0.5)
        y0 = max(0, yy)
        if y0 > H - 1:
            continue
        x0 = max(0, cx2 - dx)
        x1 = min(W, cx2 + dx + 1)
        if x1 <= x0:
            continue
        buf[y0 * W * 3 + x0 * 3: y0 * W * 3 + x1 * 3] = bytes(rgb) * (x1 - x0)


def tri(p1, p2, p3, rgb):
    """Filled triangle from three (x, y) final-pixel points."""
    pts = sorted([(p1[0] * S, p1[1] * S), (p2[0] * S, p2[1] * S),
                  (p3[0] * S, p3[1] * S)], key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = pts
    if ay == cy:
        return
    def edge(x1, y1, x2, y2, y):
        if y2 == y1:
            return x1
        return x1 + (x2 - x1) * (y - y1) / (y2 - y1)
    for yy in range(max(0, int(ay)), min(H, int(cy) + 1)):
        if yy < by:
            xa = edge(ax, ay, bx, by, yy)
            xb = edge(ax, ay, cx, cy, yy)
        else:
            xa = edge(bx, by, cx, cy, yy)
            xb = edge(ax, ay, cx, cy, yy)
        x0 = max(0, int(min(xa, xb)))
        x1 = min(W, int(max(xa, xb)) + 1)
        if x1 > x0:
            buf[yy * W * 3 + x0 * 3: yy * W * 3 + x1 * 3] = bytes(rgb) * (x1 - x0)


def poly(points, rgb):
    """Filled polygon from a list of (x, y) final-pixel points."""
    for i in range(1, len(points) - 1):
        tri(points[0], points[i], points[i + 1], rgb)


# -------------------------------------------------------------- text -------
def text_w(s, size):
    """Width in final pixels of s at cap-height `size` (final px)."""
    return len(s.upper()) * 6 * size / 7.0


def draw_text(x, y, s, size, rgb, align="l"):
    """Draw s with top-left (x, y) in final pixels; size = cap height."""
    s = s.upper()
    unit = size / 7.0
    px = max(1, int(round(unit)))
    w = text_w(s, size)
    if align == "c":
        x -= w / 2.0
    elif align == "r":
        x -= w
    cx = int(x * S)
    cy = int(y * S)
    for ch in s:
        g = GLYPHS.get(ch, GLYPHS[" "])
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == "1":
                    x0 = cx + col * px
                    y0 = cy + row * px
                    rect(x0 / S, y0 / S, px / S, px / S, rgb)
        cx += 6 * px
    return w


def wrap(s, size, max_w):
    """Greedy word wrap; returns list of lines, each <= max_w final px."""
    words = s.upper().split()
    lines, cur = [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(trial, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def text_block(x, y, lines, size, rgb, leading=None):
    """Draw pre-wrapped lines; returns y just below the block."""
    lead = leading if leading is not None else size * 1.32
    for ln in lines:
        draw_text(x, y, ln, size, rgb)
        y += lead
    return y


def fit_lines(s, size, max_w, max_lines):
    """Wrap s; if it overflows max_lines, shorten with an ellipsis."""
    lines = wrap(s, size, max_w)
    if len(lines) <= max_lines:
        return lines
    out = lines[:max_lines]
    last = out[-1]
    while last and text_w(last + " ...", size) > max_w:
        last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
    out[-1] = (last + " ...").strip()
    return out


# --------------------------------------------------------------- png --------
def png_bytes(rgb_rows, w, h):
    """Encode RGB rows (bytes per row = w*3) as a PNG (filter 0)."""
    raw = b"".join(b"\x00" + row for row in rgb_rows)
    comp = zlib.compress(raw, 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def downscale_png():
    """Box-average the 2048 canvas to 1024 and return PNG bytes."""
    rows = []
    for y in range(1024):
        row = bytearray()
        y0 = y * 2
        for x in range(1024):
            x0 = x * 2
            tot = [0, 0, 0]
            for dy in (0, 1):
                base = (y0 + dy) * W * 3 + x0 * 3
                for dx in (0, 1):
                    o = base + dx * 3
                    tot[0] += buf[o]
                    tot[1] += buf[o + 1]
                    tot[2] += buf[o + 2]
            row += bytes((tot[0] // 4, tot[1] // 4, tot[2] // 4))
        rows.append(bytes(row))
    return png_bytes(rows, 1024, 1024)

# ------------------------------------------------------------ palette ------
PAPER = (247, 241, 227)      # warm cream page
INK = (24, 24, 26)           # near-black text
NAVY = (16, 30, 51)          # dark masthead / rail
NAVY2 = (24, 46, 78)         # lighter navy panel
GOLD = (217, 164, 65)        # gold accents / numbers
GOLD_LT = (240, 203, 120)
RED = (178, 34, 28)          # kicker red
RED_DK = (140, 29, 24)       # variant A masthead
GREEN = (46, 139, 87)        # market green
GREEN_DK = (28, 94, 58)
BLUE = (38, 84, 150)
SKY = (126, 178, 214)
GREY = (120, 118, 112)
GREY_LT = (226, 220, 206)
WHITE = (255, 255, 255)
CREAM_TX = (244, 238, 224)
ORANGE = (214, 110, 44)
TEAL = (32, 128, 128)

# ------------------------------------------------------------ content ------
DATE_LINE = "TUESDAY · 24 NOVEMBER 2026"
SUB_LINE = "44 STORIES · 16 PICTURED · 9 REGIONS · ONE DAY IN UTC"

HERO = {
    "kicker": "MARKETS · AI RALLY",
    "head": "NVIDIA SOARS 31.5% AS HUANG RETURNS",
    "body": ("Nvidia adds about $950bn in one day - its biggest jump - as "
             "the board reinstates Jensen Huang. Asia follows: Kospi tops "
             "5,000, TSMC up 10%."),
}

NUMBERS = [
    ("+31.5%", "NVIDIA IN A DAY"),
    ("$950BN", "VALUE ADDED"),
    ("5,006", "KOSPI CLOSE"),
    ("74", "LASHES FOR SINGER"),
    ("26", "BODY BAGS, BANTEN"),
]

MIDDLE = [
    {"kicker": "UKRAINE · WAR",
     "head": "RUSSIAN STRIKE ON ZAPORIZHZHIA KILLS 2",
     "body": ("Guided bombs hit the city overnight, partly collapsing a "
              "five-storey block; 22 injured."),
     "pic": "building"},
    {"kicker": "US · CHIPS",
     "head": "US BLACKLISTS MEGASPEED OVER CHINA CHIPS",
     "body": ("Singapore firm blacklisted; six more firms join it."),
     "pic": "chipban"},
    {"kicker": "EUROPE · SANCTIONS",
     "head": "EU PROPOSES 22ND SANCTIONS ON RUSSIA",
     "body": ("60 more banks, 70-plus shadow-fleet ships, a sports ban; "
              "states must still agree."),
     "pic": "bank"},
]

GRID = [
    {"kicker": "MISSILES", "head": "UKRAINE, GERMANY AGREE MORE INTERCEPTORS",
     "body": "Berlin agrees steps to send more interceptors.",
     "pic": "missile"},
    {"kicker": "US COURTS", "head": "TRUMP GETS PATH TO ERASE HUSH-MONEY CASE",
     "body": "Court move opens immunity defence.",
     "pic": "gavel"},
    {"kicker": "HORMUZ", "head": "THREE TANKERS ABLAZE AFTER HITTING MINES",
     "body": "Iran blames mines; 25 dead.",
     "pic": "tanker"},
    {"kicker": "IRAN", "head": "SINGER FLOGGED 74 TIMES WITHOUT HIJAB",
     "body": "Parastoo Ahmadi and four colleagues flogged by court.",
     "pic": "mic"},
    {"kicker": "GAZA", "head": "ISRAELI STRIKES KILL 3, INCL. UN WORKER",
     "body": "UNRWA worker dies at Jabalia well; baby dies of cold.",
     "pic": "tent"},
    {"kicker": "KOREA", "head": "RUSSIAN JETS SPARK ALERT ON KOREAN ISLAND",
     "body": "Seoul briefly warns Ulleung islanders to shelter.",
     "pic": "jet"},
    {"kicker": "PACIFIC", "head": "SOLOMONS TO DROP CHINA PACT FOR AUSTRALIA",
     "body": "Honiara will not renew its 2022 pact with Beijing.",
     "pic": "island"},
    {"kicker": "INDONESIA", "head": "BANTEN FACTORY FIRE TOLL: 26 BODY BAGS",
     "body": "26 dead; two VP picks named.",
     "pic": "factory"},
    {"kicker": "US JUSTICE", "head": "TRUMP ORDERS FASTER FEDERAL EXECUTIONS",
     "body": "He attacks Newsom over 548 commutations.",
     "pic": "scales"},
    {"kicker": "SPAIN", "head": "SPAIN'S PP LEADS POLLS BEFORE SUNDAY VOTE",
     "body": "Conservatives lead; a coalition with Vox looms.",
     "pic": "ballot"},
    {"kicker": "CLIMATE", "head": "COP31 FALLOUT: ISLANDS LEAVE EMPTY-HANDED",
     "body": "No finance deal for Pacific states; COP32 next.",
     "pic": "globe"},
    {"kicker": "SPORT", "head": "COMMANDERS STUN BENGALS 22-20",
     "body": "Daniels drives 64 yards in 39 seconds for the winner.",
     "pic": "ball"},
]

BRIEFS = [
    "Zelensky wants four-party talks",
    "Hacked data: 490,000 war dead",
    "Russia may put nuke in space",
    "NATO AWACS planes for Poland",
    "$15bn Iran shadow banks exposed",
    "Iran seeks $290bn damages from US",
    "US-Qatar dialogue opens in DC",
    "China death sentence for spying",
    "Beijing warns chip risks remain",
    "Singapore-Australia sign pacts",
    "Oil down 3%; Libya pipeline back",
    "DRC fighting traps Ebola teams",
    "14 nations back Rohingya ruling",
    "S. Africa mourns Mlambo-Ngcuka",
    "US envoy regrets Sudan violence",
    "Colombia car bomb at governor HQ",
    "Pennsylvania measles death No. 9",
    "Danish court backs 'ghetto law'",
    "WHO chief visits Cuba amid strain",
    "FDA approves breast-cancer drug",
    "NHS starts AI screening trial",
    "Rangers beat Motherwell 2-1 late",
    "West Ham 4-2 Wolves, first win",
    "Trump approval 45%, a term low",
    "Seoul names new foreign minister",
    "Russia expands base near Finland",
    "India leader barred from UK trip",
    "Australia: 5% fines on platforms",
]

TIMELINE = [
    ("OVERNIGHT", "ZAPORIZHZHIA HIT"),
    ("MORNING", "ASIA CHIPS SOAR"),
    ("MIDDAY", "EU SANCTIONS"),
    ("AFTERNOON", "MEGASPEED BAN"),
    ("EVENING", "TRUMP COURT WIN"),
]

SOURCES = ("SOURCES: BBC · REUTERS · AP · AL JAZEERA · GUARDIAN · EURONEWS · "
           "YONHAP · ANTARA · DETIK · NPR")
FOOTER = "ALL STORIES FIRST REPORTED TUESDAY 24 NOVEMBER 2026 · DRAWN BY CODE, NO PHOTOGRAPHS"

# ------------------------------------------------------- illustrations -----
# Flat shapes drawn in code; no text inside any illustration.
def pic_chart(x, y, w, h):
    """Hero: rising market bars + chip on a deep-green field."""
    rect(x, y, w, h, GREEN_DK)
    rect(x, y + h - 14, w, 14, (18, 64, 40))
    bars = [0.22, 0.34, 0.30, 0.46, 0.42, 0.60, 0.55, 0.78]
    bw = w / 12.0
    for i, f in enumerate(bars):
        bh = f * (h - 34)
        rect(x + 14 + i * (bw + 4), y + h - 16 - bh, bw, bh, GREEN)
    rect(x + 14, y + h - 16 - 0.60 * (h - 34) - 8, w - 28, 4, GOLD)
    # chip at right
    cx, cy, cw = x + w - 78, y + 16, 58
    rect(cx, cy, cw, 44, NAVY)
    rect(cx + 8, cy + 8, cw - 16, 28, GOLD)
    rect(cx + 20, cy + 16, cw - 40, 12, NAVY)
    for k in range(4):
        rect(cx + 6 + k * 14, cy - 6, 4, 6, GOLD)
        rect(cx + 6 + k * 14, cy + 44, 4, 6, GOLD)
        rect(cx - 6, cy + 6 + k * 10, 6, 4, GOLD)
        rect(cx + cw, cy + 6 + k * 10, 6, 4, GOLD)


def pic_building(x, y, w, h):
    """Damaged apartment block, smoke, rescue light."""
    rect(x, y, w, h, (58, 64, 78))
    rect(x, y, w, h * 0.42, (196, 120, 78))
    rect(x + 8, y + h * 0.42, w - 16, h * 0.58, (88, 90, 98))
    # broken top edge
    tri((x + 8, y + h * 0.42), (x + w * 0.45, y + h * 0.42),
        (x + w * 0.30, y + h * 0.20), (58, 64, 78))
    tri((x + w * 0.55, y + h * 0.42), (x + w - 8, y + h * 0.42),
        (x + w * 0.80, y + h * 0.28), (58, 64, 78))
    # windows
    for r in range(2):
        for c in range(4):
            rect(x + 16 + c * (w - 32) / 4, y + h * 0.52 + r * h * 0.22,
                 (w - 32) / 5, h * 0.13, GOLD_LT if (r + c) % 3 else (40, 42, 50))
    # smoke puffs
    circle(x + w * 0.30, y + h * 0.16, 7, (200, 198, 192))
    circle(x + w * 0.72, y + h * 0.22, 6, (200, 198, 192))
    rect(x, y + h - 6, w, 6, RED)


def pic_chipban(x, y, w, h):
    """Chip with a red ban ring over it."""
    rect(x, y, w, h, NAVY2)
    cx, cy = x + w / 2, y + h / 2
    rect(cx - 22, cy - 16, 44, 32, (20, 20, 24))
    rect(cx - 14, cy - 8, 28, 16, GOLD)
    rect(cx - 6, cy - 3, 12, 6, NAVY2)
    for k in range(3):
        rect(cx - 18 + k * 14, cy - 22, 4, 6, GOLD)
        rect(cx - 18 + k * 14, cy + 16, 4, 6, GOLD)
        rect(cx - 28, cy - 12 + k * 10, 6, 4, GOLD)
        rect(cx + 22, cy - 12 + k * 10, 6, 4, GOLD)
    circle(cx, cy, 30, RED)
    circle(cx, cy, 24, NAVY2)
    rect(cx - 22, cy - 16, 44, 32, (20, 20, 24))
    rect(cx - 14, cy - 8, 28, 16, GOLD)
    # slash
    poly([(cx - 26, cy + 14), (cx - 18, cy + 20), (cx + 26, cy - 14),
          (cx + 18, cy - 20)], RED)


def pic_bank(x, y, w, h):
    """Bank building with EU-style star ring."""
    rect(x, y, w, h, (52, 74, 120))
    rect(x + w * 0.18, y + h * 0.30, w * 0.64, h * 0.62, (232, 228, 214))
    tri((x + w * 0.10, y + h * 0.32), (x + w * 0.90, y + h * 0.32),
        (x + w / 2, y + h * 0.08), GOLD)
    for c in range(4):
        rect(x + w * 0.24 + c * w * 0.15, y + h * 0.42, w * 0.07, h * 0.42,
             (52, 74, 120))
    rect(x + w * 0.10, y + h * 0.88, w * 0.80, h * 0.08, (232, 228, 214))
    # stars arc
    for k in range(5):
        circle(x + w * 0.14 + k * w * 0.18, y + h * 0.16, 2.5, GOLD)


def pic_missile(x, y, w, h):
    rect(x, y, w, h, SKY)
    rect(x, y + h - 8, w, 8, (70, 90, 110))
    poly([(x + 12, y + h * 0.55), (x + w - 12, y + h * 0.55),
          (x + w / 2, y + h * 0.15)], (220, 224, 228))
    rect(x + w / 2 - 5, y + h * 0.50, 10, h * 0.30, (220, 224, 228))
    poly([(x + w / 2 - 16, y + h * 0.82), (x + w / 2 - 5, y + h * 0.60),
          (x + w / 2 - 5, y + h * 0.82)], RED)
    poly([(x + w / 2 + 16, y + h * 0.82), (x + w / 2 + 5, y + h * 0.60),
          (x + w / 2 + 5, y + h * 0.82)], RED)
    tri((x + w / 2 - 6, y + h * 0.80), (x + w / 2 + 6, y + h * 0.80),
        (x + w / 2, y + h * 0.98), ORANGE)


def pic_gavel(x, y, w, h):
    rect(x, y, w, h, (72, 56, 44))
    rect(x + 8, y + h * 0.30, w - 16, 10, (150, 110, 62))
    rect(x + w / 2 - 4, y + h * 0.30, 8, h * 0.55, (150, 110, 62))
    tri((x + w * 0.30, y + h * 0.22), (x + w * 0.70, y + h * 0.22),
        (x + w / 2, y + h * 0.05), GOLD)
    rect(x + 12, y + h * 0.86, w - 24, 6, GOLD)


def pic_tanker(x, y, w, h):
    rect(x, y, w, h, (28, 44, 66))
    rect(x, y + h * 0.55, w, h * 0.45, (26, 84, 122))
    rect(x + 8, y + h * 0.34, w - 16, h * 0.24, (176, 52, 40))
    rect(x + w * 0.60, y + h * 0.16, w * 0.22, h * 0.20, (232, 228, 214))
    tri((x + w * 0.30, y + h * 0.34), (x + w * 0.42, y + h * 0.34),
        (x + w * 0.36, y + h * 0.14), ORANGE)
    tri((x + w * 0.44, y + h * 0.34), (x + w * 0.56, y + h * 0.34),
        (x + w * 0.50, y + h * 0.10), GOLD)
    circle(x + w * 0.36, y + h * 0.06, 4, (200, 198, 192))


def pic_mic(x, y, w, h):
    rect(x, y, w, h, (74, 34, 58))
    circle(x + w / 2, y + h * 0.34, h * 0.24, (220, 216, 204))
    rect(x + w / 2 - 3, y + h * 0.52, 6, h * 0.28, (200, 196, 184))
    rect(x + w / 2 - 14, y + h * 0.80, 28, 5, (200, 196, 184))
    for k in range(3):
        rect(x + w / 2 - 12 + k * 9, y + h * 0.26, 4, h * 0.14, (74, 34, 58))


def pic_tent(x, y, w, h):
    rect(x, y, w, h, (214, 176, 120))
    tri((x + 6, y + h * 0.86), (x + w - 6, y + h * 0.86),
        (x + w / 2, y + h * 0.18), (240, 238, 226))
    tri((x + w / 2 - 12, y + h * 0.86), (x + w / 2 + 12, y + h * 0.86),
        (x + w / 2, y + h * 0.52), (60, 66, 76))
    rect(x, y + h * 0.86, w, h * 0.14, (120, 92, 58))
    circle(x + w * 0.78, y + h * 0.22, 8, GOLD)


def pic_jet(x, y, w, h):
    rect(x, y, w, h, (160, 190, 214))
    poly([(x + 8, y + h * 0.52), (x + w - 8, y + h * 0.52),
          (x + w * 0.62, y + h * 0.30)], (232, 236, 240))
    tri((x + w * 0.62, y + h * 0.30), (x + w * 0.86, y + h * 0.44),
        (x + w * 0.62, y + h * 0.52), (200, 204, 208))
    tri((x + w * 0.40, y + h * 0.52), (x + w * 0.55, y + h * 0.52),
        (x + w * 0.45, y + h * 0.78), RED)
    circle(x + w * 0.80, y + h * 0.50, 3, NAVY)


def pic_island(x, y, w, h):
    rect(x, y, w, h, (120, 190, 214))
    rect(x, y + h * 0.66, w, h * 0.34, (26, 84, 122))
    poly([(x + 8, y + h * 0.66), (x + w * 0.55, y + h * 0.66),
          (x + w * 0.30, y + h * 0.48)], (232, 206, 140))
    rect(x + w * 0.58, y + h * 0.28, 5, h * 0.40, (120, 90, 50))
    tri((x + w * 0.58, y + h * 0.28), (x + w * 0.86, y + h * 0.20),
        (x + w * 0.62, y + h * 0.34), GREEN)
    tri((x + w * 0.58, y + h * 0.28), (x + w * 0.32, y + h * 0.22),
        (x + w * 0.54, y + h * 0.36), GREEN_DK)
    circle(x + w * 0.18, y + h * 0.20, 9, GOLD)


def pic_factory(x, y, w, h):
    rect(x, y, w, h, (96, 92, 88))
    rect(x + 8, y + h * 0.44, w - 16, h * 0.42, (196, 90, 60))
    poly([(x + 8, y + h * 0.44), (x + w * 0.36, y + h * 0.44),
          (x + w * 0.36, y + h * 0.24), (x + w * 0.22, y + h * 0.44)],
         (196, 90, 60))
    poly([(x + w * 0.36, y + h * 0.44), (x + w * 0.64, y + h * 0.44),
          (x + w * 0.64, y + h * 0.24), (x + w * 0.50, y + h * 0.44)],
         (196, 90, 60))
    rect(x + w * 0.70, y + h * 0.18, w * 0.14, h * 0.68, (150, 146, 138))
    circle(x + w * 0.77, y + h * 0.10, 6, (200, 198, 192))
    rect(x + 16, y + h * 0.56, w * 0.10, h * 0.16, GOLD_LT)
    rect(x + w * 0.42, y + h * 0.56, w * 0.10, h * 0.16, GOLD_LT)


def pic_scales(x, y, w, h):
    rect(x, y, w, h, NAVY2)
    rect(x + w / 2 - 2, y + h * 0.18, 4, h * 0.58, GOLD)
    rect(x + w * 0.18, y + h * 0.18, w * 0.64, 4, GOLD)
    tri((x + w * 0.18, y + h * 0.24), (x + w * 0.36, y + h * 0.24),
        (x + w * 0.27, y + h * 0.56), GOLD_LT)
    tri((x + w * 0.64, y + h * 0.24), (x + w * 0.82, y + h * 0.24),
        (x + w * 0.73, y + h * 0.56), GOLD_LT)
    rect(x + w / 2 - 14, y + h * 0.78, 28, 5, GOLD)


def pic_ballot(x, y, w, h):
    rect(x, y, w, h, (196, 60, 52))
    rect(x + w * 0.20, y + h * 0.34, w * 0.60, h * 0.46, (244, 240, 228))
    rect(x + w * 0.38, y + h * 0.22, w * 0.24, h * 0.16, WHITE)
    rect(x + w * 0.46, y + h * 0.14, 4, h * 0.20, NAVY)
    rect(x + w * 0.30, y + h * 0.30, w * 0.40, 3, RED)
    for k in range(3):
        rect(x + w * 0.30, y + h * 0.44 + k * h * 0.10, w * 0.40, 3,
             (180, 176, 164))


def pic_globe(x, y, w, h):
    rect(x, y, w, h, (26, 84, 122))
    circle(x + w / 2, y + h / 2, min(w, h) * 0.38, (60, 140, 90))
    circle(x + w / 2, y + h / 2, min(w, h) * 0.38, (60, 140, 90))
    # land blobs
    circle(x + w * 0.40, y + h * 0.38, 7, GREEN)
    circle(x + w * 0.58, y + h * 0.55, 6, GREEN)
    circle(x + w * 0.62, y + h * 0.36, 4, GREEN)
    # leaf (climate)
    tri((x + w * 0.72, y + h * 0.20), (x + w * 0.88, y + h * 0.28),
        (x + w * 0.70, y + h * 0.36), GOLD)


def pic_ball(x, y, w, h):
    rect(x, y, w, h, GREEN_DK)
    rect(x, y + h * 0.72, w, h * 0.28, GREEN)
    for k in range(4):
        rect(x + k * w / 4, y + h * 0.72, 2, h * 0.28, (220, 226, 220))
    circle(x + w / 2, y + h * 0.40, min(w, h) * 0.30, WHITE)
    poly([(x + w / 2 - 6, y + h * 0.40 - 8), (x + w / 2 + 6, y + h * 0.40 - 8),
          (x + w / 2 + 10, y + h * 0.40 + 2), (x + w / 2, y + h * 0.40 + 9),
          (x + w / 2 - 10, y + h * 0.40 + 2)], INK)


PICS = {"chart": pic_chart, "building": pic_building, "chipban": pic_chipban,
        "bank": pic_bank, "missile": pic_missile, "gavel": pic_gavel,
        "tanker": pic_tanker, "mic": pic_mic, "tent": pic_tent,
        "jet": pic_jet, "island": pic_island, "factory": pic_factory,
        "scales": pic_scales, "ballot": pic_ballot, "globe": pic_globe,
        "ball": pic_ball}


# -------------------------------------------------------------- layout -----
MX = 16          # side margin, final px
CW = 992         # content width


def masthead(navy=True):
    """Top band: title, date line, story count, DATE-CHECKED cell."""
    bg = NAVY if navy else RED_DK
    rect(0, 0, 1024, 124, bg)
    rect(0, 120, 1024, 4, GOLD if navy else (232, 220, 200))
    draw_text(MX, 12, "THE WORLD IN ONE PAGE", 40, CREAM_TX)
    draw_text(MX, 62, DATE_LINE, 19, GOLD_LT if navy else (255, 214, 160))
    draw_text(MX, 90, SUB_LINE, 12, CREAM_TX)
    # DATE-CHECKED cell, right side
    cx, cy, cw2, ch = 1024 - MX - 210, 12, 210, 100
    rect(cx, cy, cw2, ch, NAVY2 if navy else (120, 20, 16))
    rect(cx, cy, cw2, ch, GOLD if navy else (232, 220, 200))
    # inner fill to fake a border
    rect(cx + 2, cy + 2, cw2 - 4, ch - 4, NAVY2 if navy else (120, 20, 16))
    draw_text(cx + cw2 / 2, cy + 8, "DATE-CHECKED", 15, GOLD, align="c")
    draw_text(cx + cw2 / 2, cy + 30, "24 NOV 2026", 22, WHITE, align="c")
    draw_text(cx + cw2 / 2, cy + 58, "ALL STORIES FIRST", 12, CREAM_TX,
              align="c")
    draw_text(cx + cw2 / 2, cy + 74, "REPORTED TODAY", 12, CREAM_TX,
              align="c")


def numbers_rail(x, y, w, h, navy=True):
    """Day-in-numbers rail: big gold figures, one per row."""
    rect(x, y, w, h, NAVY if navy else (240, 232, 214))
    draw_text(x + 10, y + 8, "THE DAY IN NUMBERS", 12,
              GOLD if navy else RED_DK)
    hline(x + 10, y + 28, w - 20, GOLD if navy else RED_DK, 2)
    yy = y + 36
    for big, small in NUMBERS:
        draw_text(x + 10, yy, big, 20, GOLD_LT if navy else RED_DK)
        draw_text(x + 10, yy + 21, small, 9, CREAM_TX if navy else INK)
        yy += 32


def numbers_strip(x, y, w, h):
    """Variant A: the same five numbers in two rows of three."""
    rect(x, y, w, h, (240, 232, 214))
    rect(x, y, w, h, RED_DK)
    rect(x + 2, y + 2, w - 4, h - 4, (240, 232, 214))
    colw = (w - 20) / 3.0
    for i, (big, small) in enumerate(NUMBERS):
        cx = x + 10 + (i % 3) * colw
        cy = y + 5 + (i // 3) * 18
        draw_text(cx, cy, big + " " + small, 13, RED_DK)


def hero_panel(x, y, w, h, navy=True, body_lines=4, label=True,
               body_text=None):
    """Wide hero: kicker + headline + body left, chart art right."""
    rect(x, y, w, h, WHITE)
    rect(x, y, w, h, GREY)
    rect(x + 2, y + 2, w - 4, h - 4, WHITE)
    tx = x + 14
    tw = w - 300
    draw_text(tx, y + 10, HERO["kicker"], 14, RED)
    head = fit_lines(HERO["head"], 26, tw, 2)
    yy = text_block(tx, y + 30, head, 26, INK, leading=30)
    body = fit_lines(body_text if body_text is not None else HERO["body"],
                     14, tw, body_lines)
    text_block(tx, yy + 6, body, 14, (52, 52, 54), leading=17)
    PICS["chart"](x + w - 282, y + 12, 268, h - 24)
    if label:
        draw_text(tx, y + h - 22, "WALL STREET + ASIA · TUESDAY",
                  11, GREY)


def middle_row(y, h, navy=True):
    """Three panels: art strip on top, headline + body below."""
    pw = (CW - 2 * 16) / 3.0
    for i, m in enumerate(MIDDLE):
        x = MX + i * (pw + 16)
        rect(x, y, pw, h, WHITE)
        rect(x, y, pw, h, GREY)
        rect(x + 2, y + 2, pw - 4, h - 4, WHITE)
        PICS[m["pic"]](x + 2, y + 2, pw - 4, 46)
        draw_text(x + 10, y + 52, m["kicker"], 11, RED)
        head = fit_lines(m["head"], 15, pw - 20, 2)
        yy = text_block(x + 10, y + 68, head, 15, INK, leading=17)
        body = fit_lines(m["body"], 11, pw - 20, 3)
        text_block(x + 10, yy + 2, body, 11, (52, 52, 54), leading=13.5)


def grid_panel(x, y, w, h):
    """One grid cell: art at left, kicker + headline + body at right."""
    g = GRID[grid_panel.idx]
    grid_panel.idx += 1
    rect(x, y, w, h, WHITE)
    rect(x, y, w, h, GREY)
    rect(x + 2, y + 2, w - 4, h - 4, WHITE)
    PICS[g["pic"]](x + 2, y + 2, 52, h - 4)
    tx = x + 62
    tw = w - 70
    draw_text(tx, y + 5, g["kicker"], 10, RED)
    head = fit_lines(g["head"], 12, tw, 2)
    yy = text_block(tx, y + 17, head, 12, INK, leading=13.5)
    body = fit_lines(g["body"], 10, tw, 2)
    text_block(tx, yy + 2, body, 10, (52, 52, 54), leading=12)


grid_panel.idx = 0


def grid_block(y):
    """12 grid panels: 3 columns x 4 rows."""
    pw = (CW - 2 * 16) / 3.0
    ph = 74
    for r in range(4):
        for c in range(3):
            grid_panel(MX + c * (pw + 16), y + r * (ph + 8), pw, ph)


def timeline_strip(y, h):
    rect(MX, y, CW, h, NAVY)
    draw_text(MX + 10, y + 5, "THE DAY IN UTC", 12, GOLD)
    cw2 = (CW - 170) / 5.0
    for i, (part, event) in enumerate(TIMELINE):
        x = MX + 170 + i * cw2
        if i:
            vline(x - 6, y + 5, h - 10, NAVY2, 2)
        draw_text(x, y + 4, part, 10, GOLD_LT)
        ev = fit_lines(event, 11, cw2 - 12, 1)
        draw_text(x, y + 19, ev[0], 11, WHITE)


def briefs_block(y, h):
    """In-brief: 3 columns x 10 rows of one-liners."""
    rect(MX, y, CW, h, WHITE)
    rect(MX, y, CW, h, GREY)
    rect(MX + 2, y + 2, CW - 4, h - 4, WHITE)
    draw_text(MX + 10, y + 5, "IN BRIEF", 14, RED)
    hline(MX + 10, y + 22, CW - 20, GREY_LT, 2)
    colw = (CW - 20) / 3.0
    for i, b in enumerate(BRIEFS):
        c, r = i % 3, i // 3
        x = MX + 10 + c * colw
        yy = y + 27 + r * 10.5
        draw_text(x, yy, "•", 10, RED)
        line = fit_lines(b, 10, colw - 22, 1)
        draw_text(x + 10, yy, line[0], 10, INK)


def footer(y):
    draw_text(512, y, SOURCES, 9, GREY, align="c")
    draw_text(512, y + 11, FOOTER, 9, GREY, align="c")


def render_a():
    """Variant A: warm-paper front page, red masthead, numbers as a strip."""
    fill(PAPER)
    masthead(navy=False)
    numbers_strip(MX, 132, CW, 40)
    hero_panel(MX, 180, CW, 148, navy=False, body_lines=2, label=False,
               body_text=("Nvidia adds $950bn in a day as Huang returns; "
                          "Asia follows: Kospi tops 5,000."))
    middle_row(336, 144, navy=False)
    grid_block(488)
    timeline_strip(816, 38)
    briefs_block(862, 136)
    footer(1002)


def render_b():
    """Variant B: dark-navy masthead + day-in-numbers rail beside wide hero."""
    fill(PAPER)
    masthead(navy=True)
    numbers_rail(MX, 132, 196, 196, navy=True)
    hero_panel(MX + 204, 132, CW - 204, 196, navy=True)
    middle_row(336, 144, navy=True)
    grid_block(488)
    timeline_strip(816, 38)
    briefs_block(862, 136)
    footer(1002)


def main():
    if VARIANT == "A":
        render_a()
    else:
        render_b()
    data = downscale_png()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(data)
    print("wrote", path, len(data), "bytes, variant", VARIANT)


if __name__ == "__main__":
    main()
