"""Build the profile README's SVGs.

Every piece of text is shaped with HarfBuzz and turned into outlines, so the
SVGs look identical everywhere (GitHub renders README images with no web
fonts). Each asset is written twice, for GitHub's light and dark themes.

    uv run --with uharfbuzz --with fonttools python scripts/gen_assets.py

The contribution grid reads live data from GitHub's GraphQL API, using
GITHUB_TOKEN if set, else `gh auth token`. A daily workflow re-runs this.

Every animation only plays the entrance (or loops on top of a resting
state), so a renderer that ignores CSS animation still shows the full page.

Fonts (all SIL Open Font License): Instrument Serif, JetBrains Mono.
"""

import json
import math
import os
import subprocess
import urllib.request
from datetime import date
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "scripts" / "fonts"
OUT = ROOT / "assets"
USER = "Aeshvarya"
W = 1000  # canvas width; GitHub scales it to the column

THEMES = {
    "dark": dict(fg="#e6edf3", muted="#8b949e", faint="#30363d", empty="#21262d", accent="#ff5c35"),
    "light": dict(fg="#1f2328", muted="#656d76", faint="#d8dee4", empty="#ebeef1", accent="#e8492a"),
}

EASE = "cubic-bezier(.16,1,.3,1)"
SINE = "cubic-bezier(.37,0,.63,1)"


def num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".").replace("-0", "0") if abs(v) >= 0.05 else "0"


class Face:
    def __init__(self, file, key):
        self.key = key
        path = FONTS / file
        self.tt = TTFont(path)
        self.glyphs = self.tt.getGlyphSet()
        self.upem = self.tt["head"].unitsPerEm
        self.hb = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))

    def shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": True})
        return list(zip(buf.glyph_infos, buf.glyph_positions))

    def width(self, text, size, track=0.0):
        g = self.shape(text)
        return sum(p.x_advance for _, p in g) * size / self.upem + track * (len(g) - 1)

    def ref(self, gid, size):
        """Store a glyph outline once in DEFS; return its id (None if blank)."""
        key = f"{self.key}{gid}-{size:g}".replace(".", "_")
        if key not in DEFS:
            pen = SVGPathPen(self.glyphs, ntos=num)
            s = size / self.upem
            self.glyphs[self.tt.getGlyphName(gid)].draw(TransformPen(pen, (s, 0, 0, -s, 0, 0)))
            DEFS[key] = pen.getCommands()
        return key if DEFS[key] else None

    def layout(self, text, size, x, y, track=0.0):
        """Yield (glyph id, x, y, advance) per glyph."""
        s = size / self.upem
        for info, p in self.shape(text):
            yield info.codepoint, x + p.x_offset * s, y - p.y_offset * s, p.x_advance * s
            x += p.x_advance * s + track

    def glyph_paths(self, text, size, x, y, track=0.0):
        for gid, gx, gy, _ in self.layout(text, size, x, y, track):
            k = self.ref(gid, size)
            if k:
                yield f'<use href="#{k}" x="{num(gx)}" y="{num(gy)}"/>'

    def path(self, text, size, x, y, track=0.0, anchor="start"):
        if anchor == "end":
            x -= self.width(text, size, track)
        elif anchor == "middle":
            x -= self.width(text, size, track) / 2
        return "".join(self.glyph_paths(text, size, x, y, track))


DEFS = {}
SERIF = Face("InstrumentSerif-Regular.ttf", "s")
ITALIC = Face("InstrumentSerif-Italic.ttf", "i")
MONO = Face("JetBrainsMono-Regular.ttf", "m")

BASE_CSS = f"""
.a{{animation:u 1.1s {EASE} backwards}}
.ln{{transform-origin:0 0;animation:l 1.6s {EASE} backwards}}
.dot{{animation:p 2.4s ease-in-out infinite}}
@keyframes u{{from{{opacity:0;transform:translateY(10px)}}}}
@keyframes l{{from{{transform:scaleX(0)}}}}
@keyframes p{{50%{{opacity:.15}}}}
"""
REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def svg(h, body, label, css=""):
    defs = "".join(f'<path id="{k}" pathLength="1" d="{d}"/>' for k, d in DEFS.items() if d)
    DEFS.clear()
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
        f'viewBox="0 0 {W} {h}" role="img" aria-label="{label}">'
        f"<style>{BASE_CSS}{css}{REDUCED}</style><defs>{defs}</defs>{body}</svg>\n"
    )


def p(d, fill, cls="a", delay=0.0, extra=""):
    return f'<g class="{cls}" style="animation-delay:{delay:.2f}s" fill="{fill}"{extra}>{d}</g>'


def rule(y, color, delay=0.0, x1=0, x2=W):
    return (
        f'<line class="ln" style="animation-delay:{delay:.2f}s" x1="{x1}" y1="{y}" '
        f'x2="{x2}" y2="{y}" stroke="{color}" stroke-width="1"/>'
    )


def label(text, x, y, fill, delay, anchor="start", size=14):
    return p(MONO.path(text, size, x, y, track=2.2, anchor=anchor), fill, delay=delay)


def header(t, num_, title, right=""):
    b = [label(f"({num_:02d})", 0, 26, t["accent"], 0.0), label(title, 64, 26, t["fg"], 0.05)]
    if right:
        b.append(label(right, W, 26, t["muted"], 0.1, anchor="end"))
    b.append(rule(46, t["faint"], 0.1))
    return b


# ── hero ────────────────────────────────────────────────────────────────
STATS = [
    ("NATIONAL HACKATHON", "2nd of 1,460"),
    ("MERGED UPSTREAM", "7 PRs"),
    ("LARGEST REPO", "70k stars"),
    ("ON YOUTUBE", "33.5K"),
]

GLOBE = dict(cx=808, cy=236, r=156, tilt=math.radians(22), period=28.0)
HOME = (26.29, 73.02)  # Jodhpur


def globe(t):
    """A dot sphere spinning about its axis, drawn with CSS only.

    Each dot on a latitude ring moves as x = r·cos(θ), y = c + a·sin(θ): two
    sine-eased oscillations a quarter-period apart. Depth rides on the y
    oscillation as opacity and scale. Each dot carries its resting position
    inline, so a static renderer still draws the sphere.
    """
    g, css = [], []
    R, tau, T = GLOBE["r"], GLOBE["tilt"], GLOBE["period"]

    def depth(phi, s):  # s = sin θ ∈ [-1, 1]
        z = R * math.sin(phi) * math.sin(tau) + R * math.cos(phi) * s * math.cos(tau)
        dn = (z / R + 1) / 2
        return 0.06 + 0.94 * dn ** 1.6, 0.45 + 0.75 * dn

    def ring_css(k, phi):
        r = R * math.cos(phi)
        c = -R * math.sin(phi) * math.cos(tau)
        a = r * math.sin(tau)
        ohi, shi = depth(phi, 1)
        olo, slo = depth(phi, -1)
        css.append(
            f".x{k}{{animation:x{k} {T / 2:g}s {SINE} infinite alternate}}"
            f".y{k}{{animation:y{k} {T / 2:g}s {SINE} infinite alternate}}"
            f"@keyframes x{k}{{from{{transform:translateX({num(r)}px)}}to{{transform:translateX({num(-r)}px)}}}}"
            f"@keyframes y{k}{{from{{transform:translateY({num(c + a)}px) scale({shi:.2f});opacity:{ohi:.2f}}}"
            f"to{{transform:translateY({num(c - a)}px) scale({slo:.2f});opacity:{olo:.2f}}}}}"
        )
        return r, c, a

    def dot(k, phi, theta, inner):
        r, c, a = RINGS[k]
        dx = -((theta % (2 * math.pi)) / (2 * math.pi)) * T
        dy = -(((theta - math.pi / 2) % (2 * math.pi)) / (2 * math.pi)) * T
        o, s = depth(phi, math.sin(theta))
        return (
            f'<g class="x{k}" style="transform:translateX({num(r * math.cos(theta))}px);animation-delay:{dx:.2f}s">'
            f'<g class="y{k}" style="transform:translateY({num(c + a * math.sin(theta))}px) scale({s:.2f});'
            f'opacity:{o:.2f};animation-delay:{dy:.2f}s">{inner}</g></g>'
        )

    RINGS = {}
    lats = list(range(-72, 73, 12))
    for k, lat in enumerate(lats):
        phi = math.radians(lat)
        RINGS[k] = ring_css(k, phi)
        n = max(6, round(34 * math.cos(phi)))
        for j in range(n):
            theta = 2 * math.pi * j / n + (k % 2) * math.pi / n
            g.append(dot(k, phi, theta, '<circle r="2.1"/>'))

    # Home: its own ring at Jodhpur's latitude, one accent dot with a pulse.
    hk = len(lats)
    hphi = math.radians(HOME[0])
    RINGS[hk] = ring_css(hk, hphi)
    css.append(
        ".halo{animation:halo 2.4s ease-out infinite;transform-box:fill-box;transform-origin:center}"
        "@keyframes halo{from{transform:scale(1);opacity:.7}to{transform:scale(4.5);opacity:0}}"
    )
    home = (
        f'<circle r="7" fill="none" stroke="{t["accent"]}" stroke-width="1" class="halo"/>'
        f'<circle r="4" fill="{t["accent"]}"/>'
    )
    g.append(dot(hk, hphi, math.radians(HOME[1] - 20), home))

    cx, cy = GLOBE["cx"], GLOBE["cy"]
    body = (
        f'<g class="a" style="animation-delay:.6s;animation-duration:2.4s">'
        f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{t["faint"]}" stroke-width="1"/>'
        f'<g transform="translate({cx},{cy})" fill="{t["fg"]}">{"".join(g)}</g></g>'
    )
    cap = "26.29° N  73.02° E  JODHPUR"
    body += label(cap, cx, cy + R + 34, t["muted"], 1.0, anchor="middle", size=12)
    return body, "".join(css)


def odometer(t, value, x, base, size, delay):
    """Digits roll up into place; everything else fades in."""
    lh = size * 1.25
    out = []
    for i, (gid, gx, gy, adv) in enumerate(SERIF.layout(value, size, x, base)):
        ch = value[i] if i < len(value) else ""
        if ch.isdigit():
            d = int(ch)
            seq = [(d + 1 + n) % 10 for n in range(9)] + [d]
            strip = []
            for n, digit in enumerate(seq):
                (dg, _, _, dadv), = SERIF.layout(str(digit), size, 0, 0)
                k = SERIF.ref(dg, size)
                dy = base - (len(seq) - 1 - n) * lh
                strip.append(f'<use href="#{k}" x="{num(gx + (adv - dadv) / 2)}" y="{num(dy)}"/>')
            out.append(
                f'<g class="odo" style="animation-delay:{delay + i * 0.07:.2f}s">{"".join(strip)}</g>'
            )
        else:
            k = SERIF.ref(gid, size)
            if k:
                out.append(p(f'<use href="#{k}" x="{num(gx)}" y="{num(gy)}"/>', t["fg"], delay=delay + 0.3))
    return "".join(out), lh * 9


def hero(t):
    b = []
    b.append(label("AI ENGINEER  /  IIT JODHPUR", 0, 26, t["muted"], 0.0))
    status = "CURRENTLY SHIPPING AT KAYA AI"
    sw = MONO.width(status, 14, 2.2)
    b.append(label(status, W, 26, t["muted"], 0.1, anchor="end"))
    b.append(f'<circle class="dot" cx="{num(W - sw - 16)}" cy="21" r="4" fill="{t["accent"]}"/>')
    b.append(rule(46, t["faint"], 0.1))

    # The name draws itself as a hairline, then fills in, glyph by glyph.
    size = 172
    i = 0
    for face, text, base in ((SERIF, "Aeshvarya", 212), (ITALIC, "Awasthi", 356)):
        for d in face.glyph_paths(text, size, -6, base):
            b.append(p(d, t["fg"], cls="dw", delay=0.15 + i * 0.09,
                       extra=f' stroke="{t["fg"]}" stroke-width="1.1"'))
            i += 1

    b.append(p(ITALIC.path("I build systems that ship.", 34, 0, 420), t["muted"], delay=1.6))

    g, gcss = globe(t)
    b.append(g)

    b.append(rule(468, t["faint"], 1.2))
    col = W / len(STATS)
    rows = []
    roll = 0
    for n, (k, v) in enumerate(STATS):
        x = n * col
        b.append(label(k, x, 500, t["muted"], 1.3 + n * 0.08))
        o, roll = odometer(t, v, x - 1, 556, 50, 1.4 + n * 0.12)
        rows.append(o)
    b.append(f'<clipPath id="win"><rect x="0" y="512" width="{W}" height="58"/></clipPath>')
    b.append(f'<g clip-path="url(#win)" fill="{t["fg"]}">{"".join(rows)}</g>')

    css = gcss + (
        f".dw{{stroke-dasharray:1;stroke-opacity:0;animation:dw 2.8s cubic-bezier(.65,0,.35,1) backwards}}"
        f"@keyframes dw{{0%{{stroke-dashoffset:1;fill-opacity:0;stroke-opacity:1}}55%{{stroke-dashoffset:0;fill-opacity:0;stroke-opacity:1}}}}"
        f".odo{{animation:odo 1.9s cubic-bezier(.22,1,.36,1) backwards}}"
        f"@keyframes odo{{from{{transform:translateY({num(roll)}px)}}}}"
    )
    return svg(582, "".join(b), "Aeshvarya Awasthi. AI engineer, IIT Jodhpur. I build systems that ship. "
               "2nd of 1,460 at a national hackathon, 7 PRs merged upstream, 33.5K on YouTube.", css)


# ── record ──────────────────────────────────────────────────────────────
RECORD = [
    ("2nd of 1,460", "Kaya AI IIT India Hackathon",
     "Two of us against teams of four. Demoed live to judges from Google, OpenAI, Meta.", "AUG 2026"),
    ("Engineering intern", "Kaya AI",
     "Hired by the company that ran the hackathon. Foreman now ships in their product.", "SEP 2026 —"),
    ("7 PRs merged upstream", "open source",
     "Docling, IBM Research, 70k stars ×3  ·  PyBaMM, a GSoC org ×3  ·  Mesa ×1", "2026"),
    ("Co-founder", "Mender",
     "Keeps AI-built apps working and safe. Building in private.", "OCT 2026 —"),
    ("Backend lead", "PulseBoard",
     "Winter of Code, team of six. Email pipeline, Gemini extraction, OAuth, 2FA.", "JAN 2026"),
    ("33.5K subscribers", "Zack Vlogs",
     "Videos for JEE aspirants. One short crossed 11 million views.", "YOUTUBE"),
    ("B.Tech, Chemical Engineering", "IIT Jodhpur",
     "Second year. Building everything else on the side.", "2025 — 29"),
]


def record(t):
    b = header(t, 1, "RECORD", "2025 — NOW")
    top, row = 46, 106
    for n, (title, aside, detail, when) in enumerate(RECORD):
        y = top + n * row
        dl = 0.2 + n * 0.09
        b.append(label(f"{n + 1:02d}", 0, y + 52, t["muted"], dl))
        b.append(p(SERIF.path(title, 35, 62, y + 54), t["fg"], delay=dl))
        tw = SERIF.width(title, 35)
        b.append(p(ITALIC.path(aside, 35, 62 + tw + 12, y + 54), t["muted"], delay=dl))
        b.append(label(when, W, y + 52, t["muted"], dl, anchor="end"))
        b.append(p(MONO.path(detail, 16, 64, y + 85), t["muted"], delay=dl + 0.05))
        b.append(rule(y + row, t["faint"], dl + 0.1))
    h = top + len(RECORD) * row + 2
    return svg(h, "".join(b), "Record: 2nd of 1,460 at the Kaya AI IIT India Hackathon; engineering intern at "
               "Kaya AI; 7 PRs merged upstream; co-founder of Mender; backend lead on PulseBoard; 33.5K YouTube "
               "subscribers; IIT Jodhpur.")


# ── signal: the last year of contributions ──────────────────────────────
def contributions():
    token = os.environ.get("GITHUB_TOKEN") or subprocess.run(
        ["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    q = ('{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions '
         'weeks{contributionDays{contributionCount date weekday}}}}}}' % USER)
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=json.dumps({"query": q}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        cal = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], cal["weeks"]


def signal(t, total, weeks):
    counts = sorted(d["contributionCount"] for w in weeks for d in w["contributionDays"] if d["contributionCount"])
    cuts = [counts[int(len(counts) * f)] for f in (0.25, 0.5, 0.75)] if counts else [1, 2, 3]

    def level(c):
        return 0 if c == 0 else 1 + sum(c > x for x in cuts)

    radius = {0: 1.6, 1: 2.8, 2: 3.8, 3: 4.8, 4: 5.8}
    alpha = {0: 1, 1: 0.45, 2: 0.65, 3: 0.85, 4: 1}
    b = header(t, 2, "SIGNAL", f"{total:,} CONTRIBUTIONS  ·  LAST 12 MONTHS")
    cols = len(weeks)
    pitch = W / cols
    top = 74
    dots, last_month = [], None
    # A wave of accent light sweeps the year every 7 s, leaving a short tail.
    # Each level states its own resting colour so the tail ends on time.
    css = [".w{transform-box:fill-box;transform-origin:center}"]
    for lv in range(5):
        rest = f"fill:{t['empty'] if lv == 0 else t['fg']};opacity:{alpha[lv]};transform:none"
        css.append(
            f".l{lv}{{{rest};animation:w{lv} 7s ease-out infinite}}"
            f"@keyframes w{lv}{{0%,12%,100%{{{rest}}}"
            f"2.5%{{fill:{t['accent']};opacity:1;transform:scale({1.9 if lv == 0 else 1.5})}}}}"
        )
    for ci, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            ri = d["weekday"]
            lv = level(d["contributionCount"])
            cx, cy = ci * pitch + pitch / 2, top + ri * pitch + pitch / 2
            delay = 1.0 + ci * 0.05 + ri * 0.035
            dots.append(
                f'<circle class="w l{lv}" style="animation-delay:{delay:.2f}s" '
                f'cx="{num(cx)}" cy="{num(cy)}" r="{radius[lv]}"/>'
            )
        first = date.fromisoformat(wk["contributionDays"][0]["date"])
        if first.month != last_month and ci < cols - 2:
            if last_month is not None:
                dots.append(label(first.strftime("%b").upper(), ci * pitch + 4, top + 7 * pitch + 28,
                                  t["muted"], 0.4, size=12))
            last_month = first.month
    b.append(f'<g class="a" style="animation-delay:.2s">{"".join(dots)}</g>')
    return svg(top + 7 * pitch + 40, "".join(b),
               f"{total:,} GitHub contributions in the last 12 months.", "".join(css))


# ── marquee footer ──────────────────────────────────────────────────────
PHRASES = ["Outputs over consumption", "Systems that ship", "Built from IIT Jodhpur"]


def footer(t):
    size, base, gap = 76, 104, 46
    items, x = [], 0.0
    for ph in PHRASES:
        items.append(ITALIC.path(ph, size, x, base))
        x += ITALIC.width(ph, size) + gap
        items.append(f'<circle cx="{num(x)}" cy="{base - size * 0.22:.1f}" r="7" fill="{t["accent"]}"/>')
        x += gap
    copy_w = x
    copies = math.ceil(W / copy_w) + 1
    band = "".join(f'<g transform="translate({num(k * copy_w)},0)">{"".join(items)}</g>' for k in range(copies))
    css = (
        f".mq{{animation:mq {copy_w / 38:.1f}s linear infinite}}"
        f"@keyframes mq{{to{{transform:translateX({num(-copy_w)}px)}}}}"
    )
    b = [rule(8, t["faint"])]
    b.append(
        '<linearGradient id="fade"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".12" stop-color="#fff"/><stop offset=".88" stop-color="#fff"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<mask id="m"><rect width="{W}" height="140" fill="url(#fade)"/></mask>'
    )
    b.append(f'<g mask="url(#m)"><g class="mq" fill="{t["fg"]}">{band}</g></g>')
    b.append(rule(140, t["faint"], 0.2))
    b.append(label("AESHVARYA AWASTHI  ·  2026", 0, 172, t["muted"], 0.3, size=12))
    b.append(label("GITHUB.COM/AESHVARYA", W, 172, t["muted"], 0.3, anchor="end", size=12))
    return svg(184, "".join(b), "Outputs over consumption. Systems that ship. Built from IIT Jodhpur.", css)


def section(t, num_, title, right=""):
    return svg(56, "".join(header(t, num_, title, right)), title.title())


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    total, weeks = contributions()
    assets = {
        "hero": hero,
        "record": record,
        "signal": lambda t: signal(t, total, weeks),
        "oss": lambda t: section(t, 3, "OPEN SOURCE", "7 MERGED  ·  2 IN REVIEW"),
        "work": lambda t: section(t, 4, "WORK", "SELECTED"),
        "links": lambda t: section(t, 5, "ELSEWHERE"),
        "footer": footer,
    }
    for name, build in assets.items():
        for theme, colors in THEMES.items():
            f = OUT / f"{name}-{theme}.svg"
            f.write_text(build(colors))
            print(f"{f.relative_to(ROOT)}  {f.stat().st_size / 1024:.1f} KB")
