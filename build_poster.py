#!/usr/bin/env python3
"""Build the entry image: a one-page newspaper front page summing up the
world news of Tuesday 24 November 2026.

Drawn from scratch with Pillow (flat vector-style pictograms + text) so the
poster is deterministic: same code, same bytes, every run. The finished
image is committed as entry.png; main.py only copies it to /output.

Stories verified against live reporting on 24 Nov 2026 (CNN, Reuters, AP,
Al Jazeera, The Wall Street Journal, The Times, The Conversation):
  1. COP31 climate talks in Antalya collapse with no deal (ended Sun 22 Nov
     after 50+ hours of overtime; first COP to fail since Copenhagen 2009;
     fossil-fuel wording blocked by petrostates).
  2. Ukraine says seven sea drones sank the Russian corvette Merkury at
     Benghazi, Libya, hit the cargo ship Angara and destroyed a Ka-27
     helicopter (announced Mon 23 Nov; 2,400 km from the front line).
  3. Three oil tankers catch fire after hitting mines in the Strait of
     Hormuz; Iran says it downed a US drone and vows to defy the US naval
     blockade (Al Jazeera live coverage, 23-24 Nov).
  4. Nvidia reinstates Jensen Huang as CEO 11 days after he resigned;
     shares jump ~30%, S&P 500 +4.7% (announced Mon 23 Nov).
  5. 24 killed in a fire at a food factory in Jakarta; dozens missing
     (front pages, 24 Nov).
  6. Also today: Gaza strikes kill four incl. a UN aid worker; storms
     threaten US Thanksgiving travel; 25 Russian airspace violations of
     NATO in 2026; US states sue Musk firms over Grok images; Sheikh
     Hasina plans a 16 Dec return to Bangladesh; WHO chief visits Cuba.
"""

from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1024, 1024
PAPER = (248, 244, 233)
INK = (22, 21, 18)
RED = (179, 39, 30)
NAVY = (20, 50, 74)
NAVY_LIGHT = (233, 238, 242)
GREY = (90, 86, 78)
CARD = (255, 253, 247)
BORDER = (206, 200, 184)
BLUE = (47, 111, 178)
GREEN = (63, 158, 77)
ORANGE = (232, 116, 30)
GOLD = (212, 160, 32)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def rrect(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


# ---------------------------------------------------------------- icons ---
def icon_globe(d, cx, cy, r):
    """Earth with a red crack: the climate summit that broke apart."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLUE, outline=NAVY, width=3)
    d.ellipse([cx - r * 0.62, cy - r * 0.55, cx - r * 0.05, cy + r * 0.05], fill=GREEN)
    d.ellipse([cx + r * 0.05, cy + r * 0.10, cx + r * 0.60, cy + r * 0.62], fill=GREEN)
    d.ellipse([cx - r * 0.15, cy - r * 0.85, cx + r * 0.45, cy - r * 0.30], fill=GREEN)
    hw = r * 0.937
    d.arc([cx - hw, cy + r * 0.17, cx + hw, cy + r * 0.53], 0, 180, fill=(255, 255, 255), width=2)
    d.arc([cx - hw, cy - r * 0.53, cx + hw, cy - r * 0.17], 180, 360, fill=(255, 255, 255), width=2)
    crack = [(cx - r * 0.75, cy - r * 0.85), (cx - r * 0.35, cy - r * 0.35),
             (cx - r * 0.55, cy + r * 0.05), (cx - r * 0.10, cy + r * 0.45),
             (cx - r * 0.30, cy + r * 0.80)]
    d.line(crack, fill=RED, width=6, joint="curve")
    d.line(crack, fill=(255, 255, 255), width=2, joint="curve")


def icon_warship(d, x, y, s):
    """Warship with an explosion starburst and waves."""
    ex, ey, er = x + s * 0.62, y + s * 0.30, s * 0.30
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rr = er if i % 2 == 0 else er * 0.45
        pts.append((ex + rr * math.cos(ang), ey + rr * math.sin(ang)))
    d.polygon(pts, fill=ORANGE)
    d.ellipse([ex - er * 0.35, ey - er * 0.35, ex + er * 0.35, ey + er * 0.35], fill=GOLD)
    d.polygon([(x + s * 0.05, y + s * 0.62), (x + s * 0.95, y + s * 0.62),
               (x + s * 0.82, y + s * 0.78), (x + s * 0.18, y + s * 0.78)], fill=NAVY)
    d.rectangle([x + s * 0.42, y + s * 0.44, x + s * 0.60, y + s * 0.62], fill=NAVY)
    d.line([x + s * 0.51, y + s * 0.44, x + s * 0.51, y + s * 0.22], fill=NAVY, width=4)
    d.polygon([(x + s * 0.51, y + s * 0.22), (x + s * 0.66, y + s * 0.28),
               (x + s * 0.51, y + s * 0.33)], fill=RED)
    for wy in (0.84, 0.92):
        d.arc([x + s * 0.02, y + s * wy, x + s * 0.48, y + s * (wy + 0.10)], 180, 360,
              fill=BLUE, width=3)
        d.arc([x + s * 0.52, y + s * wy, x + s * 0.98, y + s * (wy + 0.10)], 180, 360,
              fill=BLUE, width=3)


def icon_tanker_mine(d, x, y, s):
    """Oil tanker, naval mine and flame on the water."""
    fx, fy = x + s * 0.74, y + s * 0.30
    d.polygon([(fx, fy - s * 0.22), (fx + s * 0.13, fy + s * 0.02),
               (fx + s * 0.05, fy + s * 0.12), (fx - s * 0.05, fy + s * 0.12),
               (fx - s * 0.13, fy + s * 0.02)], fill=ORANGE)
    d.polygon([(fx, fy - s * 0.10), (fx + s * 0.06, fy + s * 0.05),
               (fx - s * 0.06, fy + s * 0.05)], fill=GOLD)
    mx, my, mr = x + s * 0.24, y + s * 0.42, s * 0.13
    for i in range(8):
        ang = math.pi * i / 4
        d.line([mx + mr * 0.8 * math.cos(ang), my + mr * 0.8 * math.sin(ang),
                mx + mr * 1.5 * math.cos(ang), my + mr * 1.5 * math.sin(ang)],
               fill=INK, width=4)
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=INK)
    d.ellipse([mx - mr * 0.4, my - mr * 0.55, mx + mr * 0.1, my - mr * 0.05],
              fill=(120, 120, 120))
    d.polygon([(x + s * 0.08, y + s * 0.62), (x + s * 0.92, y + s * 0.62),
               (x + s * 0.86, y + s * 0.78), (x + s * 0.14, y + s * 0.78)], fill=(40, 40, 40))
    d.rectangle([x + s * 0.08, y + s * 0.58, x + s * 0.92, y + s * 0.63], fill=RED)
    d.rectangle([x + s * 0.68, y + s * 0.44, x + s * 0.82, y + s * 0.58], fill=(40, 40, 40))
    d.line([x + s * 0.75, y + s * 0.44, x + s * 0.75, y + s * 0.30], fill=(40, 40, 40), width=4)
    d.arc([x + s * 0.02, y + s * 0.84, x + s * 0.48, y + s * 0.94], 180, 360, fill=BLUE, width=3)
    d.arc([x + s * 0.52, y + s * 0.84, x + s * 0.98, y + s * 0.94], 180, 360, fill=BLUE, width=3)


def icon_chip(d, x, y, s):
    """Green AI chip with a rising red arrow."""
    d.rounded_rectangle([x + s * 0.20, y + s * 0.20, x + s * 0.80, y + s * 0.80],
                        radius=int(s * 0.06), fill=(22, 163, 74), outline=NAVY, width=3)
    d.rounded_rectangle([x + s * 0.38, y + s * 0.38, x + s * 0.62, y + s * 0.62],
                        radius=int(s * 0.03), fill=(255, 255, 255))
    for i in range(3):
        off = s * (0.32 + i * 0.18)
        d.rectangle([x + off, y + s * 0.10, x + off + s * 0.06, y + s * 0.20], fill=GOLD)
        d.rectangle([x + off, y + s * 0.80, x + off + s * 0.06, y + s * 0.90], fill=GOLD)
        d.rectangle([x + s * 0.10, y + off, x + s * 0.20, y + off + s * 0.06], fill=GOLD)
        d.rectangle([x + s * 0.80, y + off, x + s * 0.90, y + off + s * 0.06], fill=GOLD)
    d.line([(x + s * 0.06, y + s * 0.32), (x + s * 0.28, y + s * 0.10)], fill=RED, width=5)
    d.polygon([(x + s * 0.28, y + s * 0.06), (x + s * 0.38, y + s * 0.16),
               (x + s * 0.24, y + s * 0.18)], fill=RED)


def icon_factory(d, x, y, s):
    """Factory with flame and smoke."""
    d.ellipse([x + s * 0.62, y + s * 0.02, x + s * 0.78, y + s * 0.18], fill=(150, 150, 150))
    d.ellipse([x + s * 0.72, y - s * 0.06, x + s * 0.90, y + s * 0.12], fill=(170, 170, 170))
    d.rectangle([x + s * 0.66, y + s * 0.10, x + s * 0.78, y + s * 0.55], fill=(90, 86, 78))
    d.polygon([(x + s * 0.06, y + s * 0.78), (x + s * 0.06, y + s * 0.55),
               (x + s * 0.22, y + s * 0.42), (x + s * 0.38, y + s * 0.55),
               (x + s * 0.54, y + s * 0.42), (x + s * 0.66, y + s * 0.55),
               (x + s * 0.66, y + s * 0.78)], fill=(120, 116, 108))
    for wx in (0.14, 0.30, 0.46):
        d.rectangle([x + s * wx, y + s * 0.60, x + s * (wx + 0.08), y + s * 0.72],
                    fill=GOLD)
    fx, fy = x + s * 0.30, y + s * 0.40
    d.polygon([(fx, fy - s * 0.18), (fx + s * 0.11, fy + s * 0.02),
               (fx + s * 0.04, fy + s * 0.10), (fx - s * 0.04, fy + s * 0.10),
               (fx - s * 0.11, fy + s * 0.02)], fill=ORANGE)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 26  # margin

    # ---- masthead ----
    d.rectangle([M, M, W - M, M + 4], fill=INK)
    f_mast = font(SERIF, 60)
    title = "THE WORLD IN ONE DAY"
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, M + 12), title, font=f_mast, fill=INK)
    d.rectangle([M, M + 86, W - M, M + 90], fill=INK)

    # ---- date band ----
    d.rectangle([M, M + 98, W - M, M + 142], fill=NAVY)
    f_date = font(SANS_B, 36)
    date = "TUESDAY  \u2022  24 NOVEMBER 2026"
    dw = d.textlength(date, font=f_date)
    d.text(((W - dw) / 2, M + 106), date, font=f_date, fill=(255, 255, 255))

    y = M + 152  # content top = 178

    # ---- lead story: COP31 ----
    lead_h = 240
    rrect(d, [M, y, W - M, y + lead_h], 10, fill=CARD, outline=BORDER, width=2)
    d.rectangle([M, y + 10, M + 8, y + lead_h - 10], fill=RED)
    tx = M + 26
    f_kick = font(SANS_B, 23)
    d.text((tx, y + 12), "CLIMATE  \u2022  ANTALYA, T\u00dcRKIYE", font=f_kick, fill=RED)
    f_h1 = font(SERIF, 44)
    lines = wrap(d, "CLIMATE SUMMIT COLLAPSES", f_h1, 700)
    ly = draw_lines(d, lines, tx, y + 44, f_h1, INK, 50)
    f_dek = font(SANS, 26)
    dek = ("UN talks fail after 50 hours of overtime \u2014 the first COP to collapse "
           "since Copenhagen 2009. The deadlock: fossil fuels.")
    draw_lines(d, wrap(d, dek, f_dek, 700), tx, ly + 8, f_dek, (50, 48, 44), 31)
    icon_globe(d, W - M - 104, y + lead_h // 2 + 4, 76)

    # ---- story cards (icon left, text right) ----
    f_kick2 = font(SANS_B, 20)
    f_h2 = font(SERIF, 28)
    f_dek2 = font(SANS, 23)

    def card(x, yy, w, h, kicker, headline, dek_text, icon_fn):
        rrect(d, [x, yy, x + w, yy + h], 10, fill=CARD, outline=BORDER, width=2)
        icon_fn(d, x + 12, yy + (h - 96) // 2, 96)
        tx2 = x + 118
        tw2 = w - 118 - 14
        d.text((tx2, yy + 12), kicker, font=f_kick2, fill=RED)
        hl = wrap(d, headline, f_h2, tw2)
        hy = draw_lines(d, hl, tx2, yy + 40, f_h2, INK, 34)
        draw_lines(d, wrap(d, dek_text, f_dek2, tw2), tx2, hy + 4, f_dek2,
                   (50, 48, 44), 28)

    row_y = y + lead_h + 8
    row_h = 208
    cw = (W - 2 * M - 10) // 2
    card(M, row_y, cw, row_h, "WAR  \u2022  LIBYA",
         "UKRAINE SINKS RUSSIAN WARSHIP",
         "Sea drones sank the corvette Merkury off Libya \u2014 2,400 km from "
         "the front line.",
         icon_warship)
    card(M + cw + 10, row_y, cw, row_h, "MIDDLE EAST  \u2022  HORMUZ",
         "TANKERS ABLAZE IN HORMUZ",
         "Three tankers catch fire on mines; Iran says it downed a US drone.",
         icon_tanker_mine)

    row_y2 = row_y + row_h + 8
    card(M, row_y2, cw, row_h, "TECH  \u2022  MARKETS",
         "HUANG IS BACK AT NVIDIA",
         "CEO reinstated 11 days after resigning; shares jump ~30%, "
         "S&P 500 up 4.7%.",
         icon_chip)
    card(M + cw + 10, row_y2, cw, row_h, "ASIA  \u2022  JAKARTA",
         "24 KILLED IN FACTORY FIRE",
         "A blaze sweeps a food factory in Jakarta; dozens still missing "
         "in the ruins.",
         icon_factory)

    # ---- also today ----
    ay = row_y2 + row_h + 8
    ah = 136
    rrect(d, [M, ay, W - M, ay + ah], 10, fill=NAVY_LIGHT, outline=BORDER, width=2)
    d.text((M + 18, ay + 8), "ALSO TODAY", font=font(SANS_B, 24), fill=NAVY)
    items = [
        ("GAZA", "Strikes kill four, incl. a UN aid worker."),
        ("USA", "Storms threaten Thanksgiving travel."),
        ("NATO", "Russia probed NATO airspace 25 times."),
        ("TECH", "States sue Musk firms over Grok images."),
        ("BANGLADESH", "Hasina plans return 16 Dec."),
        ("CUBA", "WHO chief visits amid a health crisis."),
    ]
    f_item = font(SANS, 22)
    f_item_b = font(SANS_B, 22)
    col_w = (W - 2 * M - 36 - 28) // 3
    def flow_wrap(text, first_w, rest_w, fnt):
        """Wrap text where the first line is narrower (tag sits beside it)."""
        words = text.split()
        lines, cur, cap = [], "", first_w
        for w in words:
            trial = (cur + " " + w).strip()
            if d.textlength(trial, font=fnt) <= cap:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur, cap = w, rest_w
        if cur:
            lines.append(cur)
        return lines

    for i, (tag, text) in enumerate(items):
        col, row = i % 3, i // 3
        ix0 = M + 18 + col * (col_w + 14)
        iy0 = ay + 38 + row * 48
        d.text((ix0, iy0), tag + " \u2014 ", font=f_item_b, fill=RED)
        tag_w = d.textlength(tag + " \u2014 ", font=f_item_b)
        rest = flow_wrap(text, col_w - tag_w, col_w, f_item)
        if rest:
            d.text((ix0 + tag_w, iy0), rest[0], font=f_item, fill=INK)
            if len(rest) > 1:
                d.text((ix0, iy0 + 24), rest[1], font=f_item, fill=INK)

    # ---- footer ----
    f_foot = font(SANS, 19)
    foot = ("Sources: CNN \u00b7 Reuters \u00b7 AP \u00b7 Al Jazeera \u00b7 WSJ \u00b7 The Times"
            "  \u2014  24 November 2026")
    fw = d.textlength(foot, font=f_foot)
    d.text(((W - fw) / 2, ay + ah + 8), foot, font=f_foot, fill=GREY)

    return img


if __name__ == "__main__":
    im = build()
    im.save("entry.png", format="PNG", optimize=True)
    print("saved entry.png", im.size)
