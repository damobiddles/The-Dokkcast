#!/usr/bin/env python3
"""Draws a month-view calendar graphic of an episode's posting plan.

    python3 tools/make_calendar.py data/promo/episode-14-plan.json     # -> promo-output/<name>.png
"""
import datetime, json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_promo import ROOT, font, gradient, logo, wrap, NAVY, SKY, ICE, MUTED

W, M, GAP = 2400, 60, 14
CW = (W - 2 * M - 6 * GAP) // 7
COL = {"FEED": (117, 192, 251), "STORIES": (113, 107, 232), "VIDEO": (160, 130, 255), "YOUTUBE": (90, 153, 245),
       "EMAIL": (165, 215, 255), "SITE": (150, 160, 190)}
NAMES = {"FEED": "SOCIAL", "STORIES": "STORIES", "VIDEO": "VIDEO", "YOUTUBE": "YOUTUBE", "EMAIL": "EMAIL", "SITE": "WEBSITE"}
LEGEND = {"FEED": "Social posts", "STORIES": "Stories", "VIDEO": "Short video", "YOUTUBE": "YouTube", "EMAIL": "Email", "SITE": "Website"}


def chip_layout(d, chip, width):
    inner = width - 34
    ch = wrap(d, chip["channels"], font(800, 22), inner)
    nt = wrap(d, chip["note"], font(500, 19), inner)
    h = 14 + 19 * 1.2 + 6 + len(ch) * 22 * 1.25 + 3 + len(nt) * 19 * 1.28 + 14
    return ch, nt, h


def rrect(img, box, radius, fill, outline=None, width=0):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    img.alpha_composite(ov)


def main(path):
    plan = json.loads(Path(path).read_text(encoding="utf-8"))
    start = datetime.date.fromisoformat(plan["start"]); release = datetime.date.fromisoformat(plan["release"])
    meas = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    rows = []
    for wk in range(plan["weeks"]):
        cells = []
        for i in range(7):
            day = start + datetime.timedelta(days=wk * 7 + i)
            chips = plan["days"].get(day.isoformat(), [])
            lay = [chip_layout(meas, c, CW - 24) for c in chips]
            cells.append((day, chips, lay, 74 + sum(l[2] + 10 for l in lay) + 8))
        rows.append(cells)
    row_h = [int(max(max(c[3] for c in cells), 190)) + 1 for cells in rows]
    top = 250; H = int(top + 46 + sum(row_h) + GAP * (len(rows) - 1) + 150)
    img = gradient(W, H).convert("RGBA"); d = ImageDraw.Draw(img)
    lg = logo(120); img.alpha_composite(lg, (M, 60))
    d.text((M + lg.width + 34, 52), plan["title"], font=font(800, 74), fill="white")
    d.text((M + lg.width + 34, 146), plan["subtitle"], font=font(500, 33), fill=ICE)
    d.text((W - M, 70), plan["month"].upper(), font=font(800, 34), fill=SKY, anchor="ra")
    y = top
    for i, name in enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]):
        d.text((M + i * (CW + GAP) + 6, y + 8), name, font=font(800, 24), fill=MUTED)
    y += 46
    for cells, rh in zip(rows, row_h):
        for i, (day, chips, lay, _) in enumerate(cells):
            x = M + i * (CW + GAP); box = (x, y, x + CW, y + rh)
            is_rel = day == release; weekend = i >= 5
            rrect(img, box, 22, (255, 255, 255, 30 if is_rel else (10 if weekend else 20)),
                  outline=(117, 192, 251, 255) if is_rel else (165, 215, 255, 50), width=5 if is_rel else 2)
            d = ImageDraw.Draw(img)
            d.text((x + 18, y + 12), str(day.day), font=font(800, 46), fill="white" if (chips or is_rel) else (120, 128, 170))
            if day.day == 1 or (day == start):
                d.text((x + 18 + d.textlength(str(day.day), font=font(800, 46)) + 12, y + 32), day.strftime("%b").upper(), font=font(700, 22), fill=MUTED)
            if is_rel:
                tw = d.textlength("RELEASE DAY", font=font(800, 21))
                rrect(img, (x + CW - tw - 44, y + 16, x + CW - 14, y + 52), 18, (117, 192, 251, 255)); d = ImageDraw.Draw(img)
                d.text((x + CW - 29 - tw, y + 22), "RELEASE DAY", font=font(800, 21), fill=(8, 16, 46))
            cy = y + 74
            for chip, (ch, nt, h) in zip(chips, lay):
                c = COL[chip["type"]]
                rrect(img, (x + 12, cy, x + CW - 12, cy + h), 14, (10, 15, 44, 150)); d = ImageDraw.Draw(img)
                d.rounded_rectangle((x + 12, cy, x + 18, cy + h), radius=3, fill=c)
                tx = x + 30; ty = cy + 13
                d.text((tx, ty), NAMES[chip["type"]], font=font(800, 17), fill=c); ty += 19 * 1.2 + 6
                for l in ch: d.text((tx, ty), l, font=font(800, 22), fill="white"); ty += 22 * 1.25
                ty += 3
                for l in nt: d.text((tx, ty), l, font=font(500, 19), fill=MUTED); ty += 19 * 1.28
                cy += h + 10
        y += rh + GAP
    # legend + footer
    y += 14; x = M
    for k in ("FEED", "STORIES", "VIDEO", "YOUTUBE", "EMAIL", "SITE"):
        d.rounded_rectangle((x, y + 8, x + 26, y + 34), radius=7, fill=COL[k]); d.text((x + 38, y + 5), LEGEND[k], font=font(700, 25), fill="white")
        x += 38 + d.textlength(LEGEND[k], font=font(700, 25)) + 56
    d.text((W - M, y + 5), "thedokkcast.com", font=font(700, 25), fill=ICE, anchor="ra")
    d.text((M, y + 58), "Times of day are your call. Social starts on release day. Quote cards and the highlight reel are in the launch pack.", font=font(500, 24), fill=MUTED)
    out = ROOT / "promo-output"; out.mkdir(exist_ok=True)
    name = Path(path).stem.replace("-plan", "") + "_posting-calendar.png"
    img.convert("RGB").save(out / name, optimize=True); print(out / name, img.size)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/promo/episode-14-plan.json")
