#!/usr/bin/env python3
"""The Day in Brief — a one-page broadsheet poster for 24 November 2026.

A single 1024x1024 front page, drawn with Pillow: masthead, date bar,
the lead climate story with a cracked globe, four story rows, an
"Also today" box and a source line. Everything is laid out by hand,
in the style of a printed newspaper front page.

Run it and it writes entry.png next to this file.
"""

import math

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Page and palette
# ---------------------------------------------------------------------------

SIZE = 1024
MARGIN = 30
RIGHT = SIZE - MARGIN  # right edge of the content column

PAPER = (248, 244, 233)      # warm newsprint
BOX = (255, 252, 244)        # story boxes, a touch lighter than the page
INK = (24, 24, 22)           # headlines and body text
RED = (178, 32, 32)          # kickers and the crack in the globe
DARK_RED = (140, 20, 20)     # the lead story's side bar
TEAL = (15, 61, 62)          # date bar and the globe's outline
BORDER = (190, 183, 164)     # hairlines and box edges
GREY = (105, 100, 88)        # the source line
GLOBE_BLUE = (43, 102, 168)
GLOBE_GREEN = (52, 148, 88)
CHIP_GREEN = (16, 140, 90)
CHIP_EDGE = (0, 96, 64)       # the dark edge round the chip
BRONZE = (208, 160, 32)       # the chip's pins, a bronze gold
BUILDING = (112, 112, 112)    # the factory walls
CHIMNEY = (80, 80, 80)        # the factory chimney
SMOKE = (176, 176, 160)       # the smoke above the chimney
GOLD = (245, 176, 32)
ORANGE = (255, 140, 0)
ALSO_BG = (226, 236, 234)    # pale blue-green for the Also Today box

# ---------------------------------------------------------------------------
# Type
# ---------------------------------------------------------------------------
# One serif for every headline, one sans for the body text, and the wider
# DejaVu face for the big red kickers. The serif sizes are the ones that
# set the headlines to the widths the layout wants.

FONTS = {
    "serif": "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "sans": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "sans-bold": "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    # The wider DejaVu face, for the two big red kickers up top.
    "display": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}


def font(kind, size):
    """One of the poster's four faces, at the given size."""
    return ImageFont.truetype(FONTS[kind], size)


TITLE_FONT = font("serif", 62)
LEAD_HEAD_FONT = font("serif", 48)
ROW_HEAD_FONT = font("serif", 30)
KICKER_FONT = font("display", 18)
LEAD_KICKER_FONT = font("display", 20)
ROW_KICKER_FONT = font("display", 18)
DATE_FONT = font("sans-bold", 31)
LEAD_DECK_FONT = font("sans", 24)
ROW_DECK_FONT = font("sans", 21)
ALSO_HEAD_FONT = font("sans-bold", 22)
ALSO_LABEL_FONT = font("sans-bold", 18)
ALSO_TEXT_FONT = font("sans", 18)
FOOTER_FONT = font("sans", 17)

# ---------------------------------------------------------------------------
# The day's stories
# ---------------------------------------------------------------------------

LEAD = {
    "kicker": "CLIMATE SUMMIT • ANTALYA, TÜRKIYE",
    "headline": ["CLIMATE TALKS", "COLLAPSE"],
    "deck": (
        "UN talks fail after 50 hours of overtime — the first COP collapse "
        "since Copenhagen 2009. Deadlock: fossil fuels."
    ),
}

STORIES = [
    {
        "kicker": "WAR • OFF LIBYA",
        "headline": "Ukraine sinks Russian warship",
        "deck": "Sea drones sank the corvette Merkury 2,400 km from the front line.",
        "icon": "warship",
    },
    {
        "kicker": "ENERGY • STRAIT OF HORMUZ",
        "headline": "Tankers ablaze after mine strikes",
        "deck": "Three tankers catch fire; Iran says it downed a US drone.",
        "icon": "tanker",
    },
    {
        "kicker": "MARKETS • NVIDIA",
        "headline": "Huang returns; shares jump 30%",
        "deck": "CEO reinstated 11 days after resigning; S&P 500 up 4.7%.",
        "icon": "chip",
    },
    {
        "kicker": "ASIA • JAKARTA",
        "headline": "24 killed in factory fire",
        "deck": "A blaze sweeps a food factory; dozens still missing.",
        "icon": "factory",
    },
]

ALSO_LEFT = [
    ("GAZA", "Strikes kill four, incl. a UN aid worker."),
    ("TECH", "States sue Musk firms over Grok images."),
    ("USA", "Storms threaten Thanksgiving travel."),
]

ALSO_RIGHT = [
    ("BANGLADESH", "Hasina plans return on 16 December."),
    ("NATO", "Russia probed NATO airspace 25 times."),
    ("CUBA", "WHO chief visits amid a health crisis."),
]

FOOTER = "Sources: CNN • Reuters • AP • Al Jazeera • WSJ • The Times — 24 November 2026"

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

MASTHEAD_KICKER_TOP = 37
TITLE_TOP = 64
RULE_TOP_Y = 140
RULE_BOTTOM_Y = 147
DATE_BAR = (MARGIN, 158, RIGHT, 204)
LEAD_BOX = (MARGIN, 214, RIGHT, 430)
LEAD_TEXT_X = 56
LEAD_KICKER_X = 57
LEAD_DECK_X = 58
LEAD_DECK_WIDTH = 700
ROW_TOPS = (440, 544, 648, 752)
ROW_HEIGHT = 102
ROW_KICKER_DY = 13
ROW_HEADLINE_DY = 38
ROW_DECK_DY = 72
ROW_HEADLINE_X = 158
ROW_DECK_X = 158  # the deck's first letter sits a pixel left of the kicker's
ICON_CENTRE_X = 93
ALSO_BOX = (MARGIN, 860, RIGHT, 962)
ALSO_HEAD_TOP = 870
ALSO_HEAD_X = 48
ALSO_ITEM_TOPS = (900, 922, 944)
ALSO_LEFT_X = 48
ALSO_RIGHT_X = 528
FOOTER_TOP = 974

GLOBE_CENTRE = (872, 320)
GLOBE_RADIUS = 70


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def wrap(draw, text, typeface, width):
    """Split text into lines that fit width, on word boundaries."""
    words = text.split()
    lines, line = [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=typeface) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def centred(draw, top, text, typeface, fill, cx=SIZE // 2):
    """Draw text centred on cx, with top as its top edge."""
    width = draw.textlength(text, font=typeface)
    draw.text((cx - width / 2, top), text, font=typeface, fill=fill)


def box(draw, rect, fill, outline=BORDER, width=2):
    """A filled rectangle with a two-pixel edge, as the old broadsheets had."""
    draw.rectangle(rect, fill=fill, outline=outline, width=width)


# ---------------------------------------------------------------------------
# Icons
# ---------------------------------------------------------------------------
# Each icon lives in the 114-pixel strip at the left of its row, centred
# on ICON_CENTRE_X. The row's top edge is passed in so the same drawing
# code works for any row.

def draw_warship(draw, top):
    """A warship under a rising sun."""
    cx = ICON_CENTRE_X
    # The sun, with rays all round it. The rays reach further sideways
    # than up and down, so the sun fits its row.
    sun = (cx, top + 22)
    for step in range(12):
        angle = math.radians(step * 30)
        reach = 22 + 6 * abs(math.cos(angle))
        inner = (sun[0] + 13 * math.cos(angle), sun[1] + 13 * math.sin(angle))
        outer = (sun[0] + reach * math.cos(angle), sun[1] + reach * math.sin(angle))
        draw.line([inner, outer], fill=ORANGE, width=6)
    draw.ellipse(
        [sun[0] - 12, sun[1] - 12, sun[0] + 12, sun[1] + 12], fill=GOLD
    )
    # Mast and flag, riding on the sun.
    draw.line([(cx, top + 18), (cx, top + 42)], fill=INK, width=3)
    draw.polygon([(cx, top + 17), (cx + 18, top + 23), (cx, top + 29)], fill=RED)
    # Superstructure, then the hull, wider at the top than at the waterline.
    draw.rectangle([72, top + 40, 116, top + 54], fill=TEAL)
    draw.polygon(
        [(48, top + 54), (140, top + 54), (130, top + 78), (58, top + 78)],
        fill=TEAL,
    )
    # Three wave arcs under the hull.
    for x0 in (47, 81, 115):
        draw.arc([x0, top + 84, x0 + 30, top + 98], 180, 360, fill=GLOBE_BLUE, width=2)


def draw_tanker(draw, top):
    """A tanker under a mine and a flame."""
    # The mine, top left, spikes and all. Its spikes reach further
    # sideways than up and down, the same shape as the sun's rays.
    mine = (60, top + 24)
    for step in range(8):
        angle = math.radians(step * 45)
        reach = 13 + 6 * abs(math.cos(angle))
        inner = (mine[0] + 12 * math.cos(angle), mine[1] + 12 * math.sin(angle))
        outer = (mine[0] + reach * math.cos(angle), mine[1] + reach * math.sin(angle))
        draw.line([inner, outer], fill=INK, width=4)
    draw.ellipse(
        [mine[0] - 12, mine[1] - 12, mine[0] + 12, mine[1] + 12], fill=INK
    )
    # The flame, a teardrop with a yellow heart, over the deck.
    draw.polygon(
        [(78, top + 8), (89, top + 26), (86, top + 38), (70, top + 38), (67, top + 26)],
        fill=ORANGE,
    )
    draw.polygon(
        [(78, top + 22), (81, top + 28), (78, top + 33), (75, top + 28)],
        fill=GOLD,
    )
    # The bridge, its bow edge bulging out to the left.
    draw.polygon(
        [(50, top + 36), (116, top + 36), (116, top + 50), (59, top + 50), (46, top + 42)],
        fill=INK,
    )
    # Black hull above the waterline, red hull below it.
    draw.polygon(
        [(53, top + 50), (139, top + 50), (132, top + 66), (60, top + 66)],
        fill=INK,
    )
    draw.polygon(
        [(60, top + 66), (132, top + 66), (126, top + 82), (66, top + 82)],
        fill=RED,
    )
    # Three wave arcs under the hull.
    for x0 in (47, 81, 115):
        draw.arc([x0, top + 84, x0 + 30, top + 98], 180, 360, fill=GLOBE_BLUE, width=2)


def draw_chip(draw, top):
    """A microchip, pins out, with a rising arrow."""
    # Bronze pins on all four sides: five along the top and bottom,
    # four down each side.
    for x in (62, 78, 94, 110, 123):
        draw.rectangle([x, top + 4, x + 7, top + 17], fill=BRONZE)
        draw.rectangle([x, top + 89, x + 7, top + 102], fill=BRONZE)
    for y in (20, 40, 60, 80):
        draw.rectangle([46, top + y, 58, top + y + 8], fill=BRONZE)
        draw.rectangle([132, top + y, 144, top + y + 8], fill=BRONZE)
    # The green die, with a dark edge round it.
    draw.rectangle([58, top + 16, 132, top + 90], fill=CHIP_EDGE)
    draw.rectangle([60, top + 18, 130, top + 88], fill=CHIP_GREEN)
    # A small red arrow climbing out of the top-left corner.
    draw.line([(51, top + 31), (69, top + 13)], fill=RED, width=5)
    draw.line([(69, top + 13), (59, top + 13)], fill=RED, width=5)
    draw.line([(69, top + 13), (69, top + 23)], fill=RED, width=5)


def draw_factory(draw, top):
    """A factory with a tall chimney, smoke and a flame on the roof."""
    # Smoke drifting up from the chimney.
    for centre, radius in (((126, top + 8), 7), ((137, top + 13), 8), ((121, top + 14), 6)):
        draw.ellipse(
            [
                centre[0] - radius,
                centre[1] - radius,
                centre[0] + radius,
                centre[1] + radius,
            ],
            fill=SMOKE,
        )
    # The shed itself: a roof that slopes down to the left in two
    # runs, and a tall chimney rising from its peak.
    draw.polygon(
        [
            (48, top + 50),
            (76, top + 32),
            (118, top + 20),
            (134, top + 32),
            (134, top + 82),
            (48, top + 82),
        ],
        fill=BUILDING,
    )
    draw.rectangle([118, top + 20, 132, top + 80], fill=CHIMNEY)
    # A flame on the roof's left slope.
    draw.polygon(
        [(71, top + 20), (77, top + 30), (74, top + 38), (68, top + 38), (65, top + 30)],
        fill=ORANGE,
    )
    # Three lit windows along the wall.
    for x0 in (58, 75, 92):
        draw.rectangle([x0, top + 60, x0 + 12, top + 74], fill=GOLD)


ICONS = {
    "warship": draw_warship,
    "tanker": draw_tanker,
    "chip": draw_chip,
    "factory": draw_factory,
}


def draw_globe(draw):
    """The lead story's cracked globe."""
    cx, cy = GLOBE_CENTRE
    r = GLOBE_RADIUS
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GLOBE_BLUE, outline=TEAL, width=3)
    # Land, four rough pieces, placed where the old globe has them.
    draw.polygon([(844, 268), (866, 285), (858, 312), (832, 310), (820, 290)], fill=GLOBE_GREEN)
    draw.polygon([(910, 268), (924, 288), (920, 305), (895, 308), (880, 282)], fill=GLOBE_GREEN)
    draw.polygon([(862, 328), (876, 348), (866, 368), (832, 362), (826, 340)], fill=GLOBE_GREEN)
    draw.polygon([(898, 342), (922, 352), (918, 376), (892, 368)], fill=GLOBE_GREEN)
    # Two latitude lines, nearly straight, sagging gently to the right.
    draw.line(
        [(806, 304), (850, 295), (872, 298), (910, 301), (930, 306)],
        fill="white",
        width=2,
        joint="curve",
    )
    draw.line(
        [(806, 330), (850, 324), (872, 323), (910, 327), (930, 330)],
        fill="white",
        width=2,
        joint="curve",
    )
    # The crack: a white edge, then the red split itself.
    crack = [(848, 252), (836, 275), (850, 295), (839, 320), (849, 335), (861, 355), (850, 375), (855, 388)]
    draw.line([(x - 3, y - 1) for x, y in crack], fill="white", width=2)
    draw.line(crack, fill=RED, width=3)


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

def draw_frame(draw):
    """The page's double frame: a dark outer line, a hairline inside it."""
    draw.rectangle([16, 16, SIZE - 16, SIZE - 16], outline=INK, width=2)
    draw.rectangle([22, 22, SIZE - 22, SIZE - 22], outline=BORDER, width=1)


def draw_masthead(draw):
    """Kicker, title and the double rule underneath."""
    centred(draw, MASTHEAD_KICKER_TOP, "WORLD NEWS • ONE DAY, THE WHOLE WORLD", KICKER_FONT, RED)
    centred(draw, TITLE_TOP, "THE DAY IN BRIEF", TITLE_FONT, INK)
    draw.line([(MARGIN, RULE_TOP_Y), (RIGHT, RULE_TOP_Y)], fill=INK, width=2)
    draw.line([(MARGIN, RULE_BOTTOM_Y), (RIGHT, RULE_BOTTOM_Y)], fill=INK, width=1)


def draw_date_bar(draw):
    """The dark teal bar with the day's date."""
    draw.rectangle(DATE_BAR, fill=TEAL)
    centred(draw, 165, "TUESDAY — 24 NOVEMBER 2026", DATE_FONT, "white")


def draw_lead(draw):
    """The big story: red side bar, two-line headline, globe on the right."""
    box(draw, LEAD_BOX, fill=BOX)
    draw.rectangle([LEAD_BOX[0], LEAD_BOX[1], 42, LEAD_BOX[3]], fill=DARK_RED)
    draw.text((LEAD_KICKER_X, 229), LEAD["kicker"], font=LEAD_KICKER_FONT, fill=RED)
    draw.text((LEAD_TEXT_X, 256), LEAD["headline"][0], font=LEAD_HEAD_FONT, fill=INK)
    draw.text((LEAD_TEXT_X, 308), LEAD["headline"][1], font=LEAD_HEAD_FONT, fill=INK)
    deck = wrap(draw, LEAD["deck"], LEAD_DECK_FONT, LEAD_DECK_WIDTH)
    for step, line in enumerate(deck):
        draw.text(
            (LEAD_DECK_X, 362 + step * 30), line, font=LEAD_DECK_FONT, fill=INK
        )
    draw_globe(draw)


def draw_story_row(draw, top, story):
    """One of the four rows: kicker, headline, deck, icon on the left."""
    box(draw, (MARGIN, top, RIGHT, top + ROW_HEIGHT), fill=BOX)
    draw.text((ROW_HEADLINE_X, top + ROW_KICKER_DY), story["kicker"], font=ROW_KICKER_FONT, fill=RED)
    draw.text(
        (ROW_HEADLINE_X, top + ROW_HEADLINE_DY),
        story["headline"],
        font=ROW_HEAD_FONT,
        fill=INK,
    )
    draw.text(
        (ROW_DECK_X, top + ROW_DECK_DY), story["deck"], font=ROW_DECK_FONT, fill=GREY
    )
    ICONS[story["icon"]](draw, top)


def draw_also_today(draw):
    """The round-up box: three short items a side."""
    box(draw, ALSO_BOX, fill=ALSO_BG)
    draw.text((ALSO_HEAD_X, ALSO_HEAD_TOP), "ALSO TODAY", font=ALSO_HEAD_FONT, fill=TEAL)
    for column, items in ((ALSO_LEFT_X, ALSO_LEFT), (ALSO_RIGHT_X, ALSO_RIGHT)):
        for top, (label, text) in zip(ALSO_ITEM_TOPS, items):
            draw.text((column, top), label, font=ALSO_LABEL_FONT, fill=RED)
            label_width = draw.textlength(label, font=ALSO_LABEL_FONT)
            draw.text(
                (column + label_width + 8, top), text, font=ALSO_TEXT_FONT, fill=INK
            )


def draw_footer(draw):
    """The source line under the Also Today box."""
    centred(draw, FOOTER_TOP, FOOTER, FOOTER_FONT, GREY)


# ---------------------------------------------------------------------------
# Build it
# ---------------------------------------------------------------------------

def build_poster():
    """Draw the whole front page and hand it back."""
    image = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(image)
    draw_frame(draw)
    draw_masthead(draw)
    draw_date_bar(draw)
    draw_lead(draw)
    for top, story in zip(ROW_TOPS, STORIES):
        draw_story_row(draw, top, story)
    draw_also_today(draw)
    draw_footer(draw)
    return image


if __name__ == "__main__":
    poster = build_poster()
    poster.save("entry.png")
    print("Wrote entry.png", poster.size)
