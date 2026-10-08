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

### Media kit

The media kit lives at `media-kit.html` (source: `pages/media-kit.html`) and is linked from the Partners page
and the footer. Audience figures come from `data/mediakit.json`. Put a value on any line (for example
`"value": "1,200"` for "Downloads per episode") and it appears under "Audience in numbers". Lines left blank are
hidden, and the whole block stays out of the page until at least one has a value. Set `as_of` to show a date.

### Still to fill in

Search the `pages/` folder for `class="placeholder"`. These need real content:
- `about.html`: description of the podcast and of udokk
- `dr-nara-daubeney.html`: biography and photo
- `data/mediakit.json`: audience figures for the media kit (optional)
- `guests.html`: practical details for guests
- `data/site.json`: contact email, Acast / Apple / Spotify / YouTube links, socials, and `site_url`
  once the domain is known (this also generates `sitemap.xml` and `robots.txt`)

## Brand

udokk logo (`assets/img/udokk-logo.svg`), Manrope (SIL OFL licence in `assets/fonts`), and the
logo gradient `#716BE8` to `#A5D7FF` on navy.
