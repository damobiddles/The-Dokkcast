#!/usr/bin/env python3
"""Podcast cover art (square, 3000x3000, JPEG) with the host's portrait: promo-output/cover/dokkcast-cover-3000.jpg

Uses assets/img/source/nara.jpg. That file is only 400px wide, so for a sharper cover replace it with a larger original.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_promo import gradient, font, logo, cover, SKY, MUTED, ROOT

OUT = ROOT / "promo-output/cover"
OUT.mkdir(parents=True, exist_ok=True)
S = 3000
card = gradient(S, S).convert("RGBA")
d = ImageDraw.Draw(card)

# portrait in a circle, bottom right, with a sky-blue ring
D = 1330
ph = cover(Image.open(ROOT / "assets/img/source/nara.jpg").convert("RGB"), D, D, 0.5, 0.42).filter(ImageFilter.UnsharpMask(2, 60, 2))
mask = Image.new("L", (D * 2, D * 2), 0); ImageDraw.Draw(mask).ellipse((0, 0, D * 2 - 1, D * 2 - 1), fill=255)
mask = mask.resize((D, D), Image.LANCZOS)
cx, cy = S - D - 170, S - D - 150
ring = 34
d.ellipse((cx - ring, cy - ring, cx + D + ring, cy + D + ring), fill=SKY)
card.paste(ph, (cx, cy), mask)

lg = logo(260); card.alpha_composite(lg, (230, 180))
d.text((220, 470), "The", font=font(800, 520), fill="white")
d.text((220, 910), "Dokkcast", font=font(800, 520), fill=SKY)
for i, t in enumerate(("Evidence-led", "health podcast")):
    d.text((230, 1640 + i * 135), t, font=font(700, 116), fill="white")
d.text((230, 2000), "with", font=font(500, 100), fill=MUTED)
d.text((230, 2130), "Dr Nara", font=font(800, 130), fill=SKY)
d.text((230, 2290), "Daubeney", font=font(800, 130), fill=SKY)
card.convert("RGB").save(OUT / "dokkcast-cover-3000.jpg", quality=92, optimize=True)
card.convert("RGB").resize((1400, 1400), Image.LANCZOS).save(OUT / "dokkcast-cover-1400.jpg", quality=92, optimize=True)
card.convert("RGB").resize((120, 120), Image.LANCZOS).save("/tmp/cover-thumb.png")
print("wrote", OUT)
