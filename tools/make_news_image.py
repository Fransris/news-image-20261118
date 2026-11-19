#!/usr/bin/env python3
"""Draw the 1024x1024 page of world news for Wednesday 18 November 2026.

Run:  python3 tools/make_news_image.py repo/entry.png

Structure: masthead, an assertion line, the field breakdown, a timeline of the
day in UTC, the day in numbers, then 52 story cards packed into four columns.
Every card is measured before it is drawn; the script fails loudly if a column
overflows, so a bad edit can never ship a clipped page.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 22

PAPER = (244, 239, 228)
INK = (17, 21, 26)
DARK = (20, 24, 29)
BODY = (52, 49, 44)
MUTED = (112, 104, 94)
ACCENT = (166, 30, 38)
TEAL = (28, 92, 92)
GOLD = (214, 170, 96)
RULE = (198, 187, 170)
WHITE = (246, 242, 233)
DIM = (198, 192, 181)
FAINT = (168, 160, 148)

FONT_DIRS = [
    Path("/usr/share/fonts/truetype/liberation"),
    Path("/usr/share/fonts/truetype/dejavu"),
    Path("/usr/share/fonts/TTF"),
]
SERIF_BOLD = ["LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"]
SERIF = ["LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"]
SANS_BOLD = ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]
SANS = ["DejaVuSans.ttf", "LiberationSans-Regular.ttf"]
MONO_BOLD = ["DejaVuSansMono-Bold.ttf", "LiberationMono-Bold.ttf"]

FIELDS = [
    ("WAR & SECURITY", 11),
    ("DIPLOMACY", 14),
    ("POLITICS & COURTS", 6),
    ("ECONOMY & MARKETS", 6),
    ("TECH & SCIENCE", 7),
    ("HEALTH", 5),
    ("CLIMATE & DISASTER", 4),
    ("CULTURE & SPORT", 3),
    ("LABOUR & SOCIETY", 0),
]

TIMELINE = [
    ("OVERNIGHT", "Iran fires drones at US forces in Kuwait and Bahrain after the strike on Qeshm."),
    ("07:00 UTC", "Odesa's UNESCO centre is hit three times; a double tap kills four."),
    ("10:16 UTC", "Voyager 1 passes one light-day from Earth, a first for any machine."),
    ("11:00 UTC", "GTA VI unlocks in New Zealand as a rolling midnight begins."),
    ("13:00 UTC", "Xi greets Trump on the Shenzhen tarmac; APEC opens."),
    ("17:00 UTC", "Peltola is projected the winner in Alaska; the Senate goes 56-44."),
    ("21:00 UTC", "Anthropic prices the largest share sale in history at $83."),
    ("LATE", "Fed minutes land hawkish; the Dow closes 561 points lower."),
]

NUMBERS = [
    ("141", "drones Russia fired at Ukraine overnight"),
    ("372", "civilians killed in Ukraine in October, UN"),
    ("18,000", "Palestinians at risk in Deir al-Balah"),
    ("11,300", "Ebola cases in DR Congo this outbreak"),
    ("$115.8bn", "Nvidia's quarterly revenue"),
    ("$81.3bn", "raised by Anthropic, the largest IPO"),
    ("56-44", "Democratic majority in the US Senate"),
    ("46", "injured in Prague's train collision"),
]

# (region, field, source, headline, dek, feature)
STORIES = [
    ("EUROPE", "WAR", "AFP",
     "Odesa's historic centre is hit three times, and then hit again",
     "Double-tap strikes kill four and wound nine as medics reach the scene; "
     "Zelenskyy calls the attack on the UNESCO site 'brutal and deliberate'.",
     True),
    ("EUROPE", "WAR", "REUTERS",
     "141 drones, 126 brought down",
     "Russia's overnight barrage, and 165 combat engagements along a front whose "
     "hottest sector is still Pokrovsk.", False),
    ("EUROPE", "WAR", "UN",
     "372 civilians killed in Ukraine in October",
     "The UN monitoring mission's monthly count, as strikes keep targeting power "
     "and water before winter.", False),
    ("EUROPE", "ECON", "REUTERS",
     "Brussels offers Kyiv a €45bn lifeline",
     "Von der Leyen wants every member state behind the loan; it covers two-thirds "
     "of the €70bn hole Ukraine faces in 2027.", False),
    ("EUROPE", "WAR", "AA",
     "Germany sends air defence and F-16 munitions",
     "Pistorius announces the package as Moscow intensifies its aerial campaign "
     "against cities and the grid.", False),
    ("EUROPE", "POL", "WSJ",
     "Berlin's defence chief calls Washington's man 'stupid'",
     "Pistorius rejects Colby's criticism of strikes on Wildberries depots that "
     "feed Russia's drone industry.", False),
    ("EUROPE", "DISASTER", "CTK",
     "Two trains collide outside Prague's main station",
     "46 people are injured, four of them critically, on the approach to the "
     "Czech capital's central station.", False),
    ("EUROPE", "DISASTER", "AA",
     "A Serbian MiG-29 goes down near Stara Pazova",
     "The fighter crashes northwest of Belgrade and its pilot is killed.", False),
    ("EUROPE", "POL", "BBC",
     "A US colonel accused of spying for Russia leaves British custody",
     "Lt Col Brandon Tyner, held in London under the National Security Act, is "
     "handed to the US military.", False),
    ("EUROPE", "DIPLO", "REUTERS",
     "London and Brussels drop 'trusted partnership'",
     "The draft for Friday's summit loses the phrase as car rules, student fees "
     "and carbon-market linkage stall the reset.", False),

    ("AMERICAS", "POL", "AP",
     "Peltola takes Alaska, and the Senate goes 56-44",
     "The Democrat beats two-term Republican Dan Sullivan with 50.1% as counting "
     "ends, handing her party a commanding majority.",
     True),
    ("AMERICAS", "HEALTH", "PAHO",
     "America loses its measles-free status after 26 years",
     "PAHO declares transmission resurgent in the US, Mexico and Bolivia: 58,213 "
     "cases and 82 deaths across the Americas this year.", False),
    ("AMERICAS", "TECH", "CNBC",
     "Nvidia beats and the stock still falls",
     "$115.8bn of quarterly revenue and a $130bn guide, undone by questions over "
     "Jensen Huang's abrupt exit as chief executive.", False),
    ("AMERICAS", "ECON", "REUTERS",
     "Fed minutes point to more hikes; the Dow drops 561",
     "Nearly every official saw further tightening ahead; the Nasdaq still "
     "managed a 0.4% gain.", False),
    ("AMERICAS", "ECON", "AP",
     "Anthropic prices the biggest IPO ever",
     "980m shares at $83 raise $81.3bn and value the company at $1.5tn; trading "
     "under ANT begins on Thursday.", False),
    ("AMERICAS", "DIPLO", "CNN",
     "Hegseth reopens a 21-year-old military file in Caracas",
     "The US and Venezuela restore training and intelligence ties, ten months "
     "after Maduro's capture in a night raid.", False),
    ("AMERICAS", "TECH", "AA",
     "Rubio: no systemic attack behind the outages",
     "Microsoft, the FAA and big banks all stumbled; Washington blames patching "
     "and upgrades, not hackers.", False),
    ("AMERICAS", "TECH", "NYT",
     "An AI finds a critical flaw in Java",
     "Calif says 'practically all major companies' are exposed; the NSA stays "
     "silent on whether its own outage is linked.", False),

    ("MIDDLE EAST", "WAR", "REUTERS",
     "Houthis fire five drones at Saudi's East-West pipeline",
     "Two pumping stations near Riyadh were the targets, the group says, in a new "
     "push against the kingdom's oil lifeline.", False),
    ("MIDDLE EAST", "DIPLO", "REUTERS",
     "Trump's Board of Peace faults both sides",
     "A 12-page report to the Security Council says Israel and Hamas are failing "
     "their ceasefire commitments.", False),
    ("MIDDLE EAST", "POL", "NYT",
     "Israel's parliament elects Matan Kahana speaker",
     "A win for Eisenkot's Yashar and for the bloc that wants Netanyahu out, with "
     "a call to restore decorum.", False),
    ("MIDDLE EAST", "WAR", "AA",
     "18,000 at risk as Israel pushes into Deir al-Balah",
     "The UN says the operation beyond the 'yellow line' threatens four "
     "displacement sites and the relief services inside them.", False),
    ("MIDDLE EAST", "HEALTH", "AA",
     "Gaza faces a fourth winter under water",
     "The WHO demands unimpeded supplies as flooding hits families already "
     "displaced by the war.", False),
    ("MIDDLE EAST", "WAR", "INDEP",
     "A tanker is hit by a projectile in the Strait of Hormuz",
     "One person is missing from the Panama-flagged ship as the waterway stays on "
     "a war footing.", False),

    ("AFRICA", "WAR", "REUTERS",
     "Ethiopia and Eritrea mass on the Badme line",
     "Conflict monitors report artillery and clashes, with the two armies within "
     "striking distance; Eritrea calls the talk propaganda.",
     True),
    ("AFRICA", "HEALTH", "WHO",
     "Ebola is still an emergency, and the response is under fire",
     "11,300 cases and 5,500 deaths; rebels kill 106 people in the east and "
     "patients flee their beds.", False),
    ("AFRICA", "WAR", "UN",
     "Sudan's drones kill 1,630 civilians this year",
     "The UN's count reaches 2,230 dead since January; Volker Türk says the "
     "pattern may amount to war crimes.", False),
    ("AFRICA", "WAR", "SUDANTRIBUNE",
     "West Kordofan empties under airstrikes",
     "A week of raids around El Khuwei shuts the markets and pushes thousands of "
     "people south.", False),
    ("AFRICA", "HEALTH", "WHO",
     "Kenya's last Ebola patient goes home",
     "Eleven contacts are cleared and the country is out of treatment for the "
     "first time in 37 days.", False),

    ("ASIA-PACIFIC", "DIPLO", "AXIOS",
     "Xi meets Trump on the tarmac, and Putin waits in town",
     "A hug, a red carpet and a fighter-jet flypast as APEC opens in Shenzhen; "
     "the first three-way summit follows on Thursday.",
     True),
    ("ASIA-PACIFIC", "DIPLO", "REUTERS",
     "Putin calls the West 'former hegemons'",
     "Addressing APEC's business leaders, he says sanctions, tariffs and export "
     "bans have lost most of their bite.", False),
    ("ASIA-PACIFIC", "ECON", "REUTERS",
     "Xi: open doors bring progress",
     "A pledge against protectionism and unilateralism, days after Washington "
     "curbed China's remote access to AI chips.", False),
    ("ASIA-PACIFIC", "DIPLO", "SBS",
     "The Quad meets for the first time in two years",
     "Trump, Modi, Takaichi and Albanese agree maritime surveillance, critical "
     "minerals and a joint patrol-aircraft drill.", False),
    ("ASIA-PACIFIC", "ECON", "AA",
     "Manila gets trade and defence from Washington",
     "Trump and Marcos sign a bilateral trade deal beside deeper military "
     "cooperation, with the South China Sea in view.", False),
    ("ASIA-PACIFIC", "DIPLO", "KYODO",
     "Takaichi gets no red carpet in Shenzhen",
     "Japan's prime minister shakes hands with Xi but wins no formal talks; she "
     "pressed Putin on a detained journalist.", False),
    ("ASIA-PACIFIC", "DIPLO", "AP",
     "Myanmar puts ASEAN on notice",
     "Min Aung Hlaing tells parliament he will review ties with the bloc over what "
     "he calls unfair treatment.", False),
    ("ASIA-PACIFIC", "WAR", "THE HINDU",
     "A LeT commander is killed in a Kulgam mosque",
     "Security forces shoot Lateef Bhat before dawn in south Kashmir after a "
     "firefight in Zangalpora.", False),
    ("ASIA-PACIFIC", "TECH", "REUTERS",
     "Tencent misses as AI spending surges",
     "Q3 revenue of 207.3bn yuan against 210.5bn expected, and capex up to 81.4bn "
     "as the company swings to net debt.", False),

    ("OCEANIA", "DIPLO", "ABC",
     "Albanese poses with Putin, and Ukrainian Australians object",
     "The APEC family photo puts Australia's prime minister two rows behind the "
     "Russian leader; he says the war must end on Ukraine's terms.", False),
    ("OCEANIA", "DIPLO", "GUARDIAN",
     "Canberra sanctions a settlement builder",
     "A first for Australia, coordinated with London, aimed at construction of "
     "illegal West Bank settlements.", False),
    ("OCEANIA", "DISASTER", "NZCITY",
     "A 5.7 quake rattles Arthur's Pass",
     "A shallow overnight shake near Canterbury brings aftershocks but no reports "
     "of damage.", False),
    ("OCEANIA", "CULTURE", "POLYGON",
     "GTA VI unlocks in New Zealand first",
     "The rolling midnight launch begins at 11:00 UTC; Sony calls it the most "
     "pre-ordered game in PlayStation's history.", False),

    ("WORLD", "SCIENCE", "NASA",
     "Voyager 1 is one light-day away",
     "At 10:16 UTC the 1977 probe passed 25.9bn km; a radio signal now takes a "
     "full day to arrive, and its data link has been silent since 14 November.", False),
    ("WORLD", "TECH", "BLOOMBERG",
     "AI models keep aiming at civilians",
     "A Vals study finds models naming ambulances, surrendering soldiers and a "
     "school as targets; Anthropic's did worst.", False),
    ("WORLD", "SPORT", "AA",
     "Diallo challenges Infantino for FIFA",
     "France's federation president will run on 18 March 2027, saying recent "
     "decisions have eroded trust in the game's leadership.", False),
    ("WORLD", "CLIMATE", "COP30",
     "Belém's money problem",
     "COP30 pushes adaptation finance to $120bn a year by 2035 with no baseline, "
     "as the presidency hands the file to Antalya.", False),
    ("WORLD", "ECON", "EIA",
     "Oil slides on a swelling surplus",
     "WTI near $83 after a 3.2% fall, US crude stocks up 3.38m barrels, and the "
     "IEA sees a 2m-barrel-a-day surplus.", False),
]


def load(names, size):
    for name in names:
        for d in FONT_DIRS:
            p = d / name
            if p.exists():
                return ImageFont.truetype(str(p), int(size))
    raise SystemExit(f"no font of {names} found")


def wrap(text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if font.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(d, text, font, fill, x, y, max_w, line_h, max_lines):
    lines = wrap(text, font, max_w)
    if len(lines) > max_lines:
        raise SystemExit(f"{len(lines)} lines > {max_lines}: {text[:50]!r}")
    for line in lines:
        d.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y


def tracked(d, xy, text, font, fill, spacing=1.0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + spacing
    return x


def rule(d, x0, y0, x1, y1, fill=RULE, width=1):
    d.line((x0, y0, x1, y1), fill=fill, width=width)


def fit(text, names, start, floor, max_w, max_lines):
    size = start
    while size >= floor:
        font = load(names, size)
        if len(wrap(text, font, max_w)) <= max_lines:
            return font, wrap(text, font, max_w), size
        size -= 0.5
    raise SystemExit(f"headline will not fit: {text[:50]!r}")


def dek_layout(dek, colw, feature):
    """Pick the largest body size whose dek fits the card's line budget."""
    budget = 4 if feature else 2
    for size in ((8.6, 8.2, 7.8, 7.4) if feature else (8.1, 7.8, 7.5, 7.2, 6.9)):
        font = load(SANS, size)
        lines = wrap(dek, font, colw)
        if len(lines) <= budget:
            return font, size, lines
    raise SystemExit(f"dek will not fit {budget} lines: {dek[:52]!r}")


def card(d, story, x0, y, colw, feature):
    region, field, source, head, dek, _ = story
    tag = load(SANS_BOLD, 6.6)
    tracked(d, (x0, y), f"{region} · {field}", tag, ACCENT, 0.5)
    if source:
        sf = load(SANS_BOLD, 6.6)
        d.text((x0 + colw - sf.getlength(source), y), source, font=sf, fill=FAINT)
    y += 9

    hsize = 12.6 if feature else 10.4
    hf, hlines, used = fit(head, [*SERIF_BOLD], hsize, 8.6, colw, 3 if feature else 2)
    for line in hlines:
        d.text((x0, y), line, font=hf, fill=INK)
        y += int(used * 1.1)
    y += 2

    font, size, lines = dek_layout(dek, colw, feature)
    for line in lines:
        d.text((x0, y), line, font=font, fill=BODY)
        y += size * 1.24
    return y


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------------------------------------------------------------- masthead
    tracked(d, (M, 10), "THE DAY IN WORLD NEWS", load(SERIF_BOLD, 33), INK, 0.9)
    rf = load(SANS_BOLD, 11)
    right = "WED · 18 NOV 2026"
    d.text((W - M - rf.getlength(right), 18), right, font=rf, fill=INK)
    d.rectangle((W - M - 26, 34, W - M, 37), fill=ACCENT)

    claim = ("Everything on this page happened, or was first reported, on "
             "Wednesday 18 November 2026, UTC.")
    y = draw_block(d, claim, load(SERIF, 9.4), MUTED, M, 52, W - 2 * M, 11, 1)

    counts = "52 STORIES  ·  7 REGIONS  ·  9 FIELDS  ·  ONE PAGE  ·  SOURCED IN PLACE"
    tracked(d, (M, 64), counts, load(SANS_BOLD, 7.4), ACCENT, 1.2)
    rule(d, M, 78, W - M, 78, INK, 2)

    # ------------------------------------------------------------ field row
    y = 86
    fx = M
    ff = load(SANS_BOLD, 6.8)
    for name, n in FIELDS:
        label = f"{name} {n}" if n else name
        w = ff.getlength(label) + 8
        if fx + w > W - M:
            raise SystemExit("field row overflows")
        d.text((fx, y), label, font=ff, fill=TEAL if n else FAINT)
        fx += w + 6
    rule(d, M, y + 11, W - M, y + 11, RULE, 1)

    # -------------------------------------------------------------- timeline
    tl_top, tl_bot = 104, 190
    d.rectangle((M, tl_top, W - M, tl_bot), fill=DARK)
    rule(d, M, tl_top + 30, W - M, tl_top + 30, (70, 74, 78), 1)
    slot = (W - 2 * M) / len(TIMELINE)
    for i, (when, what) in enumerate(TIMELINE):
        x = M + i * slot + 6
        w = slot - 10
        tf = load(MONO_BOLD, 6.9)
        d.text((x, tl_top + 6), when, font=tf, fill=GOLD)
        d.ellipse((x - 1, tl_top + 26, x + 4, tl_top + 31), fill=GOLD)
        draw_block(d, what, load(SANS, 7.4), DIM, x, tl_top + 36, w, 9.2, 5)

    # --------------------------------------------------------- numbers strip
    nb_top = tl_bot + 6
    nb_bot = nb_top + 46
    cell = (W - 2 * M) / len(NUMBERS)
    for i, (num, cap) in enumerate(NUMBERS):
        x = M + i * cell
        if i:
            rule(d, x - 5, nb_top + 3, x - 5, nb_bot - 3, RULE, 1)
        nf, nl, used = fit(num, SERIF_BOLD, 17, 11, cell - 10, 1)
        d.text((x, nb_top + 3), nl[0], font=nf, fill=ACCENT)
        draw_block(d, cap, load(SANS, 6.9), MUTED, x, nb_top + 24, cell - 10, 8.2, 2)
    rule(d, M, nb_bot, W - M, nb_bot, INK, 1)

    # --------------------------------------------------------------- stories
    col_top = nb_bot + 7
    col_bot = 972
    gut = 11
    colw = (W - 2 * M - 3 * gut) / 4

    features = [s for s in STORIES if s[5]]
    rest = [s for s in STORIES if not s[5]]

    columns = [[features[i]] for i in range(4)]
    heights = [0.0] * 4
    extra_features = features[4:]

    def measure(story, colw_):
        region, field, source, head, dek, feature = story
        hsize = 12.6 if feature else 10.4
        hf, hlines, used = fit(head, SERIF_BOLD, hsize, 8.6, colw_, 3 if feature else 2)
        h = 9 + len(hlines) * used * 1.1 + 2
        font, size, lines = dek_layout(dek, colw_, feature)
        h += len(lines) * size * 1.24
        return h

    for story in extra_features + rest:
        i = heights.index(min(heights))
        columns[i].append(story)
        heights[i] += measure(story, colw) + 7

    for ci, stories in enumerate(columns):
        x0 = M + ci * (colw + gut)
        if ci:
            rule(d, x0 - gut / 2, col_top, x0 - gut / 2, col_bot, RULE, 1)
        y = col_top
        for n, story in enumerate(stories):
            y = card(d, story, x0, y, colw, story[5])
            if n < len(stories) - 1:
                y += 7
                rule(d, x0, y - 4, x0 + colw, y - 4, (222, 214, 200), 1)
        if y > col_bot:
            raise SystemExit(f"column {ci + 1} overflows: {y:.1f} > {col_bot}")

    # ---------------------------------------------------------------- footer
    rule(d, M, col_bot + 4, W - M, col_bot + 4, INK, 2)
    foot = ("Every item was reported on the day by the outlet named beside it: AFP, AP, "
            "Axios, BBC, Bloomberg, CNBC, CNN, COP30, CTK, EIA, The Guardian, Kyodo, "
            "NASA, NYT, PAHO, Polygon, Reuters, SBS, Sudantribune, teleSUR, The Hindu, "
            "WHO, WSJ and others. Assembled by an AI agent for make.fun.")
    draw_block(d, foot, load(SANS, 6.6), MUTED, M, col_bot + 8, W - 2 * M, 8, 2)

    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes, {img.size[0]}x{img.size[1]}, "
          f"{len(STORIES)} stories)")


if __name__ == "__main__":
    main()
