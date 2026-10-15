#!/usr/bin/env python3
"""Images for the "new website" announcement: promo-output/website-launch/ (portrait 1080x1350, square 1080x1080, link 1200x630)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_promo import gradient, font, logo, cover, fade, fit, lines_out, pill, SKY, MUTED, ROOT

OUT = ROOT / "promo-output/website-launch"
OUT.mkdir(parents=True, exist_ok=True)
PH = Image.open(ROOT / "assets/img/source/home-studio.jpg").convert("RGB")


def make(w, h, name):
    card = gradient(w, h).convert("RGBA")
    ph_h = round(h * (0.62 if h > w else 0.55 if h == w else 0.62))
    ph = fade(cover(PH, w, ph_h, 0.5, 0.5), "bottom", 0.45)
    card.alpha_composite(ph, (0, 0))
    d = ImageDraw.Draw(card)
    s = w / 1080
    lg = logo(round(80 * s)); card.alpha_composite(lg, (round(60 * s), round(50 * s)))
    x = round(70 * s); y = ph_h - round(30 * s)
    f, lines, size = fit(d, "The Dokkcast now has a home", "800", w - 2 * x, round(260 * s), round(92 * s), 40)
    y = lines_out(d, lines, f, x, y, size, "white")
    f2, l2, s2 = fit(d, "Episodes, guests, the blog and how to work with us, all in one place.", "500", w - 2 * x, round(140 * s), round(36 * s), 22, 1.3)
    y = lines_out(d, l2, f2, x, y + round(14 * s), s2, MUTED, 1.3)
    if h >= w:
        pill(card, x, min(y + round(34 * s), h - round(120 * s)), "thedokkcast.com", round(36 * s))
    card.convert("RGB").save(OUT / name, quality=90, optimize=True)


make(1080, 1350, "website_portrait_1080x1350.jpg")
make(1080, 1080, "website_square_1080x1080.jpg")
make(1200, 630, "website_link_1200x630.jpg")
print("wrote", OUT)
