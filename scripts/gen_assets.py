"""Build the profile README's SVGs.

Every piece of text is shaped with HarfBuzz and turned into outlines, so the
SVGs look identical everywhere (GitHub renders README images with no web
fonts). Each asset is written twice, for GitHub's light and dark themes.

    uv run --with uharfbuzz --with fonttools python scripts/gen_assets.py

Fonts (all SIL Open Font License): Instrument Serif, JetBrains Mono.
"""

from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "scripts" / "fonts"
OUT = ROOT / "assets"
W = 1000  # canvas width; GitHub scales it to the column

THEMES = {
    "dark": dict(fg="#e6edf3", muted="#8b949e", faint="#30363d", accent="#ff5c35"),
    "light": dict(fg="#1f2328", muted="#656d76", faint="#d8dee4", accent="#e8492a"),
}


class Face:
    def __init__(self, file, key):
        self.key = key
        path = FONTS / file
        self.tt = TTFont(path)
        self.glyphs = self.tt.getGlyphSet()
        self.upem = self.tt["head"].unitsPerEm
        blob = hb.Blob.from_file_path(str(path))
        self.hb = hb.Font(hb.Face(blob))

    def shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": True})
        return buf.glyph_infos, buf.glyph_positions

    def width(self, text, size, track=0.0):
        _, pos = self.shape(text)
        return sum(p.x_advance for p in pos) * size / self.upem + track * (len(pos) - 1)

    def glyph_paths(self, text, size, x, y, track=0.0):
        """Yield one <use> per glyph, laid out from (x, y) baseline.

        Each glyph outline is stored once in DEFS and reused, which keeps the
        files small even though every letter is a path.
        """
        infos, pos = self.shape(text)
        s = size / self.upem
        for info, p in zip(infos, pos):
            key = f"{self.key}{info.codepoint}-{size:g}".replace(".", "_")
            if key not in DEFS:
                pen = SVGPathPen(self.glyphs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
                self.glyphs[self.tt.getGlyphName(info.codepoint)].draw(
                    TransformPen(pen, (s, 0, 0, -s, 0, 0)))
                DEFS[key] = pen.getCommands()
            if DEFS[key]:
                gx, gy = x + p.x_offset * s, y - p.y_offset * s
                yield f'<use href="#{key}" x="{gx:.1f}" y="{gy:.1f}"/>'
            x += p.x_advance * s + track

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

STYLE = """<style>
.a{animation:u 1.1s cubic-bezier(.16,1,.3,1) backwards}
.ln{transform-origin:0 0;animation:l 1.6s cubic-bezier(.16,1,.3,1) backwards}
.dot{animation:p 2.4s ease-in-out infinite}
@keyframes u{from{opacity:0;transform:translateY(10px)}}
@keyframes l{from{transform:scaleX(0)}}
@keyframes p{50%{opacity:.15}}
@media (prefers-reduced-motion:reduce){.a,.ln,.dot{animation:none}}
</style>"""


def svg(h, body, label):
    defs = "".join(f'<path id="{k}" d="{d}"/>' for k, d in DEFS.items() if d)
    DEFS.clear()
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
        f'viewBox="0 0 {W} {h}" role="img" aria-label="{label}">{STYLE}<defs>{defs}</defs>{body}</svg>\n'
    )


def p(d, fill, cls="a", delay=0.0):
    return f'<g class="{cls}" style="animation-delay:{delay:.2f}s" fill="{fill}">{d}</g>'


def rule(y, color, delay=0.0, x1=0, x2=W):
    return (
        f'<line class="ln" style="animation-delay:{delay:.2f}s" x1="{x1}" y1="{y}" '
        f'x2="{x2}" y2="{y}" stroke="{color}" stroke-width="1"/>'
    )


def label(text, x, y, fill, delay, anchor="start"):
    return p(MONO.path(text, 14, x, y, track=2.2, anchor=anchor), fill, delay=delay)


# ── hero ────────────────────────────────────────────────────────────────
STATS = [
    ("NATIONAL HACKATHON", "2nd of 1,460"),
    ("MERGED UPSTREAM", "7 PRs"),
    ("LARGEST REPO", "70k stars"),
    ("ON YOUTUBE", "33.5K"),
]


def hero(t):
    b = []
    b.append(label("AI ENGINEER  /  IIT JODHPUR", 0, 26, t["muted"], 0.0))
    status = "CURRENTLY SHIPPING AT KAYA AI"
    sw = MONO.width(status, 14, 2.2)
    b.append(label(status, W, 26, t["muted"], 0.1, anchor="end"))
    b.append(
        f'<circle class="dot" cx="{W - sw - 16}" cy="21" r="4" fill="{t["accent"]}"/>'
    )
    b.append(rule(46, t["faint"], 0.1))

    # The name, glyph by glyph, regular then italic.
    size, base = 136, 190
    first, last = "Aeshvarya", " Awasthi"
    wf = SERIF.width(first, size)
    i = 0
    for face, text, x in ((SERIF, first, 0), (ITALIC, last, wf)):
        for d in face.glyph_paths(text, size, x - 4, base):
            b.append(p(d, t["fg"], delay=0.25 + i * 0.045))
            i += 1

    b.append(p(ITALIC.path("I build systems that ship.", 36, 0, 252), t["muted"], delay=0.9))
    b.append(rule(300, t["faint"], 1.0))

    col = W / len(STATS)
    for n, (k, v) in enumerate(STATS):
        x = n * col
        b.append(label(k, x, 334, t["muted"], 1.15 + n * 0.08))
        b.append(p(SERIF.path(v, 50, x - 1, 390), t["fg"], delay=1.2 + n * 0.08))
    return svg(410, "".join(b), "Aeshvarya Awasthi. AI engineer, IIT Jodhpur. I build systems that ship.")


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


def header(t, num, title, right=""):
    b = [label(f"({num:02d})", 0, 26, t["accent"], 0.0), label(title, 64, 26, t["fg"], 0.05)]
    if right:
        b.append(label(right, W, 26, t["muted"], 0.1, anchor="end"))
    b.append(rule(46, t["faint"], 0.1))
    return b


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
    return svg(h, "".join(b), "Record: 2nd of 1,460 at the Kaya AI IIT India Hackathon; engineering intern at Kaya AI; 7 PRs merged upstream; co-founder of Mender; backend lead on PulseBoard; 33.5K YouTube subscribers; IIT Jodhpur.")


def section(t, num, title, right=""):
    return svg(56, "".join(header(t, num, title, right)), title.title())


def footer(t):
    b = [rule(8, t["faint"])]
    b.append(label("AESHVARYA AWASTHI  ·  2026", 0, 52, t["muted"], 0.2))
    b.append(p(ITALIC.path("Outputs over consumption.", 32, W, 58, anchor="end"), t["fg"], delay=0.3))
    return svg(72, "".join(b), "Outputs over consumption.")


ASSETS = {
    "hero": hero,
    "record": record,
    "oss": lambda t: section(t, 2, "OPEN SOURCE", "7 MERGED  ·  2 IN REVIEW"),
    "work": lambda t: section(t, 3, "WORK", "SELECTED"),
    "links": lambda t: section(t, 4, "ELSEWHERE"),
    "footer": footer,
}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, build in ASSETS.items():
        for theme, colors in THEMES.items():
            f = OUT / f"{name}-{theme}.svg"
            f.write_text(build(colors))
            print(f"{f.relative_to(ROOT)}  {f.stat().st_size / 1024:.1f} KB")
