"""Small spot illustrations, drawn from primitives, for the numbers strip."""
from __future__ import annotations

from PIL import ImageDraw

INK = (30, 34, 40)
ACCENT = (166, 30, 38)
STEEL = (96, 106, 118)
WARM = (196, 128, 52)
TEAL = (32, 104, 104)
PALE = (222, 214, 198)


def _box(d, x, y, s):
    return x, y, x + s, y + s


def drone(d: ImageDraw.ImageDraw, x, y, s=20):
    d.line((x + 4, y + 5, x + 8, y + 9), fill=STEEL, width=1)
    d.line((x + 16, y + 5, x + 12, y + 9), fill=STEEL, width=1)
    d.ellipse((x + 1, y + 2, x + 7, y + 7), outline=STEEL)
    d.ellipse((x + 13, y + 2, x + 19, y + 7), outline=STEEL)
    d.rounded_rectangle((x + 7, y + 8, x + 13, y + 13), radius=2, fill=ACCENT)
    d.line((x + 10, y + 13, x + 10, y + 17), fill=INK, width=1)


def ballot(d: ImageDraw.ImageDraw, x, y, s=20):
    d.rectangle((x + 3, y + 6, x + 17, y + 18), outline=INK)
    d.line((x + 5, y + 10, x + 9, y + 14), fill=ACCENT, width=2)
    d.line((x + 9, y + 14, x + 16, y + 4), fill=ACCENT, width=2)


def virus(d: ImageDraw.ImageDraw, x, y, s=20):
    d.ellipse((x + 4, y + 4, x + 16, y + 16), outline=ACCENT, width=2)
    for dx, dy in ((10, 0), (10, 20), (0, 10), (20, 10), (3, 3), (17, 3), (3, 17), (17, 17)):
        d.line((x + 10, y + 10, x + dx, y + dy), fill=ACCENT, width=1)
        d.ellipse((x + dx - 1, y + dy - 1, x + dx + 1, y + dy + 1), fill=ACCENT)


def rocket(d: ImageDraw.ImageDraw, x, y, s=20):
    d.polygon([(x + 10, y + 1), (x + 14, y + 11), (x + 6, y + 11)], fill=INK)
    d.rectangle((x + 7, y + 11, x + 13, y + 15), fill=STEEL)
    d.polygon([(x + 7, y + 15), (x + 10, y + 19), (x + 13, y + 15)], fill=WARM)
    d.line((x + 3, y + 13, x + 7, y + 15), fill=STEEL)
    d.line((x + 17, y + 13, x + 13, y + 15), fill=STEEL)


def chip(d: ImageDraw.ImageDraw, x, y, s=20):
    d.rectangle((x + 4, y + 4, x + 16, y + 16), outline=INK, width=2)
    d.rectangle((x + 8, y + 8, x + 12, y + 12), fill=ACCENT)
    for i in range(3):
        o = 6 + i * 4
        d.line((x + o, y + 1, x + o, y + 4), fill=STEEL)
        d.line((x + o, y + 16, x + o, y + 19), fill=STEEL)
        d.line((x + 1, y + o, x + 4, y + o), fill=STEEL)
        d.line((x + 16, y + o, x + 19, y + o), fill=STEEL)


def drum(d: ImageDraw.ImageDraw, x, y, s=20):
    d.rounded_rectangle((x + 4, y + 4, x + 16, y + 18), radius=3, fill=INK)
    d.line((x + 4, y + 9, x + 16, y + 9), fill=PALE)
    d.line((x + 4, y + 13, x + 16, y + 13), fill=PALE)
    d.ellipse((x + 6, y + 15, x + 9, y + 18), fill=ACCENT)


def gavel(d: ImageDraw.ImageDraw, x, y, s=20):
    d.rounded_rectangle((x + 3, y + 4, x + 13, y + 9), radius=1, fill=INK)
    d.line((x + 8, y + 9, x + 14, y + 18), fill=WARM, width=3)
    d.line((x + 2, y + 18, x + 18, y + 18), fill=STEEL, width=2)


def train(d: ImageDraw.ImageDraw, x, y, s=20):
    d.rounded_rectangle((x + 2, y + 4, x + 18, y + 14), radius=3, fill=INK)
    d.rectangle((x + 5, y + 6, x + 9, y + 10), fill=PALE)
    d.rectangle((x + 11, y + 6, x + 15, y + 10), fill=PALE)
    d.ellipse((x + 4, y + 14, x + 8, y + 18), fill=STEEL)
    d.ellipse((x + 12, y + 14, x + 16, y + 18), fill=STEEL)


def ship(d: ImageDraw.ImageDraw, x, y, s=20):
    d.polygon([(x + 2, y + 12), (x + 18, y + 12), (x + 15, y + 17), (x + 5, y + 17)], fill=INK)
    d.rectangle((x + 6, y + 7, x + 14, y + 12), fill=STEEL)
    d.rectangle((x + 9, y + 3, x + 11, y + 7), fill=ACCENT)


ICONS = {
    'drone': drone, 'ballot': ballot, 'virus': virus, 'rocket': rocket,
    'chip': chip, 'drum': drum, 'gavel': gavel, 'train': train, 'ship': ship,
}
