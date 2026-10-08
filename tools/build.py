#!/usr/bin/env python3
"""Builds the static site: pages/*.html + partials/ + data/*.json -> *.html in the repo root.

    python3 tools/build.py

Edit content in pages/, data/site.json and data/episodes.json, never the generated
root .html files. The generated files are committed so any static host can serve the repo as-is.
"""
import datetime, html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAV = [("index.html", "Home"), ("episodes.html", "Episodes"), ("about.html", "About"),
       ("dr-nara-daubeney.html", "Dr Nara Daubeney"), ("partners.html", "Sponsors &amp; Partners"),
       ("guests.html", "Guests")]
EMBED_HOSTS = ("https://embed.acast.com/", "https://shows.acast.com/", "https://sphinx.acast.com/")
esc = html.escape


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def link(url, label):
    return f'<a href="{esc(url, True)}" rel="noopener">{esc(label)}</a>'


def episode_html(e, heading="h3"):
    if not any(e.get("acast_embed", "").startswith(h) for h in EMBED_HOSTS) and e.get("acast_embed"):
        sys.exit(f"episode '{e.get('title')}': acast_embed must start with one of {EMBED_HOSTS}")
    meta = " &middot; ".join(x for x in (f"Episode {e['number']}" if e.get("number") else "",
                                         _date(e.get("date"))) if x)
    out = ['<article class="episode">']
    if meta:
        out.append(f'<div class="meta">{meta}</div>')
    out.append(f"<{heading}>{esc(e['title'])}</{heading}>")
    if e.get("guest"):
        out.append(f'<p class="guest-line">With {esc(e["guest"])}</p>')
    if e.get("summary"):
        out.append(f"<p>{esc(e['summary'])}</p>")
    if e.get("image"):
        out.append(f'<figure><img src="{esc(e["image"], True)}" alt="{esc(e.get("image_alt", ""), True)}" loading="lazy"></figure>')
    if e.get("acast_embed"):
        out.append(f'<iframe src="{esc(e["acast_embed"], True)}" title="Listen: {esc(e["title"], True)}" loading="lazy" '
                   f'allow="autoplay" height="190"></iframe>')
    out.append("</article>")
    return "\n".join(out)


def _date(s):
    if not s:
        return ""
    d = datetime.date.fromisoformat(s)
    return f"{d.day} {d.strftime('%B %Y')}"


def build():
    site, eps = load("site.json"), load("episodes.json")
    eps = sorted(eps, key=lambda e: e.get("date", ""), reverse=True)
    listen = {k: v for k, v in site["listen"].items() if v}
    social = {k: v for k, v in site["social"].items() if v}
    header = (ROOT / "partials/header.html").read_text(encoding="utf-8")
    footer = (ROOT / "partials/footer.html").read_text(encoding="utf-8")

    placeholder = lambda t: f'<div class="placeholder">{t}</div>'
    tokens = {
        "show_name": site["show_name"], "udokk_url": site["udokk_url"], "year": str(datetime.date.today().year),
        "email": site["email"],
        "contact_line": f'        <p>Press and partnership enquiries:<br>{link("mailto:" + site["email"], site["email"])}</p>' if site["email"] else "",
        "listen_items": "\n".join(f"          <li>{link(u, k)}</li>" for k, u in listen.items())
                        or "          <li>Episodes coming soon.</li>",
        "listen_buttons": "\n".join(f'<a class="btn ghost" href="{esc(u, True)}" rel="noopener">{esc(k)}</a>' for k, u in listen.items()),
        "social_items": "\n".join(f"<li>{link(u, k)}</li>" for k, u in social.items()),
        "footer_nav": "\n".join(f'          <li><a href="{h}">{t}</a></li>' for h, t in NAV),
        "latest_episode": episode_html(eps[0], "h3") if eps else placeholder(
            "<strong>Our first episode is on its way.</strong> Check back soon."),
        "episodes_list": "\n".join(episode_html(e, "h2") for e in eps) if eps else placeholder(
            "<strong>No episodes published yet.</strong> They'll appear here as soon as they're released."),
        "email_cta": (f'<a class="btn" href="mailto:{esc(site["email"], True)}">Email us</a>' if site["email"]
                      else '<span class="note">Contact email to be added.</span>'),
    }
    for src in sorted((ROOT / "pages").glob("*.html")):
        text = src.read_text(encoding="utf-8")
        m = re.match(r"<!--meta\s*(.*?)-->\s*", text, re.S)
        if not m:
            sys.exit(f"{src.name}: missing <!--meta ... --> block")
        meta = dict(l.split(":", 1) for l in m.group(1).strip().splitlines())
        body = text[m.end():]
        name = src.name
        nav = "\n".join('      <a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == name else "", t) for h, t in NAV)
        page_tokens = {**tokens, "nav": nav}
        title = meta["title"].strip()
        full_title = site["show_name"] if name == "index.html" else f"{title} | {site['show_name']}"
        url = f'{site["site_url"].rstrip("/")}/{"" if name == "index.html" else name}' if site["site_url"] else ""
        og_img = f'{site["site_url"].rstrip("/")}/assets/img/og-image.png' if site["site_url"] else "assets/img/og-image.png"
        head = f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(meta["desc"].strip(), True)}">
<meta name="theme-color" content="#0a0f2c">
{'<base href="/">' if name == "404.html" else ""}
{f'<link rel="canonical" href="{url}">' if url and name != "404.html" else ""}
{'<meta name="robots" content="noindex">' if name == "404.html" else ""}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(site["show_name"], True)}">
<meta property="og:title" content="{esc(full_title, True)}">
<meta property="og:description" content="{esc(meta["desc"].strip(), True)}">
<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/udokk-logo.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/manrope-latin-800-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/styles.css">
</head>
<body>
'''
        doc = head + header + '\n<main id="main">\n' + body.strip() + "\n</main>\n" + footer + \
              '\n<script src="assets/site.js" defer></script>\n</body>\n</html>\n'
        for k, v in page_tokens.items():
            doc = doc.replace("{{" + k + "}}", v)
        left = re.findall(r"\{\{(\w+)\}\}", doc)
        if left:
            sys.exit(f"{name}: unknown tokens {left}")
        (ROOT / name).write_text(doc, encoding="utf-8")
        print("built", name)
    if site["site_url"]:
        base = site["site_url"].rstrip("/")
        urls = "".join(f"  <url><loc>{base}/{'' if h == 'index.html' else h}</loc></url>\n" for h, _ in NAV)
        (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
        (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")


if __name__ == "__main__":
    build()
