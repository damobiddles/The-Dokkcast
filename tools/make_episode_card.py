#!/usr/bin/env python3
"""Makes assets/img/episode-13-alexander-lyon.jpg, a 16:9 branded card (guest portrait + title) for the blog and social previews."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_promo import gradient, font, logo, SKY, MUTED, ROOT

W, H = 1600, 900
card = gradient(W, H)
photo = Image.open(ROOT / "assets/img/source/alexander-lyon.jpg").convert("RGB")
pw = 620
photo = photo.crop((0, 0, photo.width, int(photo.width * 1.2))).resize((pw, int(pw * 1.2)), Image.LANCZOS)   # head and shoulders
mask = Image.new("L", photo.size, 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, *photo.size), 36, fill=255)
card.paste(photo, (W - pw - 90, (H - photo.height) // 2), mask)
d = ImageDraw.Draw(card)
d.text((100, 250), "EPISODE 13", font=font(800, 34), fill=SKY)
y = 310
for line in ("Cancer treatment", "and heart health"):
    d.text((100, y), line, font=font(800, 82), fill="white"); y += 100
d.text((100, y + 30), "Dr Alexander Lyon", font=font(700, 44), fill="white")
d.text((100, y + 90), "Consultant cardiologist, Royal Brompton Hospital", font=font(500, 28), fill=MUTED)
lg = logo(70)
card.paste(lg, (100, 90), lg if lg.mode == "RGBA" else None)
card.save(ROOT / "assets/img/episode-13-alexander-lyon.jpg", quality=88, optimize=True)
print("wrote episode-13-alexander-lyon.jpg")
