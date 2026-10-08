#!/usr/bin/env python3
"""Builds the one-page media kit PDF: assets/downloads/the-dokkcast-media-kit.pdf

    pip install playwright          # plus a Chromium (playwright install chromium)
    python3 tools/make_pdf.py       # set CHROMIUM_PATH to use a browser you already have

Links, email and any named guests come from data/site.json and data/guests.json, so re-run this
(and commit the PDF) whenever those change. Unlike tools/build.py this needs a browser, so it is run
by hand and the PDF is committed; Netlify does not build it.
"""
import html, json, os, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/downloads/the-dokkcast-media-kit.pdf"
esc = html.escape


def uri(rel):
    return (ROOT / rel).as_uri()


def link(url, label):
    return f'<a href="{esc(url, True)}">{esc(label)}</a>'


def build_html():
    site = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
    guests = json.loads((ROOT / "data/guests.json").read_text(encoding="utf-8"))
    base = site["site_url"].rstrip("/")
    listen = " &middot; ".join(link(u, k) for k, u in site["listen"].items() if u)
    producer = site.get("producer", {})
    featured = ""
    if guests:
        names = "; ".join(f'<b>{esc(g["name"])}</b>' + (f", {esc(g['title'])}" if g.get("title") else "") for g in guests[:6])
        featured = f'<p class="featured"><span>Guests include</span> {names}</p>'
    font = lambda w: uri(f"assets/fonts/manrope-latin-{w}-normal.woff2")
    return f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8">
<title>The Dokkcast media kit</title>
<style>
@font-face{{font-family:Manrope;font-weight:400;src:url({font(400)})}}
@font-face{{font-family:Manrope;font-weight:500;src:url({font(500)})}}
@font-face{{font-family:Manrope;font-weight:700;src:url({font(700)})}}
@font-face{{font-family:Manrope;font-weight:800;src:url({font(800)})}}
@page{{size:A4;margin:0}}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0}}
body{{font-family:Manrope,sans-serif;color:#eef2ff;font-size:9.3pt;line-height:1.5}}
.page{{width:210mm;height:296.6mm;overflow:hidden;padding:12mm 13mm 9mm;display:flex;flex-direction:column;gap:5mm;
  background:linear-gradient(180deg,#0a0f2c 0,#251a63 100%);-webkit-print-color-adjust:exact;print-color-adjust:exact}}
a{{color:#75c0fb;text-decoration:none}}
h1,h2,p{{margin:0}}
header{{display:flex;align-items:center;gap:6mm}}
header img{{height:20mm;width:auto}}
.kicker{{font-weight:800;font-size:7.6pt;letter-spacing:.16em;color:#75c0fb}}
h1{{font-size:30pt;font-weight:800;line-height:1.05;letter-spacing:-.02em}}
h1 b{{color:#75c0fb}}
.tag{{color:#b4bddb;font-size:10.4pt;margin-top:1mm}}
.intro{{font-size:10.4pt;color:#dde3f7;border-left:1mm solid #5a99f5;padding-left:4mm}}
h2{{font-size:8.2pt;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#75c0fb;margin-bottom:1.6mm}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:4mm}}
.three{{display:grid;grid-template-columns:repeat(3,1fr);gap:3mm}}
.box{{background:rgba(255,255,255,.07);border:.25mm solid rgba(165,215,255,.22);border-radius:3mm;padding:4.2mm 4.6mm}}
.box h3{{margin:0 0 1.2mm;font-size:9.6pt;font-weight:800;color:#fff}}
.host{{display:flex;gap:3.6mm;align-items:flex-start}}
.host img{{width:28mm;height:28mm;border-radius:3mm;object-fit:cover;flex:none}}
.host strong{{display:block;font-size:10.4pt;font-weight:800}}
.host small{{display:block;color:#a5d7ff;font-weight:700;font-size:6.9pt;margin:.4mm 0 1.2mm}}
ul{{margin:0;padding:0;list-style:none}}
li{{padding-left:4mm;position:relative;margin-bottom:1.1mm}}
li::before{{content:"";position:absolute;left:0;top:1.35mm;width:1.9mm;height:1.1mm;border-left:.5mm solid #75c0fb;border-bottom:.5mm solid #75c0fb;transform:rotate(-45deg)}}
.featured{{margin-top:1.8mm;color:#dde3f7}}.featured span{{color:#75c0fb;font-weight:800}}
.muted{{color:#b4bddb}}
.strip{{font-size:8.6pt;color:#b4bddb}}.strip b{{color:#75c0fb}}
footer{{margin-top:auto;border-top:.25mm solid rgba(165,215,255,.3);padding-top:3.4mm;display:grid;grid-template-columns:1.2fr 1fr;gap:5mm;font-size:8.6pt}}
footer p{{margin-bottom:1mm}}
.legal{{grid-column:1/-1;color:#9aa5c7;font-size:6.3pt;line-height:1.4;margin:0!important}}
</style></head><body><div class="page">
<header>
  <img src="{uri('assets/img/udokk-logo.png')}" alt="">
  <div><div class="kicker">MEDIA KIT</div><h1>The <b>Dokkcast</b></h1>
  <p class="tag">An evidence-led health podcast hosted by Dr Nara Daubeney</p></div>
</header>

<p class="intro">Open, accessible conversations with eminent doctors, clinicians, researchers and healthcare specialists, who translate complex medical subjects into information listeners can understand and use. Credible health insight, without hype, fads or misinformation.</p>

<section class="two">
  <div class="box host">
    <img src="{uri('assets/img/nara.jpg')}" alt="">
    <div><h2>Your host</h2><strong>Dr Nara Daubeney</strong><small>CONSULTANT ENT SURGEON &amp; ENTREPRENEUR, LONDON</small>
    <p>PhD in immunology from Imperial College, Fellow of the Royal College of Surgeons, Honorary Secretary of ENTUK and Clinical Lead for Innovation at the Royal Society of Medicine.</p></div>
  </div>
  <div class="box">
    <h2>Our guests</h2>
    <p>Most of our guests are eminent in their fields: doctors, clinicians, researchers and healthcare specialists, chosen for their professional experience, specialist knowledge and ability to explain their work clearly.</p>
    <p class="muted" style="margin-top:2mm">Qualified professionals are given the time and space to discuss their work properly, explain why it matters and consider where their field may be heading next.</p>
    {featured}
  </div>
</section>

<section>
  <h2>Why partner</h2>
  <div class="three">
    <div class="box"><h3>Credibility by association</h3><p class="muted">Your organisation appears alongside eminent, qualified voices in health and medicine.</p></div>
    <div class="box"><h3>Listeners who want reliable information</h3><p class="muted">People come for thoughtful, evidence-led conversation, not hype.</p></div>
    <div class="box"><h3>Editorial integrity protected</h3><p class="muted">Partnerships must fit our audience and protect the programme's credibility.</p></div>
  </div>
</section>

<section class="two">
  <div>
    <h2>Ways to work together</h2>
    <ul>
      <li><b>Episode sponsorship</b>, with wording and disclosure agreed in advance</li>
      <li><b>Expert-led discussions</b> relevant to your field</li>
      <li><b>Product or service features</b> where useful to our audience</li>
      <li><b>Video content</b> developed alongside the show</li>
      <li><b>Wider campaigns</b> across the Udokk platform</li>
    </ul>
  </div>
  <div>
    <h2>How we protect editorial trust</h2>
    <ul>
      <li>Guests chosen for expertise and how clearly they communicate</li>
      <li>Episodes researched, with claims needing verification flagged</li>
      <li>Editorial and factual review before release</li>
      <li>Partner wording, disclosure and a review contact agreed in advance</li>
    </ul>
  </div>
</section>

<section>
  <h2>What every episode becomes</h2>
  <p>The full episode on audio and video platforms &middot; a launch trailer &middot; captioned vertical and landscape clips &middot; an episode page with transcript &middot; launch posts and email &middot; outreach to relevant media, newsletters and communities.</p>
</section>

<p class="strip"><b>Topics</b> &nbsp;Women's health and hormonal change &middot; Metabolic health &middot; Musculoskeletal health &middot; Voice and vocal health &middot; Paediatric and specialist medicine &middot; Mental wellbeing &middot; Exercise and recovery &middot; Prevention and healthier ageing &middot; Medical research</p>

<footer>
  <div>
    <p><b>Listen</b>&nbsp; {listen}</p>
    <p><b>Web</b>&nbsp; {link(base, base.replace("https://", ""))}</p>
    <p class="muted">Brought to you by {link(site["udokk_url"], "Udokk")}</p>
  </div>
  <div>
    <p><b>Press &amp; partnership enquiries</b></p>
    <p>{link("mailto:" + site["email"], site["email"])}</p>
    <p class="muted">Production and marketing: {link(producer.get("url", ""), producer.get("name", ""))}</p>
  </div>
  <p class="legal">The Dokkcast provides general information and education only and does not replace individual medical advice, diagnosis or treatment. &copy; Udokk Ltd. Company number 16772147.</p>
</footer>
</div></body></html>'''


def main():
    from playwright.sync_api import sync_playwright
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp()) / "media-kit.html"
    tmp.write_text(build_html(), encoding="utf-8")
    with sync_playwright() as p:
        exe = os.environ.get("CHROMIUM_PATH")
        browser = p.chromium.launch(**({"executable_path": exe} if exe else {}))
        page = browser.new_page()
        page.goto(tmp.as_uri())
        page.wait_for_timeout(600)
        page.pdf(path=str(OUT), format="A4", print_background=True, margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                 prefer_css_page_size=True)
        browser.close()
    print("wrote", OUT)


if __name__ == "__main__":
    main()
