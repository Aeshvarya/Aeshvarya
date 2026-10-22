"""Generates the animated SVGs for the GitHub profile README."""
import sys
from pathlib import Path
from html import escape

OUT = Path(sys.argv[1])
SANS = "'Inter','Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'SFMono-Regular','Consolas','Liberation Mono',monospace"
GRAD = '<linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#a855f7"/><stop offset="55%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#3b82f6"/></linearGradient>'


def header(name, title):
    w = 48 + len(title) * 28 + 20
    (OUT / "brand" / f"h-{name}.svg").write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="66" viewBox="0 0 {w} 66" font-family="ui-monospace,SFMono-Regular,Menlo,'Liberation Mono',monospace">
  <defs>{GRAD}</defs>
  <rect x="24" y="14" width="9" height="40" rx="4.5" fill="url(#g)"/>
  <text x="48" y="46" font-size="34" letter-spacing="7" font-weight="700" fill="url(#g)">{escape(title)}</text>
</svg>
''')


# ─────────────────────────── HERO ───────────────────────────
def hero():
    W, H = 1200, 340
    pills = ["AI ENGINEER", "OPEN SOURCE", "HACKATHON FINALIST", "IIT JODHPUR"]
    px, pill_svg = 0, []
    widths = [len(p) * 9.2 + 40 for p in pills]
    total = sum(widths) + 14 * (len(pills) - 1)
    px = (W - total) / 2
    for i, (p, pw) in enumerate(zip(pills, widths)):
        d = 1.2 + i * 0.15
        pill_svg.append(f'''<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{d}s" dur="0.5s" fill="freeze"/>
    <rect x="{px:.1f}" y="262" width="{pw:.1f}" height="34" rx="17" fill="#8b5cf6" fill-opacity="0.10" stroke="#8b5cf6" stroke-opacity="0.55"/>
    <text x="{px + pw / 2:.1f}" y="284" text-anchor="middle" font-size="13" font-weight="800" letter-spacing="2" fill="#d8b4fe">{p}</text></g>''')
        px += pw + 14
    # starfield
    import random
    random.seed(7)
    stars = "".join(
        f'<circle cx="{random.uniform(0, W):.0f}" cy="{random.uniform(0, H):.0f}" r="{random.choice([0.8, 1, 1.4])}" fill="#c4b5fd">'
        f'<animate attributeName="opacity" values="0.1;0.9;0.1" dur="{random.uniform(2, 5):.1f}s" begin="{random.uniform(0, 3):.1f}s" repeatCount="indefinite"/></circle>'
        for _ in range(70))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#0b0716"/><stop offset="100%" stop-color="#060b18"/></linearGradient>
    <radialGradient id="o1"><stop offset="0%" stop-color="#8e2de2" stop-opacity="0.55"/><stop offset="100%" stop-color="#8e2de2" stop-opacity="0"/></radialGradient>
    <radialGradient id="o2"><stop offset="0%" stop-color="#3b82f6" stop-opacity="0.45"/><stop offset="100%" stop-color="#3b82f6" stop-opacity="0"/></radialGradient>
    <linearGradient id="name" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1200" y2="0" spreadMethod="reflect">
      <stop offset="0%" stop-color="#c084fc"/><stop offset="35%" stop-color="#ffffff"/><stop offset="50%" stop-color="#a78bfa"/><stop offset="75%" stop-color="#60a5fa"/><stop offset="100%" stop-color="#c084fc"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="0 0;1200 0" dur="6s" repeatCount="indefinite"/>
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#8b5cf6" stroke-opacity="0.07"/></pattern>
    <linearGradient id="scan" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#8b5cf6" stop-opacity="0"/><stop offset="50%" stop-color="#a78bfa" stop-opacity="0.9"/><stop offset="100%" stop-color="#3b82f6" stop-opacity="0"/></linearGradient>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#grid)"/>
    <circle cx="220" cy="80" r="260" fill="url(#o1)"><animate attributeName="cx" values="220;320;220" dur="14s" repeatCount="indefinite"/><animate attributeName="cy" values="80;140;80" dur="11s" repeatCount="indefinite"/></circle>
    <circle cx="1000" cy="280" r="280" fill="url(#o2)"><animate attributeName="cx" values="1000;880;1000" dur="12s" repeatCount="indefinite"/><animate attributeName="cy" values="280;200;280" dur="15s" repeatCount="indefinite"/></circle>
    {stars}
    <rect x="-400" y="0" width="400" height="2" fill="url(#scan)"><animate attributeName="x" values="-400;1200" dur="3.5s" repeatCount="indefinite"/></rect>
    <rect x="1200" y="{H - 2}" width="400" height="2" fill="url(#scan)"><animate attributeName="x" values="1200;-400" dur="3.5s" repeatCount="indefinite"/></rect>
  </g>
  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="22" fill="none" stroke="#8b5cf6" stroke-opacity="0.35" stroke-width="1.5"/>
  <g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="0.1s" dur="0.6s" fill="freeze"/>
    <text x="{W / 2}" y="78" text-anchor="middle" font-size="15" font-weight="800" letter-spacing="9" fill="#a78bfa">HEY, I'M</text>
  </g>
  <g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="0.3s" dur="0.8s" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate" from="0 18" to="0 0" begin="0.3s" dur="0.8s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>
    <text x="{W / 2}" y="168" text-anchor="middle" font-size="96" font-weight="900" letter-spacing="-2" fill="url(#name)">AESHVARYA AWASTHI</text>
  </g>
  <g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="0.8s" dur="0.6s" fill="freeze"/>
    <text x="{W / 2}" y="222" text-anchor="middle" font-size="24" font-weight="700" fill="#e6edf3">I build systems that ship <tspan fill="#a78bfa">—</tspan> and win rooms.</text>
  </g>
  {"".join(pill_svg)}
</svg>
'''
    (OUT / "hero.svg").write_text(svg)


# ─────────────────────────── COUNT-UP STATS ───────────────────────────
def stats():
    # (prefix, target, suffix, label, sub)
    cards = [
        ("#", 2, "", "OUT OF 1,460", "Kaya AI national hackathon"),
        ("₹", 100000, "", "PRIZE MONEY", "won live in front of the judges"),
        ("", 4, "", "UPSTREAM MERGES", "Docling ×3 · PyBaMM ×1"),
        ("", 69, "K★", "BIGGEST REPO MERGED INTO", "Docling by IBM Research"),
        ("", 1165, "", "CONTRIBUTIONS", "in the last 12 months"),
        ("$", 300, "/mo", "PAID INTERNSHIP", "US startup, hired in 2nd year"),
    ]
    W, CW, CH, GAP = 1200, 373, 150, 30
    rows = []
    frames = 26
    for i, (pre, tgt, suf, label, sub) in enumerate(cards):
        col, row = i % 3, i // 3
        x, y = col * (CW + GAP) + (W - 3 * CW - 2 * GAP) / 2, row * (CH + GAP) + 5
        start = 0.3 + i * 0.18
        g = [f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{start:.2f}s" dur="0.4s" fill="freeze"/>',
             f'<animateTransform attributeName="transform" type="translate" from="0 14" to="0 0" begin="{start:.2f}s" dur="0.5s" fill="freeze"/>',
             f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="18" fill="#0d1117" stroke="url(#g)" stroke-opacity="0.6" stroke-width="1.5"/>',
             f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="18" fill="url(#glow)" opacity="0.6"><animate attributeName="opacity" values="0.25;0.7;0.25" dur="4s" begin="{i * 0.6:.1f}s" repeatCount="indefinite"/></rect>',
             f'<rect x="{x + 24}" y="{y + 26}" width="5" height="44" rx="2.5" fill="url(#g)"/>']
        # count-up frames, ease-out cubic
        dt = 1.4 / frames
        for k in range(frames + 1):
            t = k / frames
            v = round(tgt * (1 - (1 - t) ** 3))
            txt = f"{pre}{v:,}{suf}" if tgt >= 1000 or pre == "₹" else f"{pre}{v}{suf}"
            if pre == "₹":  # Indian digit grouping: 1,00,000
                d = str(v); head, tail = d[:-3], d[-3:]
                groups = []
                while len(head) > 2:
                    groups.insert(0, head[-2:]); head = head[:-2]
                txt = "₹" + ",".join(([head] if head else []) + groups + [tail]) if len(d) > 3 else f"₹{v}"
            b = start + 0.25 + k * dt
            hide = "" if k == frames else f'<set attributeName="visibility" to="hidden" begin="{b + dt:.3f}s"/>'
            g.append(f'<text x="{x + 44}" y="{y + 68}" font-size="50" font-weight="900" fill="url(#g)" visibility="hidden">{escape(txt)}'
                     f'<set attributeName="visibility" to="visible" begin="{b:.3f}s"/>{hide}</text>')
        g.append(f'<text x="{x + 46}" y="{y + 102}" font-size="14" font-weight="800" letter-spacing="2.5" fill="#e6edf3">{escape(label)}</text>')
        g.append(f'<text x="{x + 46}" y="{y + 126}" font-size="14" font-weight="500" fill="#8b949e">{escape(sub)}</text>')
        g.append("</g>")
        rows.append("\n  ".join(g))
    H = 2 * CH + GAP + 10
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">
  <defs>{GRAD}
    <radialGradient id="glow" cx="0.15" cy="0.2" r="0.9"><stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.22"/><stop offset="100%" stop-color="#8b5cf6" stop-opacity="0"/></radialGradient>
  </defs>
  {"".join(rows)}
</svg>
'''
    (OUT / "stats.svg").write_text(svg)


# ─────────────────────────── TIMELINE ───────────────────────────
def timeline():
    events = [
        ("AUG '25", "IIT Jodhpur", "B.Tech, Chemical Eng."),
        ("JAN '26", "PulseBoard", "Backend lead, team of 6"),
        ("AUG '26", "2nd / 1,460", "Kaya AI national final"),
        ("SEP '26", "Hired", "Paid intern, Kaya AI"),
        ("OCT '26", "Docling merge", "First upstream PR in"),
        ("OCT '26", "PyBaMM merge", "GSoC org, merged"),
        ("OCT '26", "Mender", "Co-founded a startup"),
        ("NEXT", "GSoC 2027", "Loading..."),
    ]
    W, H, Y = 1200, 300, 150
    n = len(events)
    xs = [80 + i * (W - 160) / (n - 1) for i in range(n)]
    draw = 3.2
    parts = [f'<line x1="{xs[0]}" y1="{Y}" x2="{xs[-1]}" y2="{Y}" stroke="#232b36" stroke-width="3" stroke-linecap="round"/>',
             f'<line x1="{xs[0]}" y1="{Y}" x2="{xs[-1]}" y2="{Y}" stroke="url(#g)" stroke-width="3" stroke-linecap="round" stroke-dasharray="{xs[-1] - xs[0]:.0f}" stroke-dashoffset="{xs[-1] - xs[0]:.0f}">'
             f'<animate attributeName="stroke-dashoffset" from="{xs[-1] - xs[0]:.0f}" to="0" dur="{draw}s" begin="0.2s" fill="freeze"/></line>']
    for i, (x, (date, title, sub)) in enumerate(zip(xs, events)):
        t = 0.2 + draw * i / (n - 1)
        up = i % 2 == 0
        last = i == n - 1
        ty = Y - 92 if up else Y + 52
        stem = f'<line x1="{x:.1f}" y1="{Y}" x2="{x:.1f}" y2="{Y - 40 if up else Y + 30}" stroke="#8b5cf6" stroke-opacity="0.5" stroke-width="1.5" stroke-dasharray="3 3"/>'
        node_fill = "#0d1117" if last else "url(#g)"
        pulse = (f'<circle cx="{x:.1f}" cy="{Y}" r="9" fill="none" stroke="#a78bfa" stroke-width="2">'
                 f'<animate attributeName="r" values="9;22" dur="1.8s" begin="{t + 0.4:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0.9;0" dur="1.8s" begin="{t + 0.4:.2f}s" repeatCount="indefinite"/></circle>') if i in (2, 6, 7) else ""
        parts.append(f'''<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="0.35s" fill="freeze"/>
    {stem}{pulse}
    <circle cx="{x:.1f}" cy="{Y}" r="9" fill="{node_fill}" stroke="#c4b5fd" stroke-width="2"{' stroke-dasharray="3 2"' if last else ''}/>
    <text x="{x:.1f}" y="{ty}" text-anchor="middle" font-size="12" font-weight="800" letter-spacing="2" fill="#a78bfa">{date}</text>
    <text x="{x:.1f}" y="{ty + 22}" text-anchor="middle" font-size="17" font-weight="900" fill="#e6edf3">{escape(title)}</text>
    <text x="{x:.1f}" y="{ty + 41}" text-anchor="middle" font-size="12.5" font-weight="500" fill="#8b949e">{escape(sub)}</text></g>''')
        if up:
            pass
    # keep text inside bounds for upper labels: shift them up so 3 lines fit above the line
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}">
  <defs>{GRAD}</defs>
  {"".join(parts)}
</svg>
'''
    (OUT / "timeline.svg").write_text(svg)


# ─────────────────────────── CODE CARD ───────────────────────────
C = dict(kw="#c792ea", cls="#ffcb6b", pun="#89ddff", fn="#82aaff", slf="#f78c6c", txt="#b9c2d0", s="#c3e88d")


def code():
    S, P, F, K, T, Q = "slf", "pun", "fn", "kw", "txt", "s"
    def attr(name, pad, val):
        return [(T, "        "), (S, "self"), (P, "."), (T, name), (T, " " * pad), (P, "="), (T, " "), (Q, f'"{val}"')]
    def item(key, pad, val):
        return [(T, "            "), (Q, f'"{key}"'), (P, ":"), (T, " " * pad), (Q, f'"{val}"'), (P, ",")]
    lines = [
        [(K, "class"), (T, " "), ("cls", "Aeshvarya"), (P, ":")],
        [(T, "    "), (K, "def"), (T, " "), (F, "__init__"), (P, "("), (S, "self"), (P, "):")],
        attr("base", 4, "IIT Jodhpur · B.Tech '29"),
        attr("role", 4, "AI engineer who ships"),
        attr("day_job", 1, "Engineering intern @ Kaya AI"),
        attr("startup", 1, "Mender (co-founder)"),
        [],
        [(T, "    "), (K, "def"), (T, " "), (F, "trophies"), (P, "("), (S, "self"), (P, "):")],
        [(T, "        "), (K, "return"), (T, " "), (P, "{")],
        item("hackathon", 3, "2nd / 1,460 · Kaya AI"),
        item("open_source", 1, "Docling ×3 · PyBaMM"),
        item("shipped", 5, "Foreman · PulseBoard"),
        [(T, "        "), (P, "}")],
        [],
        [(T, "    "), (K, "def"), (T, " "), (F, "philosophy"), (P, "("), (S, "self"), (P, "):")],
        [(T, "        "), (K, "return"), (T, " "), (Q, '"Outputs > Consumption"')],
    ]
    CW, LH, Y0, X0 = 9.0, 23.25, 67.0, 26
    per_char, pause = 0.042, 0.09
    # timeline: each non-empty line types after the previous one finishes
    t, sched = 0.4, []
    for ln in lines:
        txt = "".join(s for _, s in ln)
        lead = len(txt) - len(txt.lstrip(" "))
        n = len(txt)
        if n == 0:
            sched.append(None); t += pause; continue
        start = t
        t0 = t + 0  # leading spaces appear instantly
        end = t0 + (n - lead) * per_char
        sched.append((start, end, lead * CW, n * CW))
        t = end + pause
    hold = 4.0
    total = t + hold
    def kt(x):
        return f"{x / total:.4f}"
    clips, texts = [], []
    caret_kt, caret_x, caret_y = ["0"], [str(X0)], [f"{Y0 - 12:.1f}"]
    for i, (ln, sc) in enumerate(zip(lines, sched)):
        y = Y0 + i * LH
        if sc is None:
            continue
        s, e, lw, w = sc
        clips.append(f'<clipPath id="cl{i}"><rect x="{X0}" y="{y - 15:.1f}" height="21" width="0"><animate attributeName="width" dur="{total:.2f}s" repeatCount="indefinite" '
                     f'keyTimes="0;{kt(s)};{kt(s + 0.01)};{kt(e)};0.995;1" values="0;0;{lw:.1f};{w:.1f};{w:.1f};0"/></rect></clipPath>')
        spans = "".join(f'<tspan fill="{C[c]}" xml:space="preserve">{escape(seg)}</tspan>' for c, seg in ln)
        texts.append(f'<text x="{X0}" y="{y:.1f}" clip-path="url(#cl{i})" xml:space="preserve">{spans}</text>')
        caret_kt += [kt(s), kt(e)]
        caret_x += [f"{X0 + lw:.1f}", f"{X0 + w:.1f}"]
        caret_y += [f"{y - 12:.1f}", f"{y - 12:.1f}"]
    caret_kt.append("1"); caret_x.append(str(X0)); caret_y.append(f"{Y0 - 12:.1f}")
    # discrete jumps between lines: use linear but keyTimes are close enough
    H = int(Y0 + len(lines) * LH + 12)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="655" height="{H}" viewBox="0 0 655 {H}" font-family="{MONO}" font-size="15">
  <defs>
{chr(10).join(clips)}
  </defs>
  <rect x="0.5" y="0.5" width="654" height="{H - 1}" rx="14" fill="#0d1117" stroke="#232b36"/>
  <rect x="1" y="1" width="653" height="44" rx="13" fill="#161b22"/>
  <rect x="1" y="32" width="653" height="12" fill="#161b22"/>
  <circle cx="26" cy="26" r="6.5" fill="#ff5f56"/><circle cx="48" cy="26" r="6.5" fill="#ffbd2e"/><circle cx="70" cy="26" r="6.5" fill="#27c93f"/>
  <text x="328" y="31" text-anchor="middle" font-size="13" fill="#6b7689" font-family="monospace">aeshvarya.py</text>
  <line x1="0" y1="44" x2="655" y2="44" stroke="#232b36"/>
{chr(10).join(texts)}
  <rect x="{X0}" y="{Y0 - 12:.1f}" width="7.6" height="15" fill="#82aaff">
    <animate attributeName="x" dur="{total:.2f}s" repeatCount="indefinite" keyTimes="{';'.join(caret_kt)}" values="{';'.join(caret_x)}"/>
    <animate attributeName="y" dur="{total:.2f}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{';'.join(caret_kt)}" values="{';'.join(caret_y)}"/>
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/>
  </rect>
</svg>
'''
    (OUT / "code.svg").write_text(svg)


hero(); stats(); timeline(); code()
header("numbers", "BY THE NUMBERS")
header("trophies", "TROPHY CASE")
header("journey", "THE JOURNEY")
header("oss", "OPEN SOURCE")
print("ok")
