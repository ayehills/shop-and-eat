#!/usr/bin/env python3
"""Generate a high-quality purple graduation "Order of Events" program that
matches the flyer's theme, in two print sizes (4x6 and 8.5x11)."""
import base64, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, "assets", "fonts")

def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def font_face(family, fname, weight="400", style="normal"):
    data = b64(os.path.join(FONTS, fname))
    return (f"@font-face{{font-family:'{family}';src:url(data:font/ttf;base64,{data}) "
            f"format('truetype');font-weight:{weight};font-style:{style};font-display:block;}}")

CUTOUT = os.path.join(ROOT, "assets", "graduate_cutout.png")
if not os.path.exists(CUTOUT):
    CUTOUT = os.path.join(ROOT, "build", "graduate_cutout.png")
CUTOUT_B64 = b64(CUTOUT) if os.path.exists(CUTOUT) else ""

FACES = "".join([
    font_face("Archivo Black", "ArchivoBlack-Regular.ttf"),
    font_face("Oswald", "Oswald.ttf", "200 700"),
    font_face("Montserrat", "Montserrat.ttf", "100 900"),
    font_face("Montserrat", "Montserrat.ttf", "100 900", "italic"),
    font_face("Dancing Script", "DancingScript.ttf", "400 700"),
    font_face("Barlow Condensed", "BarlowCondensed-Bold.ttf", "700"),
    font_face("Barlow Condensed", "BarlowCondensed-SemiBold.ttf", "600"),
])

# ---- deterministic sparkle / bokeh particles -------------------------------
def sparkles(n=80):
    pts = []
    seed = 24680
    def rnd():
        nonlocal seed
        seed = (1103515245 * seed + 12345) & 0x7fffffff
        return seed / 0x7fffffff
    for _ in range(n):
        x = rnd() * 100; y = rnd() * 100
        size = 1 + rnd() * 4.5
        gold = rnd() > 0.45
        blur = rnd() * 2.5
        op = 0.2 + rnd() * 0.55
        col = "#ffd870" if gold else "#f3e9ff"
        glow = "#ffbf3a" if gold else "#b98cff"
        pts.append(
            f"<div class='spark' style='left:{x:.2f}%;top:{y:.2f}%;width:{size:.2f}px;height:{size:.2f}px;"
            f"background:{col};filter:blur({blur:.2f}px);opacity:{op:.2f};"
            f"box-shadow:0 0 {6+size*2:.0f}px {glow}'></div>")
    return "".join(pts)

def cap(x, y, size, rot, blur=0, op=1.0):
    return f"""<div class="deco" style="left:{x:.0f}px;top:{y:.0f}px;width:{size:.0f}px;transform:rotate({rot}deg);filter:blur({blur}px) drop-shadow(0 10px 14px rgba(0,0,0,.55));opacity:{op}">
    <svg viewBox="0 0 120 90" width="{size:.0f}" height="{size*0.75:.0f}">
      <defs><linearGradient id="b{x:.0f}{y:.0f}" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#3a3a44"/><stop offset=".5" stop-color="#101014"/><stop offset="1" stop-color="#000"/></linearGradient></defs>
      <polygon points="60,6 116,30 60,54 4,30" fill="url(#b{x:.0f}{y:.0f})" stroke="#4a4458" stroke-width="1"/>
      <path d="M28,40 L28,60 Q60,80 92,60 L92,40 L60,56 Z" fill="#15121c" stroke="#3a3346" stroke-width="1"/>
      <polygon points="60,10 110,30 60,50 10,30" fill="#26222e" opacity=".55"/>
      <circle cx="60" cy="30" r="5" fill="#e9b949"/>
      <path d="M60,30 C86,34 96,34 100,30 L100,64" fill="none" stroke="#f0c85a" stroke-width="2.4"/>
      <g transform="translate(100,64)"><rect x="-4" y="-2" width="8" height="6" rx="2" fill="#e9b949"/>
        <path d="M-5,4 L5,4 L2,26 L-2,26 Z" fill="#f4cf67"/><path d="M-3,26 L3,26 L2,34 L-2,34 Z" fill="#d8a935"/></g>
    </svg></div>"""

def diploma(x, y, size, rot, blur=0, op=1.0):
    return f"""<div class="deco" style="left:{x:.0f}px;top:{y:.0f}px;width:{size:.0f}px;transform:rotate({rot}deg);filter:blur({blur}px) drop-shadow(0 8px 12px rgba(0,0,0,.5));opacity:{op}">
    <svg viewBox="0 0 120 46" width="{size:.0f}" height="{size*0.38:.0f}">
      <defs><linearGradient id="p{x:.0f}{y:.0f}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#fffdf6"/><stop offset=".5" stop-color="#efe7d4"/><stop offset="1" stop-color="#d9ccb0"/></linearGradient></defs>
      <rect x="10" y="12" width="100" height="22" rx="4" fill="url(#p{x:.0f}{y:.0f})" stroke="#cdbd9c" stroke-width="1"/>
      <ellipse cx="10" cy="23" rx="7" ry="12" fill="#f6efdd" stroke="#cdbd9c"/>
      <ellipse cx="110" cy="23" rx="7" ry="12" fill="#f6efdd" stroke="#cdbd9c"/>
      <rect x="40" y="6" width="40" height="34" fill="#7b2ff7" opacity=".92" transform="rotate(8 60 23)"/>
      <rect x="40" y="6" width="40" height="10" fill="#f0c85a" transform="rotate(8 60 23)"/>
    </svg></div>"""

# ---- agenda items ----------------------------------------------------------
ITEMS = [
    ("Welcome from the MC", "Housekeeping &amp; opening remarks"),
    ("Entrance of the Graduate", "Ushered in by family and friends"),
    ("Opening Prayer &amp; Praise Session", "A moment of thanksgiving"),
    ("Dinner", "Please enjoy the meal"),
    ("The Graduate&rsquo;s Journey", "In his own words"),
    ("Words of Congratulations", "From family &amp; friends"),
    ("Dance Floor Opens", "Celebration &amp; music"),
    ("Cake Cutting &amp; Photos", "Capture the memories"),
    ("Closing Remarks", "Until we meet again"),
]

def deco(w, h):
    s = w / 800.0
    return "".join([
        cap(w*0.015, h*0.012, 118*s, -18, blur=1.0, op=.92),
        cap(w-138*s, h*0.010, 128*s, 20, blur=0.6, op=.94),
        diploma(-18*s, h*0.30, 150*s, -22, blur=1.6, op=.7),
        diploma(w-132*s, h*0.33, 150*s, 20, blur=1.4, op=.7),
        cap(w*0.02, h-150*s, 120*s, -26, blur=3.0, op=.6),
        cap(w-140*s, h-150*s, 120*s, 24, blur=3.0, op=.6),
    ])

def rows():
    out = []
    for title, sub in ITEMS:
        out.append(f"""<div class="item">
      <div class="txt"><div class="it-title">{title}</div></div>
    </div>""")
    return '<div class="divider"></div>'.join(out)

def build(w, h):
    wm = ""
    if CUTOUT_B64:
        ww = int(w * 0.42)                      # watermark width
        wm = (f'<img class="gradwm" style="width:{ww}px;right:26px;bottom:20px" '
              f'src="data:image/png;base64,{CUTOUT_B64}"/>')
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{FACES}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{background:#0b0410}}
#page{{position:relative;width:{w}px;height:{h}px;overflow:hidden;
  background:
    radial-gradient(120% 70% at 50% 12%, rgba(150,70,220,.5) 0%, rgba(96,34,168,.32) 26%, rgba(52,14,96,.18) 48%, rgba(20,6,42,0) 68%),
    radial-gradient(80% 45% at 50% 8%, rgba(190,120,255,.32), rgba(0,0,0,0) 60%),
    linear-gradient(165deg, #2a0a4e 0%, #1c0736 42%, #12042a 72%, #0a0318 100%);
  font-family:'Montserrat',sans-serif}}
.grunge{{position:absolute;inset:0;mix-blend-mode:soft-light;opacity:.45}}
.grunge2{{position:absolute;inset:0;mix-blend-mode:overlay;opacity:.24}}
.vignette{{position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(120% 100% at 50% 40%, rgba(0,0,0,0) 48%, rgba(0,0,0,.5) 84%, rgba(0,0,0,.9) 100%)}}
.frame{{position:absolute;inset:22px;border:2px solid rgba(240,200,90,.45);border-radius:8px;pointer-events:none;
  box-shadow:inset 0 0 60px rgba(0,0,0,.5)}}
.frame:before{{content:'';position:absolute;inset:7px;border:1px solid rgba(240,200,90,.24);border-radius:4px}}
.spark{{position:absolute;border-radius:50%}}
.deco{{position:absolute}}

.content{{position:absolute;inset:52px 46px 46px;z-index:6;display:flex;flex-direction:column;align-items:center}}
.eyebrow{{font-family:'Barlow Condensed';font-weight:600;letter-spacing:8px;font-size:20px;color:#f4d27a;
  text-shadow:0 0 12px rgba(240,200,90,.5)}}
.eyebrow:before,.eyebrow:after{{content:'';display:inline-block;width:34px;height:1px;vertical-align:middle;margin:0 13px;background:#e9b949;opacity:.7}}

.hero-wrap{{position:relative;height:104px;width:100%;margin-top:6px}}
.hero-ext,.hero-face{{position:absolute;left:0;right:0;text-align:center;font-family:'Archivo Black';
  font-size:92px;line-height:1.05;letter-spacing:1px}}
.hero-ext{{color:#2a1547;
  text-shadow:1px 1px 0 #241141,2px 2px 0 #221040,3px 3px 0 #1f0e3b,4px 4px 0 #1c0d36,5px 5px 0 #190b31,6px 7px 10px rgba(0,0,0,.6)}}
.hero-face{{background:linear-gradient(180deg,#ffffff 0%,#f3f0ff 30%,#c9c2dd 52%,#ffffff 60%,#9a92b4 82%,#e7e2f2 100%);
  -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;
  filter:drop-shadow(2px 4px 0 rgba(60,30,100,.5)) drop-shadow(0 12px 22px rgba(0,0,0,.5))}}

.script{{font-family:'Dancing Script';font-weight:700;font-size:52px;color:#f6d98a;line-height:1;margin-top:2px;
  text-shadow:0 0 18px rgba(240,200,90,.55),0 2px 8px rgba(0,0,0,.6)}}
.honoree{{font-family:'Barlow Condensed';font-weight:700;font-style:italic;font-size:34px;letter-spacing:1px;color:#fff;
  margin-top:12px;text-shadow:0 2px 0 #6a4aa0,0 0 18px rgba(150,90,230,.5)}}
.datebar{{margin-top:12px;font-family:'Barlow Condensed';font-weight:700;letter-spacing:3px;font-size:19px;
  color:#1a0636;background:linear-gradient(90deg,#e9b949,#ffe9a8,#f0c85a);padding:6px 26px;border-radius:16px;
  box-shadow:0 5px 14px rgba(0,0,0,.4)}}

.listpanel{{flex:1;width:100%;margin-top:22px;display:flex;flex-direction:column;
  background:linear-gradient(180deg,rgba(34,14,66,.5),rgba(15,6,32,.58));
  border:1px solid rgba(240,200,90,.32);border-radius:16px;
  box-shadow:inset 0 0 46px rgba(0,0,0,.45),0 10px 30px rgba(0,0,0,.35);
  padding:8px 34px}}
.item{{flex:1;display:flex;align-items:center;justify-content:center;text-align:center}}
.txt{{width:100%}}
.it-title{{font-family:'Barlow Condensed';font-weight:600;font-size:38px;letter-spacing:3px;color:#fff;
  text-transform:uppercase;line-height:1.02;text-shadow:0 1px 6px rgba(0,0,0,.45)}}
.it-sub{{font-family:'Barlow Condensed';font-weight:600;font-style:italic;font-size:19px;letter-spacing:.5px;
  color:#f0cf88;margin-top:1px}}
.divider{{height:1px;background:linear-gradient(90deg,rgba(240,200,90,0),rgba(240,200,90,.35) 20%,rgba(240,200,90,.35) 80%,rgba(240,200,90,0));
  margin:0 -6px}}

.footer{{margin-top:16px;font-family:'Barlow Condensed';font-weight:600;letter-spacing:3px;font-size:18px;color:#e9c877;
  text-align:center;text-shadow:0 0 10px rgba(240,200,90,.4)}}
.footer .v{{color:#fff;font-weight:700}}

.gradwm{{position:absolute;z-index:7;pointer-events:none;opacity:.30;
  filter:saturate(.9) drop-shadow(0 0 18px rgba(150,80,230,.4));
  -webkit-mask-image:linear-gradient(to top left, rgba(0,0,0,1) 26%, rgba(0,0,0,.55) 55%, rgba(0,0,0,0) 82%);
  mask-image:linear-gradient(to top left, rgba(0,0,0,1) 26%, rgba(0,0,0,.55) 55%, rgba(0,0,0,0) 82%)}}
</style></head><body>
<div id="page">
  <svg class="grunge" xmlns="http://www.w3.org/2000/svg"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/></filter><rect width="100%" height="100%" filter="url(#n)"/></svg>
  <svg class="grunge2" xmlns="http://www.w3.org/2000/svg"><filter id="n2"><feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="3"/><feColorMatrix values="0 0 0 0 0.15  0 0 0 0 0.05  0 0 0 0 0.28  0 0 0 1 0"/></filter><rect width="100%" height="100%" filter="url(#n2)"/></svg>
  {sparkles()}
  {deco(w,h)}
  <div class="vignette"></div>
  <div class="frame"></div>

  <div class="content">
    <div class="eyebrow">CLASS OF 2026 &middot; GRADUATION CELEBRATION</div>
    <div class="hero-wrap"><div class="hero-ext">PROGRAM</div><div class="hero-face">PROGRAM</div></div>
    <div class="script">Order of Events</div>
    <div class="honoree">MR HILLARY NWACHUKWU UMEH JR</div>
    <div class="datebar">SATURDAY &middot; 15 AUGUST 2026 &middot; 7&ndash;10 PM</div>

    <div class="listpanel">
    {rows()}
    </div>

    <div class="footer"><span class="v">GARDENVILLE RECREATION CENTER</span> &middot; 6219 SYMMES RD, GIBSONTON, FL 33534</div>
  </div>
  {wm}
</div>
</body></html>"""

SIZES = {"4x6": (800, 1200), "85x11": (850, 1100)}

if __name__ == "__main__":
    for name, (w, h) in SIZES.items():
        html = build(w, h)
        out = os.path.join(ROOT, "build", f"agenda_{name}.html")
        with open(out, "w") as f:
            f.write(html)
        print("wrote", out, len(html), "bytes")
