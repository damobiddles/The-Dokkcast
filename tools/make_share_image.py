#!/usr/bin/env python3
"""Builds the social share image (assets/img/og-image.png, 1200x630): logo and web address on the left, podcast cover art on the right.

    pip install pillow cairosvg fonttools brotli
    python3 tools/make_share_image.py
"""
import io, tempfile
from pathlib import Path
import cairosvg
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 630
PHOTO = "conversation-pair"          # which photo in assets/img/ to use
PHOTO_X = 640                        # where the photo panel starts


def font(weight, size):
    out = Path(tempfile.gettempdir()) / f"manrope-{weight}.ttf"
    f = TTFont(ROOT / f"assets/fonts/manrope-latin-{weight}-normal.woff2"); f.flavor = None; f.save(out)
    return ImageFont.truetype(str(out), size)


def main():
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):                                        # navy -> indigo, as on the site
        t = y / (H - 1)
        c = tuple(round(a + (b - a) * t) for a, b in zip((10, 15, 44), (37, 26, 99)))
        for x in range(W):
            px[x, y] = c
    # the podcast cover art on the right
    cov = Image.open(ROOT / "assets/img/the-dokkcast-cover.jpg").convert("RGB").resize((H, H), Image.LANCZOS)
    img.paste(cov, (W - H - 0, 0))
    # logo + text
    logo = Image.open(io.BytesIO(cairosvg.svg2png(url=str(ROOT / "assets/img/udokk-logo.svg"), output_height=150))).convert("RGBA")
    img.paste(logo, (70, 62), logo)
    d = ImageDraw.Draw(img)
    d.text((70, 335), "Listen and watch", font=font(500, 32), fill=(165, 215, 255))
    d.text((70, 380), "thedokkcast.com", font=font(800, 50), fill="white")
    img.save(ROOT / "assets/img/og-image.png", optimize=True)
    print("wrote assets/img/og-image.png")


if __name__ == "__main__":
    main()
