#!/usr/bin/env python3
"""Gentle, consistent tone adjustment for the site photos.

Reads the untouched originals in assets/img/source/ and writes the versions the site uses to assets/img/.
Originals are never modified, so you can change the settings below and re-run, or drop a hand-edited
file (for example from Canva) straight into assets/img/ and remove that name from PHOTOS.


    pip install pillow numpy
    python3 tools/enhance_photos.py
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC, DST = ROOT / "assets/img/source", ROOT / "assets/img"
# Per-photo overrides of the settings below. The studio photos are dim phone shots and take the full treatment;
# the portrait is already colourful, so it gets a much lighter touch.
PHOTOS = {
    "studio-wide": {}, "studio-behind-the-scenes": {}, "conversation-pair": {}, "group-of-four": {},
    "guests-pair-portrait": {},
    "nara": {"cutoff": 0.05, "contrast": 0.18, "saturation": 0.97, "sharpen": 35},
}

CUTOFF = 0.4      # % of darkest and brightest pixels clipped when stretching the range
CONTRAST = 0.40   # strength of the S-curve (0 = none, 1 = strong)
TARGET_MEAN = 0.46  # dim photos are lifted towards this average brightness
SATURATION = 1.08
SHARPEN = 55      # unsharp mask percent


def enhance(im, cutoff=CUTOFF, contrast=CONTRAST, saturation=SATURATION, sharpen=SHARPEN):
    im = ImageOps.autocontrast(im.convert("RGB"), cutoff=cutoff, preserve_tone=True)
    x = np.asarray(im, dtype=np.float32) / 255.0
    lum = (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2]).mean()
    if lum < TARGET_MEAN:                      # lift only when the photo is dim
        gamma = max(0.78, float(np.log(TARGET_MEAN) / np.log(max(lum, 1e-3))))
        x = x ** gamma
    smooth = x * x * (3 - 2 * x)               # S-curve: deeper darks, brighter lights
    x = x * (1 - contrast) + smooth * contrast
    im = Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8))
    im = ImageEnhance.Color(im).enhance(saturation)
    return im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=sharpen, threshold=2))


def stats(im):
    a = np.asarray(im.convert("L"), dtype=np.float32) / 255
    return f"mean {a.mean():.2f}  spread(p5-p95) {np.percentile(a, 95) - np.percentile(a, 5):.2f}"


if __name__ == "__main__":
    for name, opts in PHOTOS.items():
        src = Image.open(SRC / f"{name}.jpg")
        out = enhance(src, **opts)
        out.save(DST / f"{name}.jpg", quality=84, optimize=True, progressive=True)
        print(f"{name:26s} before: {stats(src)}   after: {stats(out)}")
