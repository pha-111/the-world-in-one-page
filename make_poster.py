#!/usr/bin/env python3
"""Draw entry.png: the world news of Tuesday 24 November 2026 on one page.

A classic broadsheet front page rendered with PIL and the DejaVu fonts.
The layout is fully deterministic -- fixed text, fixed geometry, no clock,
no randomness -- so running this script twice produces byte-identical
output. It writes entry.png next to this file.

    python3 make_poster.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# Page geometry and palette
# --------------------------------------------------------------------------

W = H = 1024
PAPER = (247, 242, 231)        # off-white newsprint
INK = (20, 17, 13)             # near-black ink
RED = (142, 31, 31)            # deep red accent
SOFT = (58, 52, 42)            # softer ink for summaries
FAINT = (150, 140, 118)        # hairlines / distant skyline
MID = (104, 95, 78)            # mid tone for skyline depth

FRAME_OUT = 18                 # outer frame inset
FRAME_IN = 27                  # inner frame inset
MX = 48                        # text margin
CW = W - 2 * MX                # text column width (928)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def serif(size: int) -> ImageFont.FreeTypeFont:
    return font("DejaVuSerif.ttf", size)


def serif_b(size: int) -> ImageFont.FreeTypeFont:
    return font("DejaVuSerif-Bold.ttf", size)


def sans(size: int) -> ImageFont.FreeTypeFont:
    return font("DejaVuSans.ttf", size)


def sans_b(size: int) -> ImageFont.FreeTypeFont:
    return font("DejaVuSans-Bold.ttf", size)


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------

def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_w: int):
    """Greedy word wrap; returns the list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def tracked_width(draw, text, fnt, tracking):
    return sum(draw.textlength(ch, font=fnt) for ch in text) + tracking * (len(text) - 1)


def draw_tracked(draw, cx, y, text, fnt, fill, tracking):
    """Draw text centred on cx with extra letter spacing."""
    x = cx - tracked_width(draw, text, fnt, tracking) / 2
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking


def draw_block(draw, x, y, lines, fnt, fill, line_h):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def fit_size(draw, text, maker, start, min_size, max_w, tracking=0):
    """Largest font size (<= start) whose tracked width fits max_w."""
    size = start
    while size > min_size:
        fnt = maker(size)
        if tracked_width(draw, text, fnt, tracking) <= max_w:
            return fnt
        size -= 1
    return maker(min_size)


# --------------------------------------------------------------------------
# The day's news (Tuesday 24 November 2026)
# --------------------------------------------------------------------------

MASTHEAD = "THE WORLD IN ONE PAGE"
DATELINE = "Tuesday, 24 November 2026"

LEAD_LABEL = "LEAD STORY — MIDDLE EAST"
LEAD_HEAD = "Houthi Strike Hits Riyadh's Tallest Tower — Again"
LEAD_SUB = (
    "The Saudi capital's landmark skyscraper is struck for the second time "
    "in a week; 11 people injured as the coalition fighting the Houthis "
    "denounces a terrorist attack."
)
LEAD_CAPTION = "Riyadh's tallest tower, struck a second time in a week."

STORIES = [
    (
        "UKRAINE TALKS",
        "Zelenskyy Urges Four-Way Peace Talks",
        "Kyiv says it is ready to meet Russia, the US and Europe. Ukraine "
        "says it struck a Russian vessel in the Gulf of Finland, and new "
        "analysis of leaked data puts Russian war losses above 700,000.",
    ),
    (
        "HORMUZ",
        "Four Tankers Catch Fire After Hitting Mines in the Strait of Hormuz",
        "Tehran also rules out talks with Washington until its seven "
        "conditions are met.",
    ),
    (
        "WORLD COURT",
        "14 Nations Affirm ICJ Genocide Ruling Against Myanmar",
        "Britain, Spain, Canada, Australia and ten other countries back "
        "the court's Rohingya ruling; London adds sanctions on Myanmar's "
        "military leaders.",
    ),
    (
        "ARTIFICIAL INTELLIGENCE",
        "UN Chief Wants Global AI Guardrails Within a Year",
        "António Guterres urges member states to build a multilateral "
        "framework to manage the risks of artificial intelligence.",
    ),
    (
        "CHIP GIANT",
        "Nvidia Rebounds as Jensen Huang Returns",
        "Huang is reinstated as chief executive after President Trump's "
        "intervention; the chip maker regains about $900 billion in "
        "market value as markets rally.",
    ),
    (
        "GAZA",
        "Israeli Strike Kills Hamas Security Chief in Gaza City",
        "The strike lands despite a ceasefire in place since last year; "
        "Oxfam describes Gaza as a 'toxic land'.",
    ),
    (
        "HEALTH",
        "Pennsylvania Measles Death Toll Reaches Nine",
        "The outbreak now spans 46 counties across the state.",
    ),
    (
        "SPACE & ASIA",
        "China Opens Tiangong Station to First Foreign Astronaut",
        "Pakistan's Zeeshan Ali will fly on the Shenzhou-24 mission. "
        "A 5.6-magnitude earthquake strikes Nepal near the Chinese border.",
    ),
]

MARKETS = (
    "MARKETS · 24 NOV CLOSE — S&P 500 7,237 · NASDAQ 24,090 · DAX 25,337 · "
    "FTSE 100 10,481 · NIKKEI 58,645 · GOLD $3,620 · BRENT $86.7"
)

BRIEF = (
    "Car bomb destroys buildings in Villavicencio, Colombia · Global "
    "landmine casualties hit a five-year high of 7,000 · Trump awards "
    "Rudy Giuliani the Medal of Freedom · COP31 deadlock renews calls "
    "to reform UN climate summits · Two arrested after break-in at "
    "Prince William's Norfolk home"
)

FOOTER = "The world of Tuesday 24 November 2026 — summed up on one page."


# --------------------------------------------------------------------------
# The tower motif beside the lead story
# --------------------------------------------------------------------------

def draw_motif(draw, x0, y0, x1, y1):
    """A Riyadh skyline in silhouette: low blocks, one tall tower with
    its great arch, and a red burst where the strike landed. The caption
    sits inside the box, under the ground line."""
    ground = y1 - 46
    cx = (x0 + x1) // 2

    # Blocks on both sides of the tower, all standing on the ground.
    blocks = [
        (0, 34, 30, FAINT), (36, 30, 52, MID), (72, 28, 24, FAINT),
        (190, 30, 44, MID), (226, 36, 28, FAINT), (262, 32, 56, MID),
    ]
    for off, w, h, tone in blocks:
        draw.rectangle([x0 + off, ground - h, x0 + off + w, ground], fill=tone)

    # The tower: a tapered slab with the great arch cut through it.
    top = y0 + 24
    draw.polygon(
        [(cx - 16, top), (cx + 16, top), (cx + 29, ground), (cx - 29, ground)],
        fill=INK,
    )
    draw.ellipse([cx - 11, top + 28, cx + 11, top + 88],
                 fill=PAPER, outline=INK, width=1)

    # The burst at the tower's crown, and two short incoming streaks.
    bx, by = cx, top - 5
    for dx, dy in [(-13, -7), (0, -14), (13, -7), (-16, 3), (16, 3), (-8, -12), (8, -12)]:
        draw.line([bx, by, bx + dx, by + dy], fill=RED, width=3)
    draw.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=RED)
    draw.line([bx - 58, y0 - 4, bx - 13, by - 3], fill=RED, width=2)
    draw.line([bx + 13, by - 3, bx + 58, y0 - 4], fill=RED, width=2)

    # Ground rule and caption.
    draw.line([x0, ground + 5, x1, ground + 5], fill=INK, width=3)
    cap_f = serif(12)
    cap = wrap(draw, LEAD_CAPTION, cap_f, x1 - x0)
    cy = ground + 10
    for line in cap:
        w = draw.textlength(line, font=cap_f)
        draw.text((x0 + (x1 - x0 - w) / 2, cy), line, font=cap_f, fill=SOFT)
        cy += 16


# --------------------------------------------------------------------------
# Page assembly
# --------------------------------------------------------------------------

def build() -> Image.Image:
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # Double-rule frame.
    draw.rectangle([FRAME_OUT, FRAME_OUT, W - FRAME_OUT, H - FRAME_OUT],
                   outline=INK, width=3)
    draw.rectangle([FRAME_IN, FRAME_IN, W - FRAME_IN, H - FRAME_IN],
                   outline=INK, width=1)

    y = 36

    # Masthead.
    mast_f = fit_size(draw, MASTHEAD, serif_b, 60, 40, CW, tracking=2)
    draw_tracked(draw, W // 2, y, MASTHEAD, mast_f, INK, 2)
    y += 68

    # Thick-and-thin rule under the masthead.
    draw.line([MX, y, MX + CW, y], fill=INK, width=4)
    draw.line([MX, y + 7, MX + CW, y + 7], fill=INK, width=1)
    y += 14

    # Dateline row: edition marks flank the date, which carries the day.
    flank_f = serif(13)
    draw.text((MX, y + 8), "VOL. I — NO. 24", font=flank_f, fill=SOFT)
    right = "GLOBAL EDITION"
    draw.text((MX + CW - draw.textlength(right, font=flank_f), y + 8),
              right, font=flank_f, fill=SOFT)
    date_f = serif_b(30)
    dw = draw.textlength(DATELINE, font=date_f)
    draw.text(((W - dw) / 2, y), DATELINE, font=date_f, fill=INK)
    y += 40
    draw.line([MX, y, MX + CW, y], fill=INK, width=1)
    y += 12

    # Lead story: text left, tower motif right.
    lead_top = y
    motif_w = 298
    text_w = CW - motif_w - 24
    draw_tracked_label(draw, MX, y, LEAD_LABEL)
    y += 20
    head_lines = wrap(draw, LEAD_HEAD, serif_b(40), text_w)
    y = draw_block(draw, MX, y, head_lines, serif_b(40), INK, 46)
    y += 5
    sub_lines = wrap(draw, LEAD_SUB, serif(17), text_w)
    y = draw_block(draw, MX, y, sub_lines, serif(17), SOFT, 22)
    lead_bottom = y
    draw_motif(draw, MX + CW - motif_w, lead_top, MX + CW, lead_top + 190)
    y = max(lead_bottom, lead_top + 190) + 9
    draw.line([MX, y, MX + CW, y], fill=INK, width=1)
    y += 11

    # Story grid: two columns, hairlines between rows and down the gutter.
    grid_top = y
    col_gap = 28
    col_w = (CW - col_gap) // 2
    col_x = [MX, MX + col_w + col_gap]
    head_f, sum_f = serif_b(19), sans(12)
    rows = [STORIES[i:i + 2] for i in range(0, len(STORIES), 2)]
    for ri, row in enumerate(rows):
        heights = []
        for label, head, summary in row:
            hl = wrap(draw, head, head_f, col_w)
            sl = wrap(draw, summary, sum_f, col_w)
            heights.append(19 + len(hl) * 23 + 3 + len(sl) * 16)
        row_h = max(heights)
        for ci, (label, head, summary) in enumerate(row):
            x = col_x[ci]
            draw_tracked_label(draw, x, y, label)
            hl = wrap(draw, head, head_f, col_w)
            yy = draw_block(draw, x, y + 19, hl, head_f, INK, 23)
            sl = wrap(draw, summary, sum_f, col_w)
            draw_block(draw, x, yy + 3, sl, sum_f, SOFT, 16)
        y += row_h
        if ri < len(rows) - 1:
            y += 5
            draw.line([MX, y, MX + CW, y], fill=FAINT, width=1)
            y += 6
    draw.line([MX + col_w + col_gap // 2, grid_top, MX + col_w + col_gap // 2, y],
              fill=FAINT, width=1)

    # Markets strip between rules.
    y += 8
    draw.line([MX, y, MX + CW, y], fill=INK, width=1)
    y += 5
    mkt_f = fit_size(draw, MARKETS, sans_b, 15, 10, CW)
    mw = draw.textlength(MARKETS, font=mkt_f)
    draw.text(((W - mw) / 2, y), MARKETS, font=mkt_f, fill=INK)
    y += 21
    draw.line([MX, y, MX + CW, y], fill=INK, width=1)
    y += 10

    # In brief: a red label, then one wrapped run of short items.
    brief_f = sans(13)
    label = "IN BRIEF"
    label_w = tracked_width(draw, label, sans_b(13), 1) + 12
    draw_tracked_label(draw, MX, y, label, fnt=sans_b(13))
    brief_lines = wrap_brief(draw, BRIEF, brief_f, CW, CW - label_w)
    yy = y
    for i, line in enumerate(brief_lines):
        x = MX + label_w if i == 0 else MX
        draw.text((x, yy), line, font=brief_f, fill=SOFT)
        yy += 17
    y = yy + 6

    # Footer.
    draw.line([MX, y, MX + CW, y], fill=FAINT, width=1)
    y += 9
    foot_f = serif(15)
    fw = draw.textlength(FOOTER, font=foot_f)
    draw.text(((W - fw) / 2, y), FOOTER, font=foot_f, fill=INK)

    return img


def draw_tracked_label(draw, x, y, text, fnt=None, left=False):
    """A small red caps label, tracked out, drawn from x (not centred)."""
    fnt = fnt or sans_b(13)
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=fnt, fill=RED)
        cx += draw.textlength(ch, font=fnt) + 1


def wrap_brief(draw, text, fnt, full_w, first_w):
    """Wrap where the first line is narrower (the label sits on it)."""
    lines, cur, limit = [], "", first_w
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= limit or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
            limit = full_w
    if cur:
        lines.append(cur)
    return lines


def main():
    out = Path(__file__).resolve().parent / "entry.png"
    build().save(out, format="PNG", optimize=True)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
