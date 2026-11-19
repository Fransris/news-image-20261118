#!/usr/bin/env python3
"""Compose the 1024x1024 page for Wednesday 18 November 2026.

Layout: masthead, a hero band (lead story on the left, a drawn night-side Earth
with the day's hotspots on the right), the day in numbers, then 48 story cards
in four columns, then the sources line.

Data lives in tools/make_news_image.py (STORIES, TIMELINE, NUMBERS). Type
sizes shrink step by step until four columns fit, so an edit can never clip.

Run:  python3 tools/make_page.py entry.png
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

SRC = Path(__file__).with_name('make_news_image.py')
_spec = importlib.util.spec_from_file_location('m', SRC)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

W = H = 1024
M = 22
PAPER, INK, DARK, BODY, MUTED = m.PAPER, m.INK, m.DARK, m.BODY, m.MUTED
ACCENT, TEAL, GOLD, RULE, WHITE, DIM, FAINT = (m.ACCENT, m.TEAL, m.GOLD, m.RULE,
                                               m.WHITE, m.DIM, m.FAINT)
load, wrap, tracked, rule, fit = m.load, m.wrap, m.tracked, m.rule, m.fit
SERIF_BOLD, SERIF, SANS, SANS_BOLD, MONO_BOLD = (m.SERIF_BOLD, m.SERIF, m.SANS,
                                                 m.SANS_BOLD, m.MONO_BOLD)
STORIES, TIMELINE, NUMBERS = m.STORIES, m.TIMELINE, m.NUMBERS

FIELD_NAMES = {
    'WAR': 'WAR & SECURITY', 'DIPLO': 'DIPLOMACY', 'POL': 'POLITICS & COURTS',
    'ECON': 'ECONOMY & MARKETS', 'TECH': 'TECHNOLOGY', 'HEALTH': 'HEALTH',
    'DISASTER': 'CLIMATE & DISASTER', 'CULTURE': 'CULTURE', 'SCIENCE': 'SCIENCE',
    'SPORT': 'SPORT', 'CLIMATE': 'CLIMATE',
}

LEAD = (
    'IRAN ANSWERS A STRIKE WITH DRONES ON TWO GULF BASES',
    'US jets hit an IRGC missile site on Qeshm Island; overnight, Iran fired at '
    'American forces in Kuwait and Bahrain. A third US carrier group is in the '
    'theatre, and Washington says it is still weighing strikes on the mainland.',
    '\u201cWe are not under systemic attack.\u201d \u2014 RUBIO, ON THE OUTAGES AT HOME',
)

HOTSPOTS = [
    ('SHENZHEN', 0.30, 0.30), ('QESHM', 0.62, 0.52), ('ODESA', 0.52, 0.26),
    ('BADME', 0.40, 0.62), ('KINSHASA', 0.44, 0.70), ('CARACAS', 0.20, 0.60),
    ('DEIR AL-BALAH', 0.56, 0.45), ('CANBERRA', 0.80, 0.80),
]


class Overflow(Exception):
    pass


def dek_layout(dek, colw, budget, scale):
    for size in (9.4, 9.1, 8.8, 8.5, 8.2, 7.9, 7.6, 7.3):
        s = size * scale
        font = load(SANS, s)
        lines = wrap(dek, font, colw)
        if len(lines) <= budget:
            return font, s, lines
    raise Overflow(f'dek will not fit: {dek[:40]!r}')


def draw_globe(d, box):
    """A night-side Earth limb with city lights, clipped to its panel."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    panel = Image.new('RGB', (w, h), (9, 14, 26))
    pd = ImageDraw.Draw(panel)
    cx, cy, r = w * 0.52, h * 1.62, h * 1.28

    # sky: a vertical gradient, one line per row
    top, bot = (9, 14, 26), (24, 38, 60)
    for i in range(h):
        t = i / max(h - 1, 1)
        col = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        pd.line((0, i, w, i), fill=col)

    # stars, placed by a hash so two runs agree
    for i in range(260):
        hsh = hashlib.sha256(f'star{i}'.encode()).digest()
        sx = (hsh[0] * 256 + hsh[1]) % w
        sy = (hsh[2] * 256 + hsh[3]) % int(h * 0.66)
        lum = 110 + hsh[4] % 130
        pd.point((sx, sy), fill=(lum, lum, min(255, lum + 14)))

    # the glow above the limb
    for k in range(30, 0, -1):
        rr = r + k * 1.5
        shade = int(150 * (1 - k / 31) ** 2)
        pd.arc((cx - rr, cy - rr, cx + rr, cy + rr), 196, 344,
               fill=(shade // 2, shade, int(shade * 1.2)), width=2)

    # the body of the planet, then its lit rim
    pd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(9, 28, 38))
    for k in range(20, 0, -1):
        rr = r - k * 2.0
        t = k / 20
        pd.arc((cx - rr, cy - rr, cx + rr, cy + rr), 198, 342,
               fill=(int(20 + 30 * (1 - t)), int(52 + 46 * (1 - t)), int(66 + 34 * (1 - t))),
               width=2)

    # city lights, clustered on the lit band of the limb
    import math
    for i in range(700):
        hsh = hashlib.sha256(f'city{i}'.encode()).digest()
        ang = 198 + (hsh[0] * 256 + hsh[1]) % 144
        rad = r - 3 - (hsh[2] * 256 + hsh[3]) % int(h * 0.55)
        a = math.radians(ang)
        px = cx + rad * math.cos(a)
        py = cy + rad * math.sin(a)
        if 0 <= px < w and 0 <= py < h:
            warm = 150 + hsh[4] % 105
            pd.point((px, py), fill=(warm, int(warm * 0.86), int(warm * 0.55)))

    # hotspot markers, with a label on the busiest ones
    lab = load(SANS_BOLD, 6.2)
    for name, fx, fy in HOTSPOTS:
        px, py = fx * w, fy * h
        pd.ellipse((px - 2.4, py - 2.4, px + 2.4, py + 2.4), fill=(240, 128, 64))
        pd.ellipse((px - 5.2, py - 5.2, px + 5.2, py + 5.2), outline=(238, 158, 96))
        pd.text((px + 7, py - 3.4), name, font=lab, fill=(232, 226, 214))

    d._image.paste(panel, (x0, y0))


def draw_card(d, story, x0, y, colw, lead, scale):
    region, field, source, head, dek, _ = story
    tag = load(SANS_BOLD, 7.2 * scale)
    tracked(d, (x0, y), f'{region} · {FIELD_NAMES[field]}', tag, ACCENT, 0.5)
    sf = load(SANS_BOLD, 7.0 * scale)
    d.text((x0 + colw - sf.getlength(source), y + 0.5), source, font=sf, fill=FAINT)
    y += 10 * scale

    hsize = (14.2 if lead else 12.4) * scale
    hf, hlines, used = fit(head, SERIF_BOLD, hsize, 8.6 * scale, colw, 3 if lead else 2)
    for line in hlines:
        d.text((x0, y), line, font=hf, fill=INK)
        y += used * 1.08
    y += 2

    font, size, lines = dek_layout(dek, colw, 4 if lead else 2, scale)
    for line in lines:
        d.text((x0, y), line, font=font, fill=BODY)
        y += size * 1.26
    return y


def measure(story, colw, lead, scale):
    region, field, source, head, dek, _ = story
    hsize = (14.2 if lead else 12.4) * scale
    hf, hlines, used = fit(head, SERIF_BOLD, hsize, 8.6 * scale, colw, 3 if lead else 2)
    h = 10 * scale + len(hlines) * used * 1.08 + 2
    font, size, lines = dek_layout(dek, colw, 4 if lead else 2, scale)
    return h + len(lines) * size * 1.26


def render(scale, out):
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ------------------------------------------------------------- masthead
    tracked(d, (M, 8), 'THE DAY IN WORLD NEWS', load(SERIF_BOLD, 31), INK, 0.9)
    rf = load(SANS_BOLD, 10.5)
    right = 'WED · 18 NOV 2026'
    d.text((W - M - rf.getlength(right), 14), right, font=rf, fill=INK)
    d.rectangle((W - M - 26, 28, W - M, 31), fill=ACCENT)

    claim = ('Everything on this page happened, or was first reported, on Wednesday '
             '18 November 2026, UTC.')
    d.text((M, 43), claim, font=load(SERIF, 9.0), fill=MUTED)

    fields = {}
    for story in STORIES:
        fields[story[1]] = fields.get(story[1], 0) + 1
    counts = (f'{len(STORIES)} STORIES  ·  {len({s[0] for s in STORIES})} REGIONS  ·  '
              f'{len(fields)} FIELDS  ·  ONE PAGE  ·  SOURCED IN PLACE')
    tracked(d, (M, 55), counts, load(SANS_BOLD, 7.4), ACCENT, 1.1)
    rule(d, M, 68, W - M, 68, INK, 2)

    # ---------------------------------------------------------------- hero
    hero_top, hero_bot = 74, 244
    panel_x = 640
    draw_globe(d, (panel_x, hero_top, W - M, hero_bot))
    d.rectangle((panel_x, hero_top, W - M, hero_bot), outline=(40, 48, 58))

    kick = load(SANS_BOLD, 8.0)
    tracked(d, (M, hero_top + 2), 'LEAD  ·  THE GULF', kick, ACCENT, 1.2)
    hf, hl, hs = fit(LEAD[0], SERIF_BOLD, 27, 16, panel_x - M - 16, 3)
    y = hero_top + 14
    for line in hl:
        d.text((M, y), line, font=hf, fill=INK)
        y += hs * 1.05
    font, size, lines = dek_layout(LEAD[1], panel_x - M - 16, 3, 1.0)
    for line in lines:
        d.text((M, y + 2), line, font=font, fill=BODY)
        y += size * 1.26
    y += 6
    rule(d, M, y, M + 22, y, ACCENT, 3)
    d.text((M + 30, y - 5), LEAD[2], font=load(SANS_BOLD, 7.6), fill=TEAL)
    if y + 12 > hero_bot:
        raise Overflow(f'hero text overflows: {y + 12} > {hero_bot}')

    # legend under the globe
    lg = load(SANS_BOLD, 6.6)
    d.text((panel_x + 6, hero_bot - 12), 'THE DAY, WHERE IT HAPPENED', font=lg, fill=(150, 160, 175))

    # --------------------------------------------------------- numbers strip
    nb_top, nb_bot = hero_bot + 4, hero_bot + 46
    cell = (W - 2 * M) / len(NUMBERS)
    rule(d, M, nb_top, W - M, nb_top, INK, 1)
    for i, (num, cap) in enumerate(NUMBERS):
        x = M + i * cell
        if i:
            rule(d, x - 4, nb_top + 3, x - 4, nb_bot - 3, RULE, 1)
        nf, nl, used = fit(num, SERIF_BOLD, 16.5, 9, cell - 9, 1)
        d.text((x, nb_top + 2), nl[0], font=nf, fill=ACCENT)
        lines = wrap(cap, load(SANS, 6.8), cell - 9)
        if len(lines) > 2:
            raise Overflow(f'caption too long: {num}')
        yy = nb_top + 22
        for line in lines:
            d.text((x, yy), line, font=load(SANS, 6.8), fill=MUTED)
            yy += 8.2
    rule(d, M, nb_bot, W - M, nb_bot, INK, 1)

    # ---------------------------------------------------------------- stories
    col_top = nb_bot + 6
    col_bot = 968
    gut = 11
    colw = (W - 2 * M - 3 * gut) / 4

    columns = [[] for _ in range(4)]
    heights = [0.0] * 4
    for story in STORIES:
        i = heights.index(min(heights))
        lead = not columns[i]
        columns[i].append(story)
        heights[i] += measure(story, colw, lead, scale) + 6

    for ci, stories in enumerate(columns):
        x0 = M + ci * (colw + gut)
        if ci:
            rule(d, x0 - gut / 2, col_top, x0 - gut / 2, col_bot, RULE, 1)
        y = col_top
        for n, story in enumerate(stories):
            y = draw_card(d, story, x0, y, colw, n == 0, scale)
            if n < len(stories) - 1:
                y += 6
                rule(d, x0, y - 3, x0 + colw, y - 3, (224, 216, 202), 1)
        if y > col_bot:
            raise Overflow(f'column {ci + 1} ends at {y:.1f} > {col_bot} (scale {scale})')

    # ---------------------------------------------------------------- footer
    rule(d, M, col_bot + 4, W - M, col_bot + 4, INK, 2)
    foot = ('Each item was reported on the day by the outlet named beside it: AFP, AP, Axios, '
            'BBC, Bloomberg, CNBC, CNN, CTK, EIA, Kyodo, NASA, NYT, PAHO, Polygon, Reuters, '
            'SBS, Sudantribune, The Hindu, WHO, WSJ. Assembled by an AI agent for make.fun.')
    lines = wrap(foot, load(SANS, 6.6), W - 2 * M)
    if len(lines) > 2:
        raise Overflow('footer too long')
    yy = col_bot + 8
    for line in lines:
        d.text((M, yy), line, font=load(SANS, 6.6), fill=MUTED)
        yy += 7.8

    # a whisper of print texture, so the page reads as paper not pixels
    noise = Image.effect_noise((W, H), 16).convert('L').point(lambda v: int(v * 0.010))
    grain = Image.merge('RGB', (noise, noise, noise))
    img = ImageChops.add(img, grain)
    img = img.filter(ImageFilter.GaussianBlur(0.25))

    img.save(out, format='PNG', optimize=True)
    return img


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else 'entry.png')
    for scale in (1.0, 0.99, 0.98, 0.97, 0.96, 0.95, 0.94, 0.93, 0.92, 0.90, 0.88):
        try:
            img = render(scale, out)
        except Overflow as exc:
            print(f'scale {scale}: {exc}')
            continue
        print(f'wrote {out} ({out.stat().st_size} bytes, {img.size[0]}x{img.size[1]}, '
              f'{len(STORIES)} stories, type scale {scale})')
        return 0
    raise SystemExit('no scale fits')


if __name__ == '__main__':
    sys.exit(main())
