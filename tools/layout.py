#!/usr/bin/env python3
"""Re-lay the page with an adaptive type scale.

Reads tools/make_news_image.py, keeps its data (STORIES, TIMELINE, NUMBERS),
and replaces everything from the card renderer down with a version that
shrinks story type until four columns fit, then writes the PNG.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SRC = Path(__file__).with_name('make_news_image.py')
spec = importlib.util.spec_from_file_location('m', SRC)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

from PIL import Image, ImageDraw  # noqa: E402

W = H = 1024
M = 22
PAPER, INK, DARK, BODY, MUTED = m.PAPER, m.INK, m.DARK, m.BODY, m.MUTED
ACCENT, TEAL, GOLD, RULE, WHITE, DIM, FAINT = m.ACCENT, m.TEAL, m.GOLD, m.RULE, m.WHITE, m.DIM, m.FAINT
load, wrap, tracked, rule, fit = m.load, m.wrap, m.tracked, m.rule, m.fit
SERIF_BOLD, SERIF, SANS, SANS_BOLD, MONO_BOLD = m.SERIF_BOLD, m.SERIF, m.SANS, m.SANS_BOLD, m.MONO_BOLD
STORIES, TIMELINE, NUMBERS = m.STORIES, m.TIMELINE, m.NUMBERS

FIELD_NAMES = {
    'WAR': 'WAR & SECURITY', 'DIPLO': 'DIPLOMACY', 'POL': 'POLITICS & COURTS',
    'ECON': 'ECONOMY & MARKETS', 'TECH': 'TECHNOLOGY', 'HEALTH': 'HEALTH',
    'DISASTER': 'CLIMATE & DISASTER', 'CULTURE': 'CULTURE', 'SCIENCE': 'SCIENCE',
    'SPORT': 'SPORT', 'CLIMATE': 'CLIMATE',
}


class Overflow(Exception):
    pass


def dek_layout(dek, colw, budget, scale):
    for size in (9.4, 9.1, 8.8, 8.5, 8.2, 7.9, 7.6, 7.3):
        s = size * scale
        font = load(SANS, s)
        lines = wrap(dek, font, colw)
        if len(lines) <= budget:
            return font, s, lines
    raise Overflow(f"dek will not fit: {dek[:40]!r}")


def draw_card(d, story, x0, y, colw, lead, scale):
    region, field, source, head, dek, _ = story
    tag = load(SANS_BOLD, 7.2 * scale)
    tracked(d, (x0, y), f"{region} · {FIELD_NAMES[field]}", tag, ACCENT, 0.5)
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
    tracked(d, (M, 8), 'THE DAY IN WORLD NEWS', load(SERIF_BOLD, 32), INK, 0.9)
    rf = load(SANS_BOLD, 10.5)
    right = 'WED · 18 NOV 2026'
    d.text((W - M - rf.getlength(right), 15), right, font=rf, fill=INK)
    d.rectangle((W - M - 26, 30, W - M, 33), fill=ACCENT)

    claim = ('Everything on this page happened, or was first reported, on Wednesday '
             '18 November 2026, UTC.')
    d.text((M, 46), claim, font=load(SERIF, 9.2), fill=MUTED)

    fields = {}
    for story in STORIES:
        fields[story[1]] = fields.get(story[1], 0) + 1
    counts = (f'{len(STORIES)} STORIES  ·  {len({s[0] for s in STORIES})} REGIONS  ·  '
              f'{len(fields)} FIELDS  ·  ONE PAGE  ·  SOURCED IN PLACE')
    tracked(d, (M, 58), counts, load(SANS_BOLD, 7.6), ACCENT, 1.1)
    rule(d, M, 72, W - M, 72, INK, 2)

    # ------------------------------------------------------------- field row
    ff = load(SANS_BOLD, 7.0)
    fx = M
    for key, n in sorted(fields.items(), key=lambda kv: -kv[1]):
        label = f'{FIELD_NAMES[key]} {n}'
        w = ff.getlength(label) + 10
        if fx + w > W - M:
            break
        d.text((fx, 79), label, font=ff, fill=TEAL)
        fx += w
    rule(d, M, 90, W - M, 90, RULE, 1)

    # --------------------------------------------------------------- timeline
    tl_top, tl_bot = 94, 170
    d.rectangle((M, tl_top, W - M, tl_bot), fill=DARK)
    slot = (W - 2 * M) / len(TIMELINE)
    for i, (when, what) in enumerate(TIMELINE):
        x = M + i * slot + 5
        d.text((x, tl_top + 5), when, font=load(MONO_BOLD, 7.2), fill=GOLD)
        d.ellipse((x - 1, tl_top + 20, x + 3, tl_top + 24), fill=GOLD)
        lines = wrap(what, load(SANS, 7.6), slot - 9)
        if len(lines) > 6:
            raise Overflow(f'timeline slot too long: {when}')
        yy = tl_top + 29
        for line in lines:
            d.text((x, yy), line, font=load(SANS, 7.6), fill=DIM)
            yy += 9.6

    # ---------------------------------------------------------- numbers strip
    nb_top = tl_bot + 4
    nb_bot = nb_top + 40
    cell = (W - 2 * M) / len(NUMBERS)
    for i, (num, cap) in enumerate(NUMBERS):
        x = M + i * cell
        if i:
            rule(d, x - 4, nb_top + 2, x - 4, nb_bot - 2, RULE, 1)
        nf, nl, used = fit(num, SERIF_BOLD, 17.5, 10, cell - 9, 1)
        d.text((x, nb_top + 1), nl[0], font=nf, fill=ACCENT)
        lines = wrap(cap, load(SANS, 7.0), cell - 9)
        if len(lines) > 2:
            raise Overflow(f'number caption too long: {num}')
        yy = nb_top + 23
        for line in lines:
            d.text((x, yy), line, font=load(SANS, 7.0), fill=MUTED)
            yy += 8.4
    rule(d, M, nb_bot, W - M, nb_bot, INK, 1)

    # ---------------------------------------------------------------- stories
    col_top = nb_bot + 6
    col_bot = 972
    gut = 11
    colw = (W - 2 * M - 3 * gut) / 4

    columns = [[] for _ in range(4)]
    heights = [0.0] * 4
    for story in STORIES:
        i = heights.index(min(heights))
        lead = not columns[i]
        columns[i].append(story)
        heights[i] += measure(story, colw, lead, scale) + 7

    for ci, stories in enumerate(columns):
        x0 = M + ci * (colw + gut)
        if ci:
            rule(d, x0 - gut / 2, col_top, x0 - gut / 2, col_bot, RULE, 1)
        y = col_top
        for n, story in enumerate(stories):
            y = draw_card(d, story, x0, y, colw, n == 0, scale)
            if n < len(stories) - 1:
                y += 7
                rule(d, x0, y - 4, x0 + colw, y - 4, (224, 216, 202), 1)
        if y > col_bot:
            raise Overflow(f'column {ci + 1} ends at {y:.1f} > {col_bot} (scale {scale})')

    # ----------------------------------------------------------------- footer
    rule(d, M, col_bot + 4, W - M, col_bot + 4, INK, 2)
    foot = ('Each item was reported on the day by the outlet named beside it: AFP, AP, Axios, '
            'BBC, Bloomberg, CNBC, CNN, CTX, EIA, Kyodo, NASA, NYT, PAHO, Polygon, Reuters, '
            'SBS, Sudantribune, The Hindu, WHO, WSJ. Assembled by an AI agent for make.fun.')
    lines = wrap(foot, load(SANS, 6.7), W - 2 * M)
    if len(lines) > 2:
        raise Overflow('footer too long')
    yy = col_bot + 8
    for line in lines:
        d.text((M, yy), line, font=load(SANS, 6.7), fill=MUTED)
        yy += 8

    img.save(out, format='PNG', optimize=True)
    return img


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else 'entry.png')
    for scale in (1.0, 0.99, 0.98, 0.97, 0.96, 0.95, 0.94, 0.93, 0.92, 0.90, 0.88, 0.86):
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
