#!/usr/bin/env python3
"""Renders GUIDE.md as a DXR Cyber-branded page.

  python3 build.py                        -> index.html (PLAINTEXT, local reading only)
  python3 build.py build/index.plain.html -> for build/encrypt.js

NEVER commit the plaintext output: this guide contains DXR's effort model, which is the
basis of their pricing. index.html in the repo is the encrypted gate.

No markdown library here on purpose — the guide uses a small, known subset (headings,
tables, lists, blockquotes, bold/italic/code, rules) and a dependency would be the only
thing standing between an edit and a rebuild.
"""
import html as _html
import pathlib
import re
import sys

SRC = pathlib.Path(__file__).parent / "GUIDE.md"

CSS = """
:root{--lime:#a6ff33;--ink:#1d1d1b;--text:#2b303a;--muted:#5d626c;--dim:#8a8e96;
  --accent:#3b7a00;--teal:#0077a8;--line:rgba(43,48,58,.12);--s1:rgba(43,48,58,.045);--r:14px}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff;color:var(--text);
  font-family:"Instrument Sans",system-ui,-apple-system,"Segoe UI",sans-serif;font-size:16px;line-height:1.6;
  -webkit-font-smoothing:antialiased}
.bar{display:flex;align-items:center;gap:18px;padding:20px 40px;border-bottom:1px solid var(--line);
  position:sticky;top:0;background:rgba(255,255,255,.94);backdrop-filter:blur(12px);z-index:10}
.bar img{width:132px;height:auto;display:block}
.bar .tag{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:600;
  border-left:1px solid var(--line);padding-left:14px}
.wrap{max-width:860px;margin:0 auto;padding:28px 24px 90px}
h1{font-size:40px;line-height:1.1;letter-spacing:-.02em;color:var(--ink);margin:14px 0 6px;font-weight:700}
h2{font-size:25px;letter-spacing:-.015em;color:var(--ink);margin:46px 0 12px;font-weight:700;
  padding-top:18px;border-top:3px solid var(--lime);display:inline-block;padding-right:10px}
h3{font-size:18px;color:var(--ink);margin:28px 0 8px;font-weight:600}
p{margin:0 0 14px}
strong{color:var(--ink)}
code{background:var(--s1);padding:1px 6px;border-radius:5px;font-size:.88em;
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
pre{background:#f7f9fb;border:1px solid var(--line);border-radius:var(--r);padding:16px 18px;overflow-x:auto;
  font-size:13px;line-height:1.5}
pre code{background:none;padding:0}
table{border-collapse:collapse;width:100%;margin:16px 0 20px;font-size:14.5px}
th{background:var(--ink);color:#fff;text-align:left;padding:9px 12px;font-size:11.5px;
  letter-spacing:.05em;text-transform:uppercase;font-weight:600}
td{padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
tr:nth-child(even) td{background:#fafbfc}
blockquote{margin:18px 0;padding:14px 18px;background:var(--s1);border-left:3px solid var(--lime);
  border-radius:0 var(--r) var(--r) 0}
blockquote p:last-child{margin-bottom:0}
ul,ol{margin:0 0 16px;padding-left:22px}
li{margin-bottom:6px}
hr{border:0;border-top:1px solid var(--line);margin:34px 0}
em{color:var(--muted)}
.sub{font-size:17px;color:var(--muted);margin:0 0 6px}
@media(max-width:640px){.bar{padding:16px 20px}.wrap{padding:20px 18px 64px}h1{font-size:30px}table{font-size:13px}}
"""


def inline(s: str) -> str:
    s = _html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    return s


def render(md: str) -> str:
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        ln = lines[i]

        if ln.startswith("```"):                                    # fenced code
            body = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(_html.escape(lines[i], quote=False))
                i += 1
            out.append("<pre><code>" + "\n".join(body) + "</code></pre>")
            i += 1
            continue

        if re.match(r"^\s*\|", ln) and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            head = cells(ln)
            i += 2
            rows = []
            while i < len(lines) and re.match(r"^\s*\|", lines[i]):
                rows.append(cells(lines[i]))
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f"<table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table>")
            continue

        if ln.startswith(">"):                                      # blockquote
            body = []
            while i < len(lines) and lines[i].startswith(">"):
                body.append(lines[i].lstrip(">").strip())
                i += 1
            paras = "".join(f"<p>{inline(p)}</p>" for p in "\n".join(body).split("\n\n") if p.strip())
            out.append(f"<blockquote>{paras}</blockquote>")
            continue

        m = re.match(r"^(#{1,3})\s+(.*)$", ln)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue

        if re.match(r"^\s*[-*]\s+", ln) or re.match(r"^\s*\d+\.\s+", ln):
            ordered = bool(re.match(r"^\s*\d+\.\s+", ln))
            items = []
            while i < len(lines) and (re.match(r"^\s*[-*]\s+", lines[i]) or re.match(r"^\s*\d+\.\s+", lines[i])
                                      or (lines[i].startswith("  ") and lines[i].strip() and items)):
                if lines[i].startswith("  ") and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]) and items:
                    items[-1] += " " + lines[i].strip()               # wrapped continuation
                else:
                    items.append(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i]))
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue

        if re.match(r"^---+\s*$", ln):
            out.append("<hr>")
            i += 1
            continue

        if ln.strip():
            para = [ln]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,3}\s|>|```|\s*\||\s*[-*]\s|\s*\d+\.\s|---+\s*$)", lines[i]):
                para.append(lines[i])
                i += 1
            out.append(f"<p>{inline(' '.join(para))}</p>")
            continue

        i += 1
    return "\n".join(out)


md = SRC.read_text()
title = re.search(r"^#\s+(.*)$", md, re.M).group(1)
body = render(md)

doc = f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet">
<title>{_html.escape(title)} — DXR Cyber</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header class="bar">
  <img src="assets/dxr-cyber-logo.png" alt="DXR Cyber">
  <div class="tag">Pre-Sales · Scoping calculator</div>
</header>
<main class="wrap">
{body}
</main>
</body>
</html>
"""

out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(doc)
print(f"{out} written: {len(doc):,} chars")
