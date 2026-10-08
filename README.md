# The Dokkcast website

Standalone static site for The Dokkcast. Plain HTML and CSS with no framework, so any static host
can serve it from the repo root (GitHub Pages, Netlify, Cloudflare Pages, Vercel). It shares no code,
hosting project or config with any other site.

## Updating content

Edit the source, then rebuild and commit the result:

```bash
python3 tools/build.py      # needs Python 3 only, no packages
```

| To change | Edit |
|---|---|
| Wording on a page | `pages/<page>.html` |
| Header, footer | `partials/` |
| Contact email, podcast-app links, socials, live site URL | `data/site.json` |
| Episodes | `data/episodes.json` |
| Colours, fonts, layout | `assets/styles.css` |

Never edit the root `*.html` files by hand. They're generated and get overwritten.

### Episodes come from the Acast feed

`rss_url` in `data/site.json` points at the Acast RSS feed. Every build reads it and generates the
Episodes page and the home-page player automatically, so a new episode only needs the site rebuilding
(a Netlify deploy does this; use a Netlify build hook to trigger one on a schedule). If the feed can't
be read, the build carries on and uses `data/episodes.json` instead. That file is also the way to run
the site without a feed.

The Episodes page shows 10 episodes per page (`episodes_per_page` in `data/site.json`), with
Newer / Older links and page numbers. Extra pages (`episodes-2.html`, ...) are generated automatically.

### Adding an episode by hand (Acast)

In Acast, open the episode, choose **Share / Embed**, and copy the player link (it starts with
`https://embed.acast.com/`). Then add an entry to `data/episodes.json`:

```json
[
  {
    "number": 1,
    "title": "Episode title",
    "date": "2026-10-20",
    "guest": "Guest name (optional)",
    "summary": "A sentence or two about the episode.",
    "acast_embed": "https://embed.acast.com/...",
    "image": "assets/img/episodes/ep1.jpg",
    "image_alt": "Describe the photo"
  }
]
```

`guest`, `summary`, `image` and `image_alt` are optional. Newest episodes appear first, and the
latest one also appears on the home page. The build refuses embed links that aren't from Acast.

### Media kit and guests

The media kit lives at `media-kit.html` (source: `pages/media-kit.html`) and is linked from the Partners page and
the footer. It leads with the quality of the guests. To name some of them, add entries to `data/guests.json`:

```json
[
  {"name": "Guest name", "title": "Role, organisation", "photo": "assets/img/guests/name.jpg", "url": "https://..."}
]
```

`photo` and `url` are optional. Once there is at least one entry, a "Some of our guests" block appears on the media
kit and the Guests page; until then nothing shows. Only list guests who have agreed to be named and pictured.

### Blog

Posts are Markdown files in `content/blog/`. Create one file per post, named after the web address you want, for example
`content/blog/understanding-hrt.md` becomes `/blog/understanding-hrt.html`. Each file starts with a short header:

```markdown
---
title: Understanding HRT
date: 2026-11-02
author: Dr Nara Daubeney
description: One or two sentences, used on the blog list and in search results.
tags: Women's health, Evidence
image: assets/img/blog/understanding-hrt.jpg
image_alt: Describe the picture
---

The article text, written in Markdown. Use `##` for headings, `-` for bullet lists, `**bold**`, `*italic*` and
[links](https://example.com). Link to other pages on the site with, for example, [our episodes](episodes.html).
```

Then run `python3 tools/build.py` and commit. Notes:

- `title` and `date` are required. `author` defaults to "The Dokkcast"; "Dr Nara Daubeney" links to her page.
- `image` is optional (put pictures in `assets/img/blog/`, around 1200 x 630 pixels). Without one, the card shows the logo.
- **Drafts and scheduling:** add `draft: true` to keep a post unpublished. A post dated in the future is held back and
  appears automatically on the first build after that date (a Netlify build hook on a schedule makes this hands-free).
- The blog gets its own index with pagination (`blog_per_page` in `data/site.json`, default 9), an RSS feed at
  `/blog/feed.xml`, structured data, sitemap entries and a "Latest articles" block on the home page.
- Every post ends with the medical disclaimer and the Listen links. Keep posts to general information: no personal medical advice.

### SEO and checks

- Every page gets a canonical URL, Open Graph and Twitter tags, a favicon set and structured data (`PodcastSeries` on the
  home page, `Person` for Dr Nara, `FAQPage` on About, `PodcastEpisode` entries on the Episodes pages, and breadcrumbs).
  The Acast feed is advertised in the page head so podcast apps and search engines can find it.
- Page titles and descriptions come from the `<!--meta ... -->` block at the top of each file in `pages/` (home also has `fulltitle:`).
- `python3 tools/audit_site.py` checks the built pages for broken links and images, missing alt text, title and
  description lengths, heading order, social tags and structured data. It should report no issues before you publish.
- `netlify.toml` redirects `www` to the main domain, and short addresses such as `/about` or `/press` to the real pages.
  Keep Netlify's **Pretty URLs** setting off, or those redirects will loop.

### Share image and header menu

`assets/img/og-image.png` (the preview shown when a link is shared) is built by `tools/make_share_image.py` from the logo
and one of the studio photos. Re-run it to change the photo or wording. The **Listen** menu in the header is built from the
`listen` links in `data/site.json`; it disappears if none are set.

### Photos

The site's photos in `assets/img/` are tone-adjusted copies of the untouched originals in `assets/img/source/`
(brighter, more contrast, slightly richer colour). The same script also writes small WebP versions
(`name-720.webp` and a full-size one) that `build.py` serves to phones through `<picture>`. To change the look, edit the settings in `tools/enhance_photos.py`
and run it. To add a photo, put the original in `assets/img/source/`, add its name to `PHOTOS` in the script and run it.
If you edit a photo by hand (for example in Canva), save the finished file into `assets/img/` and remove its name from
`PHOTOS`, so the script doesn't overwrite it.

### One-page PDF

`assets/downloads/the-dokkcast-media-kit.pdf` is a designed A4 summary of the media kit, linked from the media kit and
Partners pages. It is built by `tools/make_pdf.py` from `data/site.json` and `data/guests.json` (links, email, named guests),
so re-run it and commit the new PDF whenever those change or the wording in the script is updated:

```bash
pip install playwright && playwright install chromium
python3 tools/make_pdf.py          # set CHROMIUM_PATH to use a browser you already have
```

Netlify does not build the PDF (it needs a browser), so the committed file is what visitors download.

### Still to fill in

Search the `pages/` folder for `class="placeholder"`. These need real content:
- `about.html`: description of the podcast and of udokk
- `dr-nara-daubeney.html`: biography and photo
- `data/guests.json`: named guests, with titles and photos, for the media kit and Guests page (optional)
- `guests.html`: practical details for guests
- `data/site.json`: contact email, Acast / Apple / Spotify / YouTube links, socials, and `site_url`
  once the domain is known (this also generates `sitemap.xml` and `robots.txt`)

## Brand

udokk logo (`assets/img/udokk-logo.svg`), Manrope (SIL OFL licence in `assets/fonts`), and the
logo gradient `#716BE8` to `#A5D7FF` on navy.
