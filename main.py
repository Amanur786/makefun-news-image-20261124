#!/usr/bin/env python3
"""THE DAY IN BRIEF — Tuesday 24 November 2026.

A pure-Pillow program that draws a one-page broadsheet poster summing up
the world news of Tuesday 24 November 2026. It writes entry.png (1024x1024)
next to this file. No network, no input files, fully deterministic: two
runs write byte-identical output.

Run:  python3 main.py
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- palette
PAPER = (248, 244, 233)
CARD = (255, 252, 244)
TEAL = (15, 61, 62)
TEAL_SOFT = (226, 236, 234)
CRIMSON = (178, 32, 32)
CRIMSON_DARK = (140, 20, 20)
INK = (24, 24, 22)
MUTED = (105, 100, 88)
RULE = (190, 183, 164)
OCEAN = (43, 102, 168)
LEAF = (52, 148, 88)
GOLD = (212, 160, 40)
AMBER = (245, 130, 32)
WHITE = (255, 255, 255)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def load(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, font, max_width):
    """Greedy word wrap; returns the lines that fit inside max_width."""
    lines = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, x, y, lines, font, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


# ------------------------------------------------------------------ icons
def draw_globe(draw, cx, cy, radius):
    """Blue globe with green continents, white meridians and a red crack."""
    box = [cx - radius, cy - radius, cx + radius, cy + radius]
    draw.ellipse(box, fill=OCEAN, outline=TEAL, width=3)
    # continents: simple blobby polygons clipped by hand to the circle
    land = [
        [(cx - 52, cy - 30), (cx - 28, cy - 52), (cx - 6, cy - 34),
         (cx - 18, cy - 8), (cx - 44, cy - 6)],
        [(cx + 8, cy - 44), (cx + 38, cy - 52), (cx + 52, cy - 26),
         (cx + 30, cy - 12), (cx + 12, cy - 22)],
        [(cx - 40, cy + 18), (cx - 10, cy + 8), (cx + 4, cy + 30),
         (cx - 22, cy + 48), (cx - 46, cy + 40)],
        [(cx + 26, cy + 22), (cx + 50, cy + 34), (cx + 40, cy + 56),
         (cx + 18, cy + 48)],
    ]
    for poly in land:
        draw.polygon(poly, fill=LEAF)
    # latitude lines
    for frac, half in ((0.45, 0.89), (0.62, 0.78)):
        y = cy - radius + int(2 * radius * frac)
        w = int(radius * half)
        draw.arc([cx - w, y - 14, cx + w, y + 14], 200, 340, fill=WHITE, width=2)
    # red crack across the globe
    crack = [(cx - 48, cy - 58), (cx - 20, cy - 28), (cx - 36, cy + 2),
             (cx - 8, cy + 30), (cx - 24, cy + 60)]
    draw.line(crack, fill=CRIMSON, width=5, joint="curve")
    draw.line(crack, fill=WHITE, width=1, joint="curve")


def draw_waves(draw, x, y, width, colour=OCEAN):
    for dx in range(0, width, 34):
        draw.arc([x + dx, y, x + dx + 32, y + 14], 180, 360, fill=colour, width=3)


def draw_warship(draw, x, y):
    """Warship under a blast: orange starburst, mast, hull, waves."""
    bx, by = x + 50, y + 20
    for angle in range(0, 360, 30):
        a = math.radians(angle)
        draw.line([bx, by, bx + 28 * math.cos(a), by + 28 * math.sin(a)],
                  fill=AMBER, width=6)
    draw.ellipse([bx - 12, by - 12, bx + 12, by + 12], fill=(255, 176, 32))
    draw.line([x + 50, y + 16, x + 50, y + 50], fill=INK, width=4)
    draw.polygon([(x + 50, y + 16), (x + 70, y + 22), (x + 50, y + 28)],
                 fill=CRIMSON)
    draw.polygon([(x + 4, y + 50), (x + 96, y + 50), (x + 86, y + 76),
                  (x + 14, y + 76)], fill=TEAL)
    draw.rectangle([x + 28, y + 38, x + 72, y + 50], fill=TEAL)
    draw_waves(draw, x + 2, y + 82, 96)


def draw_tanker(draw, x, y):
    """Oil tanker on fire with a spiked mine beside it."""
    mx, my = x + 16, y + 28
    for angle in range(0, 360, 45):
        a = math.radians(angle)
        draw.line([mx, my, mx + 19 * math.cos(a), my + 19 * math.sin(a)],
                  fill=INK, width=4)
    draw.ellipse([mx - 10, my - 10, mx + 10, my + 10], fill=INK)
    fx, fy = x + 64, y + 24
    draw.polygon([(fx - 11, fy + 12), (fx, fy - 18), (fx + 11, fy + 12)],
                 fill=AMBER)
    draw.polygon([(fx - 5, fy + 12), (fx, fy - 4), (fx + 5, fy + 12)],
                 fill=(255, 200, 60))
    draw.rectangle([x + 56, y + 32, x + 72, y + 48], fill=INK)
    draw.polygon([(x + 8, y + 48), (x + 96, y + 48), (x + 88, y + 64),
                  (x + 16, y + 64)], fill=INK)
    draw.polygon([(x + 16, y + 64), (x + 88, y + 64), (x + 82, y + 80),
                  (x + 22, y + 80)], fill=CRIMSON)
    draw_waves(draw, x + 2, y + 84, 96)


def draw_chip(draw, x, y):
    """Green microchip with gold pins and a red rising arrow."""
    for i in range(4):
        px = x + 18 + i * 20
        draw.rectangle([px, y + 2, px + 8, y + 13], fill=GOLD)
        draw.rectangle([px, y + 89, px + 8, y + 100], fill=GOLD)
        py = y + 18 + i * 20
        draw.rectangle([x + 2, py, x + 13, py + 8], fill=GOLD)
        draw.rectangle([x + 89, py, x + 100, py + 8], fill=GOLD)
    draw.rounded_rectangle([x + 14, y + 14, x + 88, y + 88], radius=6,
                           fill=(16, 140, 90), outline=(10, 100, 65), width=2)
    draw.rectangle([x + 36, y + 36, x + 66, y + 66], fill=(240, 240, 235),
                   outline=(180, 180, 170), width=2)
    draw.line([x + 6, y + 30, x + 26, y + 10], fill=CRIMSON, width=5)
    draw.polygon([(x + 26, y + 10), (x + 13, y + 10), (x + 26, y + 23)],
                 fill=CRIMSON)


def draw_factory(draw, x, y):
    """Factory with smoking chimney and a flame on the roof."""
    for (sx, sy, sr) in [(x + 80, y + 12, 9), (x + 90, y + 4, 11),
                         (x + 72, y + 22, 7)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(150, 150, 148))
    draw.polygon([(x + 74, y + 18), (x + 88, y + 18), (x + 90, y + 78),
                  (x + 72, y + 78)], fill=(88, 88, 86))
    fx, fy = x + 28, y + 34
    draw.polygon([(fx - 11, fy + 12), (fx, fy - 16), (fx + 11, fy + 12)],
                 fill=AMBER)
    draw.polygon([(fx - 5, fy + 12), (fx, fy - 4), (fx + 5, fy + 12)],
                 fill=(255, 200, 60))
    draw.polygon([(x + 4, y + 48), (x + 32, y + 30), (x + 72, y + 48),
                  (x + 72, y + 80), (x + 4, y + 80)], fill=(118, 118, 114))
    for wx in (14, 32, 50):
        draw.rectangle([x + wx, y + 58, x + wx + 10, y + 72], fill=(245, 176, 32))


# ------------------------------------------------------------------ poster
def build():
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    d = ImageDraw.Draw(img)

    # outer frame: double rule
    d.rectangle([16, 16, 1008, 1008], outline=INK, width=2)
    d.rectangle([22, 22, 1002, 1002], outline=RULE, width=1)

    # ---- masthead ------------------------------------------------------
    f_kick = load(SANS_B, 20)
    kick = "WORLD NEWS  •  ONE DAY, THE WHOLE WORLD"
    tw = d.textlength(kick, font=f_kick)
    d.text(((SIZE - tw) / 2, 36), kick, font=f_kick, fill=CRIMSON)
    f_title = load(SERIF, 62)
    title = "THE DAY IN BRIEF"
    tw = d.textlength(title, font=f_title)
    d.text(((SIZE - tw) / 2, 64), title, font=f_title, fill=INK)
    d.rectangle([30, 140, 994, 143], fill=INK)
    d.rectangle([30, 147, 994, 149], fill=INK)

    # ---- date band -----------------------------------------------------
    d.rectangle([30, 158, 994, 202], fill=TEAL)
    f_date = load(SANS_B, 30)
    date = "TUESDAY  —  24 NOVEMBER 2026"
    tw = d.textlength(date, font=f_date)
    d.text(((SIZE - tw) / 2, 166), date, font=f_date, fill=WHITE)

    # ---- lead story ----------------------------------------------------
    d.rounded_rectangle([30, 214, 994, 428], radius=10, fill=CARD,
                        outline=RULE, width=2)
    d.rectangle([30, 214, 42, 428], fill=CRIMSON_DARK)
    f_lkick = load(SANS_B, 22)
    d.text((58, 228), "CLIMATE SUMMIT  •  ANTALYA, TÜRKIYE",
           font=f_lkick, fill=CRIMSON)
    f_lhead = load(SERIF, 48)
    d.text((56, 256), "CLIMATE TALKS", font=f_lhead, fill=INK)
    d.text((56, 308), "COLLAPSE", font=f_lhead, fill=INK)
    f_lbody = load(SANS_R, 24)
    lead = ("UN talks fail after 50 hours of overtime — the first COP "
            "collapse since Copenhagen 2009. Deadlock: fossil fuels.")
    draw_lines(d, 58, 362, wrap_text(d, lead, f_lbody, 690), f_lbody, INK, 30)
    draw_globe(d, 872, 320, 74)

    # ---- story rows ----------------------------------------------------
    rows = [
        ("WAR  •  OFF LIBYA",
         "Ukraine sinks Russian warship",
         "Sea drones sank the corvette Merkury 2,400 km from the front line.",
         draw_warship),
        ("ENERGY  •  STRAIT OF HORMUZ",
         "Tankers ablaze after mine strikes",
         "Three tankers catch fire; Iran says it downed a US drone.",
         draw_tanker),
        ("MARKETS  •  NVIDIA",
         "Huang returns; shares jump 30%",
         "CEO reinstated 11 days after resigning; S&P 500 up 4.7%.",
         draw_chip),
        ("ASIA  •  JAKARTA",
         "24 killed in factory fire",
         "A blaze sweeps a food factory; dozens still missing.",
         draw_factory),
    ]
    f_rkick = load(SANS_B, 19)
    f_rhead = load(SERIF, 30)
    f_rbody = load(SANS_R, 21)
    y = 440
    for kicker, headline, body, icon_fn in rows:
        d.rounded_rectangle([30, y, 994, y + 100], radius=8, fill=CARD,
                            outline=RULE, width=2)
        icon_fn(d, 44, y + 2)
        tx = 158
        d.text((tx, y + 12), kicker, font=f_rkick, fill=CRIMSON)
        d.text((tx, y + 38), headline, font=f_rhead, fill=INK)
        draw_lines(d, tx, y + 72, wrap_text(d, body, f_rbody, 994 - tx - 18),
                   f_rbody, MUTED, 26)
        y += 104

    # ---- also today ----------------------------------------------------
    d.rounded_rectangle([30, 860, 994, 962], radius=10, fill=TEAL_SOFT,
                        outline=RULE, width=2)
    f_also = load(SANS_B, 22)
    d.text((48, 870), "ALSO TODAY", font=f_also, fill=TEAL)
    f_lab = load(SANS_B, 18)
    f_txt = load(SANS_R, 18)
    left_items = [
        ("GAZA", "Strikes kill four, incl. a UN aid worker."),
        ("TECH", "States sue Musk firms over Grok images."),
        ("USA", "Storms threaten Thanksgiving travel."),
    ]
    right_items = [
        ("BANGLADESH", "Hasina plans return on 16 December."),
        ("NATO", "Russia probed NATO airspace 25 times."),
        ("CUBA", "WHO chief visits amid a health crisis."),
    ]
    for col_x, items in ((48, left_items), (528, right_items)):
        yy = 900
        for label, rest in items:
            d.text((col_x, yy), label, font=f_lab, fill=CRIMSON)
            lx = col_x + d.textlength(label + "  ", font=f_lab)
            d.text((lx, yy), rest, font=f_txt, fill=INK)
            yy += 22

    # ---- footer --------------------------------------------------------
    f_foot = load(SANS_R, 17)
    foot = "Sources: CNN • Reuters • AP • Al Jazeera • WSJ • The Times  —  24 November 2026"
    tw = d.textlength(foot, font=f_foot)
    d.text(((SIZE - tw) / 2, 974), foot, font=f_foot, fill=MUTED)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG")
    with open(out, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    print(f"wrote {out}  {img.size}  sha256={digest}")


if __name__ == "__main__":
    build()
