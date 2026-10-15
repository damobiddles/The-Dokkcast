#!/usr/bin/env python3
"""Builds scheduler-ready CSVs for the Episode 14 launch (promo-output/episode-14/schedule/).

    python3 tools/make_schedule.py

One master CSV plus one CSV per channel, in the shape Buffer, Metricool, Later and Hootsuite accept for bulk upload
(columns can be renamed in their import step). Times are Europe/London. Posts are marked HOLD until the CHECK items in
ep14-promo-copy.md are cleared. Image files are named, not linked: bulk uploaders usually want a public URL or a manual attach.
"""
import csv, json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "promo-output/episode-14/schedule"
OUT.mkdir(parents=True, exist_ok=True)
Q = {i + 1: q for i, q in enumerate(json.loads((ROOT / "data/promo/episode-14.json").read_text())["quotes"])}
BASE = "https://thedokkcast.com/blog/episode-14-how-did-we-get-here.html"
link = lambda src, med: f"{BASE}?utm_source={src}&utm_medium={med}&utm_campaign=ep14"
GEN = "General information, not medical advice."
TAGS = "#TheDokkcast #HealthPodcast #Obesity #Cardiology #Prevention"
ALT_KEY = "Dr Nara Daubeney and Professor John Deanfield CBE in conversation on a sofa in The Dokkcast studio. Text: Episode 14, How Did We Get Here? The Rise of Obesity in the UK."
alt_q = lambda n: f"Quote card. {Q[n]['text']} Professor John Deanfield CBE, The Dokkcast Episode 14."
quote = lambda n: f"“{Q[n]['text']}”"
REEL = "highlight reel (your 45-second 9:16 video)"

P = []   # (date, time, channel, type, caption, media, alt)
def add(d, t, ch, typ, cap, media, alt=""): P.append((d, t, ch, typ, cap.strip(), media, alt))

# ---- Thu 15 Oct: launch day
add("2026-10-15", "11:30", "LinkedIn", "Image post", f"""Episode 14 of The Dokkcast is out now.

How Did We Get Here? The Rise of Obesity in the UK, with Professor John Deanfield CBE.

{quote(1)}

In this first conversation in a series, Dr Nara Daubeney and Professor Deanfield cover:
- why this is not a failure of willpower, and what has changed around us
- why obesity is a medical issue, not only a cosmetic one
- why childhood obesity matters so much
- the case for prevention, and what he calls "investing in our arteries"
- where Our Future Health and the NHS fit in

Listen and watch: {link('linkedin','social')}

{GEN}

{TAGS} #PublicHealth""", "ep14_keyart_nowout_portrait_1080x1350.jpg", ALT_KEY)
add("2026-10-15", "11:45", "Instagram", "Feed image", f"""New episode out now. Episode 14: How Did We Get Here? The Rise of Obesity in the UK.

Dr Nara Daubeney talks to Professor John Deanfield CBE about why obesity is a medical issue, not just a cosmetic one, and why it is not a failure of willpower.

{quote(1)}

Listen on Spotify, Apple Podcasts or YouTube. Link in bio.

{GEN}

{TAGS}""", "ep14_keyart_nowout_portrait_1080x1350.jpg", ALT_KEY)
add("2026-10-15", "12:00", "Instagram", "Story", "Episode 14 is out now. (Add a link sticker to the episode.)", "ep14_keyart_nowout_story_1080x1920.jpg", ALT_KEY)
add("2026-10-15", "12:00", "Facebook", "Image post", f"""Episode 14 of The Dokkcast is out now.

How Did We Get Here? The Rise of Obesity in the UK. Dr Nara Daubeney is joined by Professor John Deanfield CBE, a cardiologist at University College London, to talk about why obesity matters for our health, why it is not simply a question of willpower, and what prevention could look like.

Listen and watch: {link('facebook','social')}

{GEN}""", "ep14_keyart_nowout_square_1080x1080.jpg", ALT_KEY)
add("2026-10-15", "12:00", "Facebook", "Story", "Episode 14 is out now.", "ep14_keyart_nowout_story_1080x1920.jpg", ALT_KEY)
add("2026-10-15", "12:15", "X", "Image post", f"""Episode 14 of The Dokkcast is out.

How Did We Get Here? The Rise of Obesity in the UK, with Professor John Deanfield CBE.

Listen and watch: {link('x','social')}""", "ep14_keyart_nowout_link_1200x630.jpg", ALT_KEY)
add("2026-10-15", "13:00", "Instagram", "Reel", "A short highlight from Episode 14 of The Dokkcast, with Professor John Deanfield CBE. Full episode: link in bio.\n\n#TheDokkcast #HealthPodcast", REEL)
add("2026-10-15", "13:00", "TikTok", "Video", "A short highlight from Episode 14 of The Dokkcast, with Professor John Deanfield CBE. Full episode on Spotify, Apple Podcasts and YouTube.\n\n#TheDokkcast #HealthPodcast #Obesity", REEL)
add("2026-10-15", "13:00", "YouTube Shorts", "Short", "A short highlight from Episode 14 of The Dokkcast, with Professor John Deanfield CBE. Full episode on our channel. #TheDokkcast #HealthPodcast", REEL)
add("2026-10-15", "13:30", "LinkedIn", "Video post", f"A 45-second highlight from Episode 14 of The Dokkcast, with Professor John Deanfield CBE.\n\nFull episode: {link('linkedin','social')}\n\n{GEN}", REEL)
add("2026-10-15", "15:00", "X", "Text post", f"On willpower: a collective failure of willpower is very unlikely, he says. What has changed is the world around us: how we eat, work and spend our time.\n\nBoth the individual and the environment matter. “One without the other is not going to work.”", "")
add("2026-10-15", "16:30", "X", "Image post", f"{quote(2)}\n\nProfessor John Deanfield CBE, on The Dokkcast", "ep14_quote2_square_1080x1080.png", alt_q(2))

# ---- later in the week: quote cards
add("2026-10-16", "08:30", "LinkedIn", "Image post", f"{quote(2)}\n\nProfessor John Deanfield CBE on Episode 14 of The Dokkcast, with Dr Nara Daubeney.\n\nListen: {link('linkedin','social')}\n\n{GEN}\n\n{TAGS}", "ep14_quote2_portrait_1080x1350.png", alt_q(2))
add("2026-10-16", "12:00", "Instagram", "Feed image", f"{quote(2)}\n\nProfessor John Deanfield CBE on Episode 14 of The Dokkcast. Link in bio.\n\n{GEN}\n\n{TAGS}", "ep14_quote2_portrait_1080x1350.png", alt_q(2))
add("2026-10-19", "08:30", "LinkedIn", "Image post", f"{quote(4)}\n\nProfessor John Deanfield CBE on Episode 14 of The Dokkcast.\n\nListen: {link('linkedin','social')}\n\n{GEN}\n\n{TAGS}", "ep14_quote4_portrait_1080x1350.png", alt_q(4))
add("2026-10-19", "12:00", "Instagram", "Feed image", f"{quote(4)}\n\nProfessor John Deanfield CBE on Episode 14 of The Dokkcast. Link in bio.\n\n{GEN}\n\n{TAGS}", "ep14_quote4_portrait_1080x1350.png", alt_q(4))
add("2026-10-20", "12:00", "Instagram", "Feed image", f"{quote(3)}\n\nProfessor John Deanfield CBE on Episode 14 of The Dokkcast. Link in bio.\n\n{GEN}\n\n{TAGS}", "ep14_quote3_portrait_1080x1350.png", alt_q(3))
add("2026-10-20", "12:30", "X", "Image post", f"{quote(3)}\n\nEpisode 14 of The Dokkcast: {link('x','social')}", "ep14_quote3_square_1080x1080.png", alt_q(3))
add("2026-10-20", "13:00", "Facebook", "Image post", f"{quote(3)}\n\nProfessor John Deanfield CBE on Episode 14 of The Dokkcast.\n\nListen: {link('facebook','social')}\n\n{GEN}", "ep14_quote3_square_1080x1080.png", alt_q(3))
for ch, t, extra in (("LinkedIn", "08:30", "linkedin"), ("Instagram", "12:00", None), ("Facebook", "12:30", "facebook"), ("X", "13:00", "x")):
    cap = f"{quote(5)}\n\nProfessor John Deanfield CBE on Episode 14 of The Dokkcast. If you missed it, it's out now."
    cap += f"\n\nListen: {link(extra,'social')}" if extra else "\n\nLink in bio."
    if ch != "X": cap += f"\n\n{GEN}"
    add("2026-10-22", t, ch, "Image post" if ch != "Instagram" else "Feed image", cap,
        "ep14_quote5_portrait_1080x1350.png" if ch in ("LinkedIn", "Instagram") else "ep14_quote5_square_1080x1080.png", alt_q(5))

# ---- checks
def xlen(s): return len(re.sub(r"https?://\S+", "x" * 23, s))
bad = [(p[0], p[1], xlen(p[4])) for p in P if p[2] == "X" and xlen(p[4]) > 280]
assert not bad, f"X posts over 280: {bad}"
for p in P:
    assert not p[5] or p[5].startswith("highlight") or (ROOT / "promo-output/episode-14" / p[5]).exists(), p[5]

HEAD = ["publish_date", "publish_time_london", "channel", "post_type", "caption", "media_file", "alt_text", "status", "notes"]
def row(p):
    note = "Wait for the episode to be live on the platform." if p[0] == "2026-10-15" else ""
    if p[2] == "X": note += f" {xlen(p[4])}/280 characters."
    return [*p[:7], "HOLD: confirm guest sign-off and the CHECK items first", note.strip()]
def write(name, rows):
    with open(OUT / name, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(HEAD); w.writerows(rows)
rows = sorted(P, key=lambda p: (p[0], p[1]))
write("ep14_schedule_all.csv", [row(p) for p in rows])
for ch in sorted({p[2] for p in P}):
    write(f"ep14_schedule_{ch.lower().replace(' ', '_')}.csv", [row(p) for p in rows if p[2] == ch])
print(len(P), "posts ->", OUT)

# ---- Buffer bulk-import files: Text, Image URL, Tags, Posting Time (one file per channel, because Buffer imports into one channel at a time)
BUF = OUT / "buffer"
BUF.mkdir(exist_ok=True)
for old in BUF.glob("*"): old.unlink()
SITE_IMG = "https://thedokkcast.com/assets/promo/ep14"   # images are copied here so Buffer can fetch them from a public URL
HOSTED = ROOT / "assets/promo/ep14"
HOSTED.mkdir(parents=True, exist_ok=True)
for p in P:
    if p[5] and not p[5].startswith("highlight") and not p[3].startswith(("Story",)):
        shutil.copy(ROOT / "promo-output/episode-14" / p[5], HOSTED / p[5])
MANUAL_TYPES = ("Story", "Reel", "Video", "Short")        # video and stories are not imported from CSV: attach or schedule them by hand
manual = []
for ch in sorted({p[2] for p in P}):
    rows_ch = [p for p in rows if p[2] == ch and not p[3].startswith(MANUAL_TYPES) and p[3] not in ("Video post",)]
    if rows_ch:
        with open(BUF / f"buffer_{ch.lower().replace(' ', '_')}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["Text", "Image URL", "Tags", "Posting Time"])
            for p in rows_ch: w.writerow([p[4], f"{SITE_IMG}/{p[5]}" if p[5] else "", "ep14,launch", f"{p[0]} {p[1]}"])
    manual += [p for p in rows if p[2] == ch and p not in rows_ch]
with open(BUF / "buffer_attach_images_checklist.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["channel", "posting_time", "attach_this_file", "alt_text", "first_line_of_post"])
    for p in rows:
        if not p[3].startswith(MANUAL_TYPES) and p[3] != "Video post" and p[5]:
            w.writerow([p[2], f"{p[0]} {p[1]}", p[5], p[6], p[4].split("\n")[0][:70]])
with open(BUF / "buffer_schedule_by_hand.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["channel", "type", "posting_time", "media", "caption"])
    for p in manual: w.writerow([p[2], p[3], f"{p[0]} {p[1]}", p[5], p[4]])
print("buffer files ->", BUF, sorted(x.name for x in BUF.iterdir()))
