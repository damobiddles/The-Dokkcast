#!/usr/bin/env python3
"""Builds the social share image (assets/img/og-image.png, 1200x630): logo and title on the left, studio photo on the right.

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
    # photo panel, scaled to the panel height and cropped around the two people
    ph = Image.open(ROOT / f"assets/img/{PHOTO}.jpg").convert("RGB")
    pw = W - PHOTO_X
    scale = H / ph.height
    ph = ph.resize((round(ph.width * scale), H), Image.LANCZOS)
    left = max(0, min(ph.width - pw, round(ph.width * 0.56 - pw / 2)))
    img.paste(ph.crop((left, 0, left + pw, H)), (PHOTO_X, 0))
    # soft fade from the text panel into the photo
    fade = Image.new("L", (160, H))
    fd = ImageDraw.Draw(fade)
    for x in range(160):
        fd.line([(x, 0), (x, H)], fill=round(255 * (1 - x / 159)))
    base = Image.new("RGB", (160, H))
    bp = base.load()
    for y in range(H):
        t = y / (H - 1)
        c = tuple(round(a + (b - a) * t) for a, b in zip((10, 15, 44), (37, 26, 99)))
        for x in range(160):
            bp[x, y] = c
    img.paste(base, (PHOTO_X, 0), fade)
    # logo + text
    logo = Image.open(io.BytesIO(cairosvg.svg2png(url=str(ROOT / "assets/img/udokk-logo.svg"), output_height=150))).convert("RGBA")
    img.paste(logo, (70, 62), logo)
    d = ImageDraw.Draw(img)
    d.text((70, 250), "The", font=font(800, 92), fill="white")
    d.text((70, 340), "Dokkcast", font=font(800, 92), fill=(117, 192, 251))
    d.text((72, 470), "Evidence-led health podcast", font=font(700, 34), fill="white")
    d.text((72, 518), "Hosted by Dr Nara Daubeney", font=font(500, 30), fill=(165, 215, 255))
    d.text((72, 572), "thedokkcast.com", font=font(500, 26), fill=(180, 189, 219))
    img.save(ROOT / "assets/img/og-image.png", optimize=True)
    print("wrote assets/img/og-image.png")


if __name__ == "__main__":
    main()
