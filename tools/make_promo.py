#!/usr/bin/env python3
"""Builds the launch images for an episode: key art (teaser + out now) in every size, and quote cards.

    python3 tools/make_promo.py data/promo/episode-14.json      # writes promo-output/<name>/

Everything is drawn from the episode JSON plus the brand fonts, logo and photo in this repo.
"""
import datetime, io, json, sys, tempfile
from functools import lru_cache
from pathlib import Path
import cairosvg, numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from enhance_photos import enhance  # same tone adjustment as the site photos

NAVY, INDIGO, SKY, ICE, MUTED = (10, 15, 44), (37, 26, 99), (117, 192, 251), (165, 215, 255), (180, 189, 219)


@lru_cache(None)
def font_path(weight):
    out = Path(tempfile.gettempdir()) / f"dokk-manrope-{weight}.ttf"
    f = TTFont(ROOT / f"assets/fonts/manrope-latin-{weight}-normal.woff2"); f.flavor = None; f.save(out)
    return str(out)


@lru_cache(None)
def font(weight, size):
    return ImageFont.truetype(font_path(weight), int(size))


def gradient(w, h):
    t = np.linspace(0, 1, h)[:, None, None]
    arr = np.array(NAVY)[None, None, :] * (1 - t) + np.array(INDIGO)[None, None, :] * t
    return Image.fromarray(np.repeat(arr, w, axis=1).astype("uint8"), "RGB")


def logo(height):
    svg = ROOT / "assets/img/udokk-logo-clean.svg"
    return Image.open(io.BytesIO(cairosvg.svg2png(url=str(svg), output_height=int(height)))).convert("RGBA")


def cover(ph, w, h, cx=0.5, cy=0.5):
    s = max(w / ph.width, h / ph.height)
    im = ph.resize((round(ph.width * s), round(ph.height * s)), Image.LANCZOS)
    x = min(max(round(im.width * cx - w / 2), 0), im.width - w)
    y = min(max(round(im.height * cy - h / 2), 0), im.height - h)
    return im.crop((x, y, x + w, y + h))


def fade(im, side, frac, strength=1.0):
    """Fade an image to transparent along one edge ('bottom') so it melts into the background."""
    w, h = im.size
    a = np.ones((h, w), float)
    n = int(h * frac)
    a[h - n:] = np.linspace(1, 1 - strength, n)[:, None]
    im = im.convert("RGBA"); im.putalpha(Image.fromarray((a * 255).astype("uint8")))
    return im


def wrap(d, text, f, max_w):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=f) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = word
    return lines + [cur]


def fit(d, text, weight, max_w, max_h, size, min_size, spacing=1.16):
    while size > min_size:
        f = font(weight, size); lines = wrap(d, text, f, max_w)
        if len(lines) * size * spacing <= max_h and all(d.textlength(l, font=f) <= max_w for l in lines):
            return f, lines, size
        size -= 2
    f = font(weight, min_size); return f, wrap(d, text, f, max_w), min_size


def lines_out(d, lines, f, x, y, size, fill, spacing=1.16):
    for l in lines:
        d.text((x, y), l, font=f, fill=fill); y += size * spacing
    return y


def pill(img, x, y, text, size):
    d = ImageDraw.Draw(img); f = font(800, size)
    tw = d.textlength(text, font=f); padx, pady = size * 0.9, size * 0.55
    box = (x, y, x + tw + 2 * padx, y + size + 2 * pady)
    d.rounded_rectangle(box, radius=(box[3] - box[1]) / 2, fill=(117, 192, 251))
    d.text((x + padx, y + pady - size * 0.06), text, font=f, fill=(8, 16, 46))
    return box[3]


def typo(s):
    return s.replace("'", "’")


def load_photo(ep):
    return enhance(Image.open(ROOT / ep["photo"]).convert("RGB"))


def key_art(ep, ph, state, kind, w, h):
    label = ep["label"].upper()
    when = datetime.date.fromisoformat(ep["release"])
    tag = f"{label}  ·  OUT {when.strftime('%A %-d %B').upper()}" if state == "teaser" else f"NEW EPISODE  ·  {label}  ·  OUT NOW"
    img = gradient(w, h)
    cx = ep.get("photo_focus_x", 0.5)
    if kind == "wide":                                    # photo fills the frame, text over a dark fade
        s = h / 1080
        img.paste(cover(ph, w, h, cx), (0, 0))
        ov = Image.new("RGBA", (w, h)); a = np.zeros((h, w))
        y0 = int(h * 0.30); y1 = int(h * 0.80)
        a[y0:y1] = np.linspace(0, 0.96, y1 - y0)[:, None]; a[y1:] = 0.96
        ov.paste(Image.new("RGBA", (w, h), NAVY + (255,)), (0, 0)); ov.putalpha(Image.fromarray((a * 255).astype("uint8")))
        img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        lg = logo(110 * s); img.paste(lg, (int(70 * s), int(60 * s)), lg)
        d = ImageDraw.Draw(img); x = int(80 * s); bottom = h - int(60 * s)
        guest_size = 40 * s
        d.text((x, bottom), f"{ep['guest']}  \u00b7  hosted by {ep['host']}", font=font(700, guest_size), fill=ICE, anchor="ls")
        f, ls, size = fit(d, ep["title"], 800, w - 2 * x - 40 * s, 250 * s, 112 * s, 40 * s, 1.08)
        ty = bottom - guest_size - 34 * s - len(ls) * size * 1.08
        lines_out(d, ls, f, x, ty, size, "white", 1.08)
        pill(img, x, int(ty - 30 * s - (34 * s * 2.1)), tag, 34 * s)
        return img
    # photo on top, text underneath
    margin = int(w * 0.06)
    photo_h = {"square": int(h * 0.56), "portrait": int(h * 0.57), "story": int(h * 0.40)}[kind]
    top = {"square": 0, "portrait": 0, "story": int(h * 0.19)}[kind]
    band = fade(cover(ph, w, photo_h, cx), "bottom", 0.38)
    img = img.convert("RGBA"); img.alpha_composite(band, (0, top)); img = img.convert("RGB")
    lg_h = {"square": 92, "portrait": 100, "story": 150}[kind]; lg = logo(lg_h)
    img.paste(lg, ((w - lg.width) // 2 if kind == "story" else margin, int(h * 0.075) if kind == "story" else 44), lg)
    d = ImageDraw.Draw(img)
    y = top + int(photo_h * 0.80)
    unit = w / 1080
    y = pill(img, margin, y, tag, 25 * unit) + 26 * unit
    safe_bottom = h - (int(h * 0.15) if kind == "story" else int(h * 0.10))
    footer = 30 * unit
    guest_h = 40 * unit * 1.5
    f, ls, size = fit(d, ep["title"], 800, w - 2 * margin, safe_bottom - y - guest_h - footer - 40 * unit, 84 * unit, 36 * unit, 1.1)
    y = lines_out(d, ls, f, margin, y, size, "white", 1.1) + 14 * unit
    d.text((margin, y), f"with {ep['guest']}", font=font(700, 38 * unit), fill=SKY)
    d.text((margin, safe_bottom - footer), f"The Dokkcast  ·  hosted by {ep['host']}  ·  {ep['site']}", font=font(500, 27 * unit), fill=MUTED)
    return img


def quote_card(ep, q, w, h):
    img = gradient(w, h); d = ImageDraw.Draw(img); m = int(w * 0.09); u = w / 1080
    lg = logo(88 * u); img.paste(lg, (m, int(70 * u)), lg)
    text = typo(q["text"])
    top = int(h * 0.27) + 90 * u                         # leaves room for the quote mark above the text
    footer_y = h - 86 * u
    attribution = 152 * u                                # rule + name + show line
    f, ls, size = fit(d, text, 800, w - 2 * m, footer_y - 44 * u - attribution - top, 78 * u, 36 * u, 1.2)
    d.text((m - 6 * u, top - 205 * u), "\u201c", font=font(800, 250 * u), fill=(90, 153, 245))
    y = lines_out(d, ls, f, m, top, size, "white", 1.2)
    d.rectangle((m, y + 26 * u, m + 120 * u, y + 32 * u), fill=SKY)
    d.text((m, y + 56 * u), ep["guest"], font=font(800, 40 * u), fill=SKY)
    d.text((m, y + 56 * u + 54 * u), f"The Dokkcast  \u00b7  {ep['label']}: {ep['short_title']}", font=font(500, 30 * u), fill=MUTED)
    d.text((m, footer_y), f"{ep['site']}", font=font(700, 30 * u), fill=ICE)
    return img


def main(path):
    ep = json.loads(Path(path).read_text(encoding="utf-8"))
    out = ROOT / "promo-output" / Path(path).stem; out.mkdir(parents=True, exist_ok=True)
    for old in list(out.glob("*.jpg")) + list(out.glob("*.png")):
        old.unlink()
    ph = load_photo(ep); n = Path(path).stem.replace("episode-", "ep")
    sizes = {"square": (1080, 1080), "portrait": (1080, 1350), "story": (1080, 1920), "wide": (1920, 1080), "link": (1200, 630), "thumb": (1280, 720)}
    for state in ("teaser", "nowout"):
        for kind, (w, h) in sizes.items():
            img = key_art(ep, ph, state, "wide" if kind in ("wide", "link", "thumb") else kind, w, h)
            if kind == "thumb" and state == "teaser":
                continue                                   # a YouTube thumbnail is only needed once the video is live
            name = f"{n}_keyart_{state}_{kind}_{w}x{h}.jpg"
            img.save(out / name, quality=92, optimize=True); print(name)
    for i, q in enumerate(ep["quotes"], 1):
        for kind, (w, h) in (("square", (1080, 1080)), ("portrait", (1080, 1350))):
            name = f"{n}_quote{i}_{kind}_{w}x{h}.png"; quote_card(ep, q, w, h).save(out / name, optimize=True); print(name)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/promo/episode-14.json")
