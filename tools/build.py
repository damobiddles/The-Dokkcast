#!/usr/bin/env python3
"""Builds the static site: pages/*.html + partials/ + data/*.json -> *.html in the repo root.

    python3 tools/build.py

Edit content in pages/, data/site.json and data/episodes.json, never the generated
root .html files. The generated files are committed so any static host can serve the repo as-is.
"""
import datetime, email.utils, html, json, re, sys, urllib.request
import xml.etree.ElementTree as ET
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


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _text(html_text, limit=320):
    t = re.sub(r"<[^>]+>", " ", html.unescape(html_text or ""))
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s+([.,;:!?])", r"\1", t)
    return t if len(t) <= limit else t[:limit].rsplit(" ", 1)[0] + "\u2026"


def parse_feed(xml_text, feed_url=""):
    """Podcast RSS -> episode dicts in the same shape as data/episodes.json."""
    chan = ET.fromstring(xml_text).find("channel")
    m = re.search(r"/([0-9a-f]{24})/?$", feed_url)
    show_hint = m.group(1) if m else ""
    eps = []
    for item in chan.findall("item"):
        f = {}
        for c in item:
            k = _local(c.tag)
            if k == "image":
                f.setdefault("image", c.get("href"))
            elif k not in f:
                f[k] = (c.text or "").strip()
        if not f.get("title"):
            continue
        guid = f.get("guid", "")
        show_id = f.get("showId") or show_hint
        ep_id = f.get("episodeId") or (guid if re.fullmatch(r"[0-9a-f]{24}", guid) else "")
        e = {"title": _text(f["title"], 200), "summary": _text(f.get("summary") or f.get("description"))}
        try:
            e["date"] = email.utils.parsedate_to_datetime(f["pubDate"]).date().isoformat()
        except (KeyError, TypeError, ValueError):
            pass
        if f.get("episode", "").isdigit():
            e["number"] = int(f["episode"])
        if show_id and ep_id:
            e["acast_embed"] = f"https://embed.acast.com/{show_id}/{ep_id}"
        if f.get("link", "").startswith("https://") and "acast.com" in f["link"].split("/")[2]:
            e["link"] = f["link"]
        if (f.get("image") or "").startswith("https://"):
            e["image"] = f["image"]
            e["image_alt"] = ""
        eps.append(e)
    return eps


def fetch_episodes(url):
    """Episodes from the RSS feed, or None if it can't be read (the build must never fail on this)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "dokkcast-site-build"})
        with urllib.request.urlopen(req, timeout=25) as r:
            eps = parse_feed(r.read().decode("utf-8"), url)
        print(f"feed: {len(eps)} episodes from {url}")
        return eps
    except Exception as ex:  # network, XML, anything
        print(f"feed: could not read {url} ({ex}); using data/episodes.json", file=sys.stderr)
        return None


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
    elif e.get("link"):
        out.append(f'<p><a class="btn ghost" href="{esc(e["link"], True)}" rel="noopener">Listen on Acast</a></p>')
    out.append("</article>")
    return "\n".join(out)


def _date(s):
    if not s:
        return ""
    d = datetime.date.fromisoformat(s)
    return f"{d.day} {d.strftime('%B %Y')}"


def build():
    site = load("site.json")
    eps = (fetch_episodes(site["rss_url"]) if site.get("rss_url") else None) or load("episodes.json")
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
