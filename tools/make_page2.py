#!/usr/bin/env python3
"""Compose the 1024x1024 page for Wednesday 18 November 2026 — edition two.

Design notes: a big lead, three secondaries, then the rest of the day as short
one-line items under regional headers, and the day in numbers. Type is large
enough to read at 1024 px; nothing is packed so tight that it turns to texture.
The night-side Earth on the right is drawn from primitives, not an image file.

Run:  python3 tools/make_page2.py entry.png
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import icons  # noqa: E402

W = H = 1024
M = 26

PAPER = (245, 240, 229)
INK = (16, 20, 25)
BODY = (48, 46, 42)
MUTED = (108, 100, 90)
ACCENT = (166, 30, 38)
TEAL = (26, 92, 92)
GOLD = (214, 170, 96)
RULE = (198, 187, 170)
WHITE = (246, 242, 233)
DIM = (206, 200, 189)
FAINT = (168, 160, 148)

FONT_DIRS = [
    Path('/usr/share/fonts/truetype/liberation'),
    Path('/usr/share/fonts/truetype/dejavu'),
    Path('/usr/share/fonts/TTF'),
]
SERIF_BOLD = ['LiberationSerif-Bold.ttf', 'DejaVuSerif-Bold.ttf']
SERIF = ['LiberationSerif-Regular.ttf', 'DejaVuSerif.ttf']
SANS_BOLD = ['DejaVuSans-Bold.ttf', 'LiberationSans-Bold.ttf']
SANS = ['DejaVuSans.ttf', 'LiberationSans-Regular.ttf']
MONO_BOLD = ['DejaVuSansMono-Bold.ttf', 'LiberationMono-Bold.ttf']


def load(names, size):
    for name in names:
        for d in FONT_DIRS:
            p = d / name
            if p.exists():
                return ImageFont.truetype(str(p), int(size))
    raise SystemExit(f'no font of {names}')


def wrap(text, font, max_w):
    words, lines, cur = text.split(), [], ''
    for word in words:
        trial = f'{cur} {word}'.strip()
        if font.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, text, font, fill, x, y, max_w, line_h, max_lines):
    lines = wrap(text, font, max_w)
    if len(lines) > max_lines:
        raise SystemExit(f'{len(lines)} lines > {max_lines}: {text[:50]!r}')
    for line in lines:
        d.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y


def fit(text, names, start, floor, max_w, max_lines):
    size = start
    while size >= floor:
        font = load(names, size)
        if len(wrap(text, font, max_w)) <= max_lines:
            return font, wrap(text, font, max_w), size
        size -= 0.5
    raise SystemExit(f'will not fit: {text[:50]!r}')


def tracked(d, xy, text, font, fill, spacing=1.0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + spacing
    return x


def rule(d, x0, y0, x1, y1, fill=RULE, width=1):
    d.line((x0, y0, x1, y1), fill=fill, width=width)


LEAD = (
    'ODESA BURNED, THEN BOMBED AGAIN AS MEDICS ARRIVED',
    'Russian missiles struck the UNESCO-listed centre of the Black Sea port three '
    'times, then hit the same street again as rescuers reached it. Four people died '
    'and nine were hurt; President Zelenskyy called it "brutal and deliberate".',
    '\u201cA double tap on our city. This is what they think of diplomacy.\u201d',
)

SECONDARY = [
    ('DIPLOMACY', 'Xi hugs Trump on the tarmac as the three-power summit nears',
     'APEC opens in Shenzhen with a red carpet and a flypast; Putin is already in '
     'town for Thursday\'s first trilateral.'),
    ('POLITICS', 'Peltola takes Alaska, and the Senate goes 56-44',
     'The Democrat beats Dan Sullivan by four points, handing her party a commanding '
     'majority two weeks after the midterms.'),
    ('ECONOMY', 'Anthropic prices the largest share sale in history',
     '980m shares at $83 raise $81.3bn and value the company at $1.5tn; trading as '
     'ANT starts on Thursday.'),
]

SECTIONS = [
    ('EUROPE', [
        'Russia fired 141 drones overnight; Ukraine says it downed 126 of them.',
        'UN monitors counted 372 civilians killed in Ukraine in October.',
        'Von der Leyen urges every EU state to back a \u20ac45bn loan for Kyiv.',
        'Pistorius sends air defence and F-16 munitions to Ukraine.',
        'Berlin\'s defence chief calls a Pentagon official "stupid" over strike criticism.',
        'Two trains collide outside Prague\'s main station; 46 people are hurt.',
        'A Serbian MiG-29 crashes near Stara Pazova and its pilot is killed.',
        '19 die as a Russian military aircraft goes down in Siberia.',
        'A US colonel accused of spying for Russia leaves British custody.',
        'London and Brussels drop "trusted partnership" from the summit draft.',
        'Sweden\'s parties race a Christmas deadline to form a government.',
        'Europe\'s stocks fall a third day; miners drop 4.7% as copper slides.',
    ]),
    ('AMERICAS', [
        'The US, Mexico and Bolivia lose measles elimination status.',
        'The Americas have logged 58,213 measles cases and 82 deaths this year.',
        'Nvidia posts $115.8bn and guides $130bn, yet the stock falls 2%.',
        'Fed minutes point to more hikes; the Dow closes down 561 points.',
        'A Fed governor calls for a half-point rise in December.',
        'Hegseth restores military ties with Venezuela after 21 years.',
        'Rubio says the outages at Microsoft, the FAA and banks were not an attack.',
        'An AI tool finds a critical Java flaw; "all major companies" are exposed.',
        'Carney books a Trump meeting and sends Kyiv another aid package.',
        'Anthropic\'s shares start trading on the Nasdaq under ANT.',
        'Canada works to win back the measles status it lost last year.',
        'US crude stocks rise 3.38m barrels, the largest build in months.',
    ]),
    ('MIDDLE EAST', [
        'US jets strike an IRGC missile site on Iran\'s Qeshm Island.',
        'Iran answers with drones at US forces in Kuwait and Bahrain.',
        'A third US carrier group, the Theodore Roosevelt, is in the theatre.',
        'Houthis fire five drones at Saudi Arabia\'s East-West pipeline.',
        'Trump\'s Board of Peace faults both Israel and Hamas on the ceasefire.',
        'Israel\'s parliament elects Matan Kahana speaker, a blow to Netanyahu.',
        '18,000 Palestinians are at risk as Israel pushes into Deir al-Balah.',
        'The WHO demands unimpeded aid as Gaza faces a fourth winter under water.',
        'A tanker is hit by a projectile in the Strait of Hormuz; one is missing.',
        'Mossad\'s chief pressed Washington for a harder line on Iran.',
        'CENTCOM\'s admiral tours Israel and Saudi Arabia on joint readiness.',
        'Brent holds near $91 as the region\'s supply fears fade.',
    ]),
    ('AFRICA', [
        'Ethiopia and Eritrea mass troops on the Badme line; clashes reported.',
        'Congo\'s Ebola outbreak passes 11,300 cases and 5,500 deaths.',
        'Rebels kill 106 people in eastern Congo and patients flee their beds.',
        'The WHO keeps Congo\'s outbreak a global health emergency.',
        'The UN counts 2,230 civilians killed in Sudan this year, 1,630 by drones.',
        'A week of airstrikes empties West Kordofan and shuts its markets.',
        'Sudan\'s Nyon talks lose a bloc over Islamist inclusion.',
        'Kenya\'s last Ebola patient goes home; no contacts remain in quarantine.',
        'Ethiopia expels Sudanese diplomats, accusing Khartoum of backing the RSF.',
        'Guinea\'s mining crackdown holds 1,263 people and pushes miners into Mali.',
        'Nigeria\'s drug agency breaks a Sahara cocaine route to Europe.',
        'Pretoria reprimands Nigeria\'s new high commissioner over a broadcast row.',
    ]),
    ('ASIA-PACIFIC', [
        'Putin tells APEC the West are "former hegemons" whose sanctions failed.',
        'Xi pledges open trade days after Washington curbs China\'s AI-chip access.',
        'The Quad meets for the first time in two years, on maritime surveillance.',
        'Trump and Marcos sign a trade deal and deepen defence ties in Manila.',
        'Takaichi shakes hands with Xi but wins no formal talks on the trip.',
        'Myanmar\'s Min Aung Hlaing says he will review ties with ASEAN.',
        'A LeT commander is killed in a pre-dawn raid in Kashmir\'s Kulgam.',
        'Tencent misses on revenue as AI capex climbs to 81.4bn yuan.',
        'Cyclone Akvan nears Andhra and Odisha; 50,000 are evacuated.',
        'Air India\'s crash report slips again as the court grants more time.',
        'Fifty schoolchildren in Kerala are taken to hospital after a pollution scare.',
        'Alibaba reports results as Chinese tech digests the chip curbs.',
    ]),
    ('OCEANIA & WORLD', [
        'Albanese is photographed two rows behind Putin at the APEC dinner.',
        'Canberra sanctions a company building illegal West Bank settlements.',
        'Albanese sells AI standards and data-centre rules to APEC.',
        'A 5.7 quake near Arthur\'s Pass shakes Canterbury; aftershocks expected.',
        'New Zealand\'s banks join forces against scams and fraud.',
        'GTA VI unlocks in New Zealand first as a rolling midnight begins.',
        'Voyager 1 passes one light-day from Earth, 25.9bn km out.',
        'A Vals study finds AI models naming civilians as military targets.',
        'France\'s Diallo will challenge Infantino for the FIFA presidency.',
        'Oil slides to a three-month low as US crude stocks swell.',
        'COP30 pushes adaptation finance to $120bn a year by 2035.',
        'Bel\u00e9m hands the climate file to Antalya as the presidency ends.',
    ]),
]

NUMBERS = [
    ('141', 'drones fired at Ukraine overnight', 'drone'),
    ('372', 'civilians killed in Ukraine in October', 'gavel'),
    ('58,213', 'measles cases across the Americas', 'virus'),
    ('11,300', 'Ebola cases in DR Congo', 'virus'),
    ('$115.8bn', 'Nvidia\'s quarterly revenue', 'chip'),
    ('$81.3bn', 'raised by Anthropic, the largest IPO', 'rocket'),
    ('56-44', 'Democratic majority in the Senate', 'ballot'),
    ('46', 'injured in Prague\'s train collision', 'train'),
]

HOTSPOTS = [
    ('ODESA', 0.30, 0.34), ('QESHM', 0.60, 0.56), ('BADME', 0.44, 0.70),
    ('SHENZHEN', 0.70, 0.30), ('CARACAS', 0.18, 0.62), ('GAZA', 0.48, 0.44),
]


def draw_globe(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    panel = Image.new('RGB', (w, h), (10, 16, 28))
    pd = ImageDraw.Draw(panel)
    cx, cy, r = w * 0.5, h * 1.72, h * 1.34

    top, bot = (10, 16, 28), (26, 42, 64)
    for i in range(h):
        t = i / max(h - 1, 1)
        pd.line((0, i, w, i), fill=tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3)))

    for i in range(300):
        hsh = hashlib.sha256(f's{i}'.encode()).digest()
        sx, sy = (hsh[0] * 256 + hsh[1]) % w, (hsh[2] * 256 + hsh[3]) % int(h * 0.7)
        lum = 110 + hsh[4] % 130
        pd.point((sx, sy), fill=(lum, lum, min(255, lum + 16)))

    for k in range(32, 0, -1):
        rr = r + k * 1.6
        shade = int(160 * (1 - k / 33) ** 2)
        pd.arc((cx - rr, cy - rr, cx + rr, cy + rr), 196, 344,
               fill=(shade // 2, shade, int(shade * 1.25)), width=2)

    pd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(8, 26, 36))
    for k in range(22, 0, -1):
        rr = r - k * 2.0
        t = k / 22
        pd.arc((cx - rr, cy - rr, cx + rr, cy + rr), 198, 342,
               fill=(int(22 + 34 * (1 - t)), int(56 + 52 * (1 - t)), int(70 + 40 * (1 - t))),
               width=2)

    import math
    for i in range(800):
        hsh = hashlib.sha256(f'c{i}'.encode()).digest()
        ang = 198 + (hsh[0] * 256 + hsh[1]) % 144
        rad = r - 3 - (hsh[2] * 256 + hsh[3]) % int(h * 0.6)
        a = math.radians(ang)
        px, py = cx + rad * math.cos(a), cy + rad * math.sin(a)
        if 0 <= px < w and 0 <= py < h:
            warm = 150 + hsh[4] % 105
            pd.point((px, py), fill=(warm, int(warm * 0.86), int(warm * 0.55)))

    lab = load(SANS_BOLD, 7.2)
    for name, fx, fy in HOTSPOTS:
        px, py = fx * w, fy * h
        pd.ellipse((px - 3, py - 3, px + 3, py + 3), fill=(242, 132, 66))
        pd.ellipse((px - 6.5, py - 6.5, px + 6.5, py + 6.5), outline=(240, 164, 100))
        pd.text((px + 9, py - 4), name, font=lab, fill=(238, 232, 220))

    d._image.paste(panel, (x0, y0))


def render(out):
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ------------------------------------------------------------- masthead
    tracked(d, (M, 12), 'THE WORLD, 18 NOVEMBER 2026', load(SERIF_BOLD, 33), INK, 0.8)
    rf = load(SANS_BOLD, 10)
    right = 'WEDNESDAY · WORLD EDITION'
    d.text((W - M - rf.getlength(right), 20), right, font=rf, fill=MUTED)
    d.rectangle((W - M - 30, 36, W - M, 39), fill=ACCENT)
    total_items = 1 + len(SECONDARY) + sum(len(items) for _, items in SECTIONS)
    claim = (f'Everything here was reported on the day: {total_items} items, seven '
             'regions, one page.')
    d.text((M, 50), claim, font=load(SERIF, 10.4), fill=BODY)
    rule(d, M, 68, W - M, 68, INK, 2)

    # ----------------------------------------------------------------- hero
    hero_top, hero_bot = 76, 268
    panel_x = 606
    draw_globe(d, (panel_x, hero_top, W - M, hero_bot))
    d.rectangle((panel_x, hero_top, W - M, hero_bot), outline=(44, 52, 62))

    tracked(d, (M, hero_top + 2), 'THE LEAD  ·  UKRAINE', load(SANS_BOLD, 8.4), ACCENT, 1.3)
    hf, hl, hs = fit(LEAD[0], SERIF_BOLD, 30, 18, panel_x - M - 18, 3)
    y = hero_top + 18
    for line in hl:
        d.text((M, y), line, font=hf, fill=INK)
        y += hs * 1.04
    y += 2
    y = block(d, LEAD[1], load(SERIF, 11.4), BODY, M, y, panel_x - M - 18, 15.4, 4)
    rule(d, M, y + 5, M + 26, y + 5, ACCENT, 3)
    block(d, LEAD[2], load(SANS_BOLD, 8.4), TEAL, M + 32, y + 1, panel_x - M - 50, 11, 1)
    if y + 16 > hero_bot:
        raise SystemExit(f'hero overflows: {y + 16} > {hero_bot}')

    # ------------------------------------------------------------ secondary
    sec_top = hero_bot + 8
    gap = 14
    colw = (W - 2 * M - 2 * gap) / 3
    sec_end = sec_top
    for i, (field, head, dek) in enumerate(SECONDARY):
        x0 = M + i * (colw + gap)
        if i:
            rule(d, x0 - gap / 2, sec_top, x0 - gap / 2, sec_top + 96, RULE, 1)
        tracked(d, (x0, sec_top), field, load(SANS_BOLD, 7.4), ACCENT, 1.1)
        hf, hl, hs = fit(head, SERIF_BOLD, 15.5, 11, colw, 3)
        y = sec_top + 12
        for line in hl:
            d.text((x0, y), line, font=hf, fill=INK)
            y += hs * 1.06
        y = block(d, dek, load(SANS, 9.2), BODY, x0, y + 3, colw, 12, 3)
        sec_end = max(sec_end, y)
        if y > sec_top + 104:
            raise SystemExit('secondary card overflows')

    # --------------------------------------------------------- numbers strip
    nb_top = sec_end + 10
    nb_bot = nb_top + 58
    rule(d, M, nb_top, W - M, nb_top, INK, 1)
    cell = (W - 2 * M) / len(NUMBERS)
    for i, (num, cap, icon) in enumerate(NUMBERS):
        x = M + i * cell
        if i:
            rule(d, x - 5, nb_top + 5, x - 5, nb_bot - 5, RULE, 1)
        icons.ICONS[icon](d, x + 1, nb_top + 6, 22)
        nf, nl, used = fit(num, SERIF_BOLD, 19, 11, cell - 32, 1)
        d.text((x + 27, nb_top + 3), nl[0], font=nf, fill=ACCENT)
        block(d, cap, load(SANS, 7.2), MUTED, x, nb_top + 30, cell - 10, 9, 3)
    rule(d, M, nb_bot, W - M, nb_bot, INK, 1)

    # -------------------------------------------------------------- sections
    sec_y = nb_bot + 8
    sec_bot = 966
    sgap = 16
    sw = (W - 2 * M - 2 * sgap) / 3
    bullet_font = load(SANS, 9.3)

    def section_height(items):
        h = 20.0
        for text in items:
            lines = wrap(text, bullet_font, sw - 9)
            if len(lines) > 2:
                raise SystemExit(f'bullet too long: {text[:44]!r}')
            h += len(lines) * 11.1 + 2.2
        return h

    cols = [[] for _ in range(3)]
    col_h = [0.0] * 3
    for region, items in SECTIONS:
        h = section_height(items) + 8
        i = col_h.index(min(col_h))
        cols[i].append((region, items))
        col_h[i] += h

    for ci, blocks in enumerate(cols):
        x0 = M + ci * (sw + sgap)
        y = sec_y
        for region, items in blocks:
            d.rectangle((x0, y, x0 + sw, y + 13), fill=INK)
            tracked(d, (x0 + 5, y + 3), f'{region}  \u00b7  {len(items)}',
                    load(SANS_BOLD, 7.6), WHITE, 0.8)
            y += 20
            for text in items:
                d.ellipse((x0, y + 3.4, x0 + 2.6, y + 6), fill=ACCENT)
                for line in wrap(text, bullet_font, sw - 9):
                    d.text((x0 + 9, y), line, font=bullet_font, fill=BODY)
                    y += 11.1
                y += 2.2
            y += 7
        if y > sec_bot:
            raise SystemExit(f'section column {ci + 1} overflows: {y:.0f} > {sec_bot}')

    # ---------------------------------------------------------------- footer
    rule(d, M, sec_bot + 4, W - M, sec_bot + 4, INK, 2)
    foot = ('Reported by AFP, AP, Axios, BBC, Bloomberg, CNBC, CNN, CTK, EIA, The Guardian, '
            'Kyodo, NASA, NYT, PAHO, Polygon, Reuters, SBS, Sudantribune, The Hindu, WHO and '
            'the WSJ on Wednesday 18 November 2026. Assembled by an AI agent for make.fun.')
    block(d, foot, load(SANS, 7.2), MUTED, M, sec_bot + 8, W - 2 * M, 8.6, 2)

    noise = Image.effect_noise((W, H), 16).convert('L').point(lambda v: int(v * 0.012))
    grain = Image.merge('RGB', (noise, noise, noise))
    img = ImageChops.add(img, grain).filter(ImageFilter.GaussianBlur(0.2))
    img.save(out, format='PNG', optimize=True)
    return img


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else 'entry.png')
    img = render(out)
    print(f'wrote {out} ({out.stat().st_size} bytes, {img.size[0]}x{img.size[1]}, '
          f'{1 + len(SECONDARY) + sum(len(x[1]) for x in SECTIONS)} stories)')


if __name__ == '__main__':
    main()
