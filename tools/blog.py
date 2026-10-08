"""Blog support for tools/build.py: Markdown posts in content/blog/*.md -> post data, HTML bodies, cards and an RSS feed.

Dependency-free on purpose (the Netlify build only needs Python). Supported Markdown: headings, paragraphs, bullet and
numbered lists, blockquotes, fenced code, horizontal rules, images, links, **bold**, *italic*, `code`.
"""
import datetime, email.utils, html, math, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "blog"
esc = html.escape


# ---------------------------------------------------------------- markdown
def _safe_url(u):
    u = u.strip()
    return u if not re.match(r"(?i)^(javascript|data|vbscript):", u) else "#"


def _inline(s):
    s = html.escape(s, quote=False)
    codes = []
    s = re.sub(r"`([^`]+)`", lambda m: (codes.append(m.group(1)) or f"\x00{len(codes) - 1}\x00"), s)
    s = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)",
               lambda m: f'<img src="{esc(_safe_url(m.group(2)), True)}" alt="{esc(m.group(1), True)}" loading="lazy">', s)

    def link(m):
        url = _safe_url(m.group(2))
        ext = ' rel="noopener"' if re.match(r"(?i)^https?://", url) else ""
        return f'<a href="{esc(url, True)}"{ext}>{m.group(1)}</a>'
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", r"<em>\1</em>", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", s)   # already escaped above


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", text).lower()).strip("-")


def md_to_html(text):
    lines, out, i = text.replace("\r\n", "\n").split("\n"), [], 0
    block_start = re.compile(r"^(#{1,6}\s|>|```|\s*[-*+]\s+|\s*\d+[.)]\s+|(-{3,}|\*{3,})\s*$)")
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf), quote=False) + "</code></pre>")
        elif re.match(r"^#{1,6}\s", line):
            m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
            level = min(max(len(m.group(1)), 2), 4)      # the post title is the h1, so body headings start at h2
            inner = _inline(m.group(2))
            out.append(f'<h{level} id="{_slug(inner)}">{inner}</h{level}>')
            i += 1
        elif re.match(r"^(-{3,}|\*{3,})\s*$", line):
            out.append("<hr>"); i += 1
        elif line.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i][1:].strip()); i += 1
            out.append("<blockquote>" + md_to_html("\n".join(buf)) + "</blockquote>")
        elif re.match(r"^\s*[-*+]\s+", line) or re.match(r"^\s*\d+[.)]\s+", line):
            ordered = bool(re.match(r"^\s*\d+[.)]\s+", line))
            pat = r"^\s*\d+[.)]\s+" if ordered else r"^\s*[-*+]\s+"
            items = []
            while i < len(lines) and (re.match(pat, lines[i]) or (items and lines[i].startswith("  ") and lines[i].strip())):
                if re.match(pat, lines[i]):
                    items.append(re.sub(pat, "", lines[i]))
                else:
                    items[-1] += " " + lines[i].strip()
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + f"</{tag}>")
        else:
            buf = []
            while i < len(lines) and lines[i].strip() and not (buf and block_start.match(lines[i])):
                buf.append(lines[i].rstrip("\n")); i += 1
            joined = " ".join(b.strip() for b in buf)
            if re.fullmatch(r"!\[[^\]]*\]\([^)\s]+\)", joined):
                out.append("<figure>" + _inline(joined) + "</figure>")
            else:
                out.append("<p>" + _inline(joined) + "</p>")
    return "\n".join(out)


# ------------------------------------------------------------------- posts
def _front_matter(raw):
    m = re.match(r"---\s*\n(.*?)\n---\s*\n?", raw, re.S)
    if not m:
        raise ValueError("missing front matter (--- ... ---)")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip().strip('"').strip("'")
    return meta, raw[m.end():]


def load_posts(today=None):
    """Published posts, newest first. Drafts and posts dated in the future are skipped (they appear once their date arrives)."""
    today = today or datetime.date.today()
    posts = []
    for f in sorted(CONTENT.glob("*.md")) if CONTENT.exists() else []:
        try:
            meta, body = _front_matter(f.read_text(encoding="utf-8"))
            date = datetime.date.fromisoformat(meta["date"])
            title = meta["title"]
        except (KeyError, ValueError) as e:
            raise SystemExit(f"{f.name}: {e}. A post needs front matter with at least title and date (YYYY-MM-DD).")
        if meta.get("draft", "").lower() in ("true", "yes", "1") or date > today:
            continue
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", f.stem)
        body_html = md_to_html(body)
        words = len(re.sub(r"<[^>]+>", " ", body_html).split())
        first_p = re.search(r"<p>(.*?)</p>", body_html, re.S)
        excerpt = meta.get("description") or (re.sub(r"<[^>]+>", "", first_p.group(1))[:170] if first_p else "")
        posts.append({
            "slug": slug, "url": f"blog/{slug}.html", "title": title, "date": date,
            "date_str": f"{date.day} {date.strftime('%B %Y')}", "author": meta.get("author", "The Dokkcast"),
            "description": excerpt, "tags": [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
            "image": meta.get("image", ""), "image_alt": meta.get("image_alt", ""),
            "body_html": body_html, "minutes": max(1, math.ceil(words / 200)),
        })
    return sorted(posts, key=lambda p: (p["date"], p["slug"]), reverse=True)


def meta_line(p):
    return f'{esc(p["date_str"])} &middot; {p["minutes"]} min read'


def tags_html(p):
    return ('<ul class="tags">' + "".join(f"<li>{esc(t)}</li>" for t in p["tags"]) + "</ul>") if p["tags"] else ""


def card_html(p, heading="h2"):
    img = (f'<img src="{esc(p["image"], True)}" alt="" width="800" height="450" loading="lazy">' if p["image"]
           else '<span class="post-card-ph"><img src="assets/img/udokk-logo.svg" alt="" width="64" height="71"></span>')
    return (f'<article class="post-card"><a class="post-card-img" href="{esc(p["url"], True)}" tabindex="-1" aria-hidden="true">{img}</a>'
            f'<div class="post-card-body"><div class="meta">{meta_line(p)}</div>'
            f'<{heading} class="post-card-title"><a href="{esc(p["url"], True)}">{esc(p["title"])}</a></{heading}>'
            f'<p>{esc(p["description"])}</p>{tags_html(p)}</div></article>')


def post_nav_html(posts, i):
    """Links to the newer and older post."""
    newer = posts[i - 1] if i > 0 else None
    older = posts[i + 1] if i + 1 < len(posts) else None
    if not (newer or older):
        return ""
    a = lambda p, label, rel: f'<a href="{esc(p["url"], True)}" rel="{rel}"><span>{label}</span>{esc(p["title"])}</a>'
    return ('<nav class="post-nav" aria-label="More posts">'
            + (a(newer, "&larr; Newer", "prev") if newer else "<span></span>")
            + (a(older, "Older &rarr;", "next") if older else "<span></span>") + "</nav>")


def feed_xml(site, posts):
    base = site["site_url"].rstrip("/")
    items = "".join(
        f"<item><title>{esc(p['title'])}</title><link>{base}/{p['url']}</link><guid isPermaLink=\"true\">{base}/{p['url']}</guid>"
        f"<pubDate>{email.utils.format_datetime(datetime.datetime.combine(p['date'], datetime.time(9, 0), datetime.timezone.utc))}</pubDate>"
        f"<description>{esc(p['description'])}</description></item>" for p in posts)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
            f"<title>{esc(site['show_name'])} blog</title><link>{base}/blog/</link>"
            f"<description>Articles and show notes from {esc(site['show_name'])}.</description><language>en-gb</language>"
            f'<atom:link href="{base}/blog/feed.xml" rel="self" type="application/rss+xml"/>{items}</channel></rss>\n')
