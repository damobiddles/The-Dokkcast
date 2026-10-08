#!/usr/bin/env python3
"""Static audit of the built site: links, titles, descriptions, headings, images, social tags, structured data.

    python3 tools/audit_site.py           # audits the *.html files in the repo root
"""
import json, re, sys
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
pages = sorted(list(ROOT.glob("*.html")) + list((ROOT / "blog").glob("*.html")))
site = json.loads((ROOT / "data/site.json").read_text())
base = site["site_url"].rstrip("/")
issues, info = [], []
titles, descs = {}, {}

def add(page, msg, level="ISSUE"):
    (issues if level == "ISSUE" else info).append(f"{page}: {msg}")

for p in pages:
    soup = BeautifulSoup(p.read_text(encoding="utf-8"), "html.parser")
    n = str(p.relative_to(ROOT))
    t = (soup.title.string or "").strip() if soup.title else ""
    d = (soup.find("meta", attrs={"name": "description"}) or {}).get("content", "")
    titles.setdefault(t, []).append(n); descs.setdefault(d, []).append(n)
    if not t: add(n, "missing <title>")
    elif len(t) > 60: add(n, f"title is {len(t)} chars (aim for <=60): {t}")
    elif len(t) < 20 and n != "404.html": add(n, f"title is short ({len(t)}): {t}", "INFO")
    if not d: add(n, "missing meta description")
    elif len(d) > 160: add(n, f"description is {len(d)} chars (aim for <=160)")
    elif len(d) < 70: add(n, f"description is short ({len(d)} chars)", "INFO")
    h1s = soup.find_all("h1")
    if len(h1s) != 1: add(n, f"{len(h1s)} <h1> elements")
    last = 1
    for h in soup.find_all(re.compile("^h[1-6]$")):
        lvl = int(h.name[1])
        if lvl > last + 1: add(n, f"heading jumps h{last} -> h{lvl}: {h.get_text(strip=True)[:40]}")
        last = lvl
    if not soup.find("html", lang=True): add(n, "missing lang")
    if not soup.find("link", rel="canonical") and n != "404.html": add(n, "missing canonical")
    for prop in ("og:title", "og:description", "og:image", "og:url", "og:type"):
        if not soup.find("meta", property=prop) and n != "404.html": add(n, f"missing {prop}")
    for nm in ("twitter:card", "twitter:title", "twitter:image"):
        if not soup.find("meta", attrs={"name": nm}) and n != "404.html": add(n, f"missing {nm}", "INFO")
    if not soup.find("link", rel="alternate", type="application/rss+xml") and n == "index.html": add(n, "no RSS <link rel=alternate>", "INFO")
    if not soup.find("script", type="application/ld+json") and n != "404.html": add(n, "no structured data (JSON-LD)", "INFO")
    for img in soup.find_all("img"):
        if img.get("alt") is None: add(n, f"image without alt: {img.get('src')}")
        if not (img.get("width") and img.get("height")): add(n, f"image without width/height: {img.get('src')}")
        src = img.get("src", "")
        if src and not src.startswith("http") and not ((ROOT / src.lstrip("/")) if src.startswith("/") else (p.parent / src)).exists(): add(n, f"broken image: {src}")
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if h.startswith(("mailto:", "tel:", "#")): continue
        u = urlparse(h)
        if u.scheme in ("http", "https"):
            if u.netloc and urlparse(base).netloc not in u.netloc and a.get("rel") is None: add(n, f"external link without rel=noopener: {h[:60]}", "INFO")
            continue
        path = u.path.lstrip("/") if h.startswith("/") else u.path
        target = (ROOT / path) if h.startswith("/") else (p.parent / path)
        if path and not target.exists(): add(n, f"broken internal link: {h}")
    if "To add" in p.read_text(): add(n, 'contains visible "To add" placeholder text')
    words = len(soup.get_text(" ", strip=True).split())
    if words < 120 and n != "404.html": add(n, f"thin content ({words} words)", "INFO")

for t, ps in titles.items():
    if len(ps) > 1: add(",".join(ps), f"duplicate title: {t}")
for d, ps in descs.items():
    if len(ps) > 1 and d: add(",".join(ps), "duplicate description")
for need in ("sitemap.xml", "robots.txt", "404.html", "blog/feed.xml"):
    if not (ROOT / need).exists(): add("site", f"missing {need}")
for f in ("assets/img/og-image.png",):
    if not (ROOT / f).exists(): add("site", f"missing {f}")
print(f"{len(pages)} pages audited\n\nISSUES ({len(issues)}):"); print("\n".join("  - " + i for i in issues) or "  none")
print(f"\nNOTES ({len(info)}):"); print("\n".join("  - " + i for i in info) or "  none")
