#!/usr/bin/env python3
"""Generate a high-detail purple graduation-party flyer (HTML) that mirrors the
red template's composition, using the graduate's cut-out photo and event info."""
import base64, os, math

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, "assets", "fonts")
CUTOUT = os.path.join(ROOT, "build", "graduate_cutout.png")

def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def font_face(family, fname, weight="400", style="normal"):
    data = b64(os.path.join(FONTS, fname))
    return (f"@font-face{{font-family:'{family}';src:url(data:font/ttf;base64,{data}) "
            f"format('truetype');font-weight:{weight};font-style:{style};font-display:block;}}")

FACES = "".join([
    font_face("Archivo Black", "ArchivoBlack-Regular.ttf"),
    font_face("Anton", "Anton-Regular.ttf"),
    font_face("Oswald", "Oswald.ttf", "200 700"),
    font_face("Montserrat", "Montserrat.ttf", "100 900"),
    font_face("Montserrat", "Montserrat.ttf", "100 900", "italic"),
    font_face("Dancing Script", "DancingScript.ttf", "400 700"),
    font_face("Great Vibes", "GreatVibes-Regular.ttf"),
    font_face("Barlow Condensed", "BarlowCondensed-Bold.ttf", "700"),
    font_face("Barlow Condensed", "BarlowCondensed-SemiBold.ttf", "600"),
    font_face("Cinzel", "Cinzel.ttf", "400 900"),
    font_face("Playfair Display", "PlayfairDisplay.ttf", "400 900"),
    font_face("Playfair Display", "PlayfairDisplay.ttf", "400 900", "italic"),
])

CUTOUT_B64 = b64(CUTOUT)

# ---- deterministic sparkle / bokeh particles -------------------------------
def sparkles():
    # pseudo-random but fixed layout
    pts = []
    seed = 12345
    def rnd():
        nonlocal seed
        seed = (1103515245 * seed + 12345) & 0x7fffffff
        return seed / 0x7fffffff
    for i in range(90):
        x = rnd() * 100
        y = rnd() * 100
        # keep some clear of dead-center face area
        size = 1 + rnd() * 5
        gold = rnd() > 0.45
        blur = rnd() * 3
        op = 0.25 + rnd() * 0.6
        col = "#ffd870" if gold else "#f3e9ff"
        glow = "#ffbf3a" if gold else "#b98cff"
        pts.append(
            f"<div class='spark' style='left:{x:.2f}%;top:{y:.2f}%;width:{size:.2f}px;height:{size:.2f}px;"
            f"background:{col};filter:blur({blur:.2f}px);opacity:{op:.2f};"
            f"box-shadow:0 0 {6+size*2:.0f}px {glow}'></div>")
    return "".join(pts)

# ---- SVG graduation cap ----------------------------------------------------
def cap(x, y, size, rot, blur=0, op=1.0):
    return f"""<div class="deco" style="left:{x}px;top:{y}px;width:{size}px;transform:rotate({rot}deg);filter:blur({blur}px) drop-shadow(0 10px 14px rgba(0,0,0,.55));opacity:{op}">
    <svg viewBox="0 0 120 90" width="{size}" height="{size*0.75}">
      <defs>
        <linearGradient id="board{x}{y}" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#3a3a44"/><stop offset=".5" stop-color="#101014"/><stop offset="1" stop-color="#000"/>
        </linearGradient>
      </defs>
      <polygon points="60,6 116,30 60,54 4,30" fill="url(#board{x}{y})" stroke="#4a4458" stroke-width="1"/>
      <path d="M28,40 L28,60 Q60,80 92,60 L92,40 L60,56 Z" fill="#15121c" stroke="#3a3346" stroke-width="1"/>
      <polygon points="60,10 110,30 60,50 10,30" fill="#26222e" opacity=".55"/>
      <circle cx="60" cy="30" r="5" fill="#e9b949"/>
      <path d="M60,30 C86,34 96,34 100,30 L100,64" fill="none" stroke="#f0c85a" stroke-width="2.4"/>
      <g transform="translate(100,64)">
        <rect x="-4" y="-2" width="8" height="6" rx="2" fill="#e9b949"/>
        <path d="M-5,4 L5,4 L2,26 L-2,26 Z" fill="#f4cf67"/>
        <path d="M-3,26 L3,26 L2,34 L-2,34 Z" fill="#d8a935"/>
      </g>
    </svg></div>"""

# ---- SVG rolled diploma ----------------------------------------------------
def diploma(x, y, size, rot, blur=0, op=1.0):
    return f"""<div class="deco" style="left:{x}px;top:{y}px;width:{size}px;transform:rotate({rot}deg);filter:blur({blur}px) drop-shadow(0 8px 12px rgba(0,0,0,.5));opacity:{op}">
    <svg viewBox="0 0 120 46" width="{size}" height="{size*0.38}">
      <defs><linearGradient id="pap{x}{y}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#fffdf6"/><stop offset=".5" stop-color="#efe7d4"/><stop offset="1" stop-color="#d9ccb0"/></linearGradient></defs>
      <rect x="10" y="12" width="100" height="22" rx="4" fill="url(#pap{x}{y})" stroke="#cdbd9c" stroke-width="1"/>
      <ellipse cx="10" cy="23" rx="7" ry="12" fill="#f6efdd" stroke="#cdbd9c"/>
      <ellipse cx="110" cy="23" rx="7" ry="12" fill="#f6efdd" stroke="#cdbd9c"/>
      <rect x="40" y="6" width="40" height="34" fill="#7b2ff7" opacity=".92" transform="rotate(8 60 23)"/>
      <rect x="40" y="6" width="40" height="10" fill="#f0c85a" transform="rotate(8 60 23)"/>
    </svg></div>"""

DECO = "".join([
    cap(70, 70, 150, -18, blur=1.2, op=.95),
    cap(880, 95, 165, 22, blur=0.6, op=.97),
    cap(30, 470, 150, -28, blur=3.5, op=.85),
    cap(905, 610, 150, 24, blur=3.2, op=.8),
    diploma(70, 360, 175, -24, blur=1.5, op=.95),
    diploma(860, 380, 175, 20, blur=1.2, op=.95),
])

HTML = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{FACES}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{background:#0b0410}}
#flyer{{position:relative;width:1080px;height:1080px;overflow:hidden;
  background:
    radial-gradient(120% 90% at 50% 34%, rgba(150,70,220,.55) 0%, rgba(96,34,168,.35) 26%, rgba(52,14,96,.2) 46%, rgba(20,6,42,0) 66%),
    radial-gradient(80% 60% at 50% 30%, rgba(190,120,255,.35), rgba(0,0,0,0) 60%),
    linear-gradient(160deg, #2a0a4e 0%, #1c0736 40%, #12042a 70%, #0a0318 100%);
  font-family:'Montserrat',sans-serif;}}
/* grunge + vignette overlays */
.grunge{{position:absolute;inset:0;mix-blend-mode:soft-light;opacity:.5}}
.grunge2{{position:absolute;inset:0;mix-blend-mode:overlay;opacity:.28}}
.vignette{{position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(120% 100% at 50% 42%, rgba(0,0,0,0) 44%, rgba(0,0,0,.55) 82%, rgba(0,0,0,.92) 100%);}}
.frame{{position:absolute;inset:26px;border:2px solid rgba(240,200,90,.42);border-radius:6px;pointer-events:none;
  box-shadow:inset 0 0 60px rgba(0,0,0,.5)}}
.frame:before{{content:'';position:absolute;inset:6px;border:1px solid rgba(240,200,90,.22)}}
.spark{{position:absolute;border-radius:50%}}
.deco{{position:absolute}}
.layer{{position:absolute;left:0;right:0;text-align:center}}

.invite{{top:60px;font-family:'Barlow Condensed';font-weight:600;letter-spacing:11px;
  font-size:25px;color:#f4d27a;text-shadow:0 0 14px rgba(240,200,90,.5)}}
.invite:before,.invite:after{{content:'';display:inline-block;width:46px;height:1px;vertical-align:middle;
  margin:0 16px;background:linear-gradient(90deg,rgba(240,200,90,0),#f0c85a)}}
.invite:after{{background:linear-gradient(90deg,#f0c85a,rgba(240,200,90,0))}}
.classof{{top:92px;font-family:'Archivo Black';font-size:40px;letter-spacing:6px;
  color:#efe7ff;text-shadow:0 2px 0 #4a2f7a,0 0 22px rgba(150,90,230,.6)}}
.classof b{{color:#f4d27a;-webkit-text-stroke:1px rgba(255,255,255,.25)}}

.big{{font-family:'Archivo Black';line-height:.86;
  color:#fff;
  background:linear-gradient(180deg,#ffffff 0%,#f3f0ff 30%,#c9c2dd 52%,#ffffff 60%,#9a92b4 82%,#e7e2f2 100%);
  -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;
  filter:drop-shadow(3px 5px 0 rgba(60,30,100,.55)) drop-shadow(0 14px 26px rgba(0,0,0,.55));}}
.grad{{top:150px;font-size:132px;letter-spacing:2px}}
.party{{top:272px;font-size:170px;letter-spacing:1px}}
/* faux 3D extrusion behind the gradient face */
.big-ext{{position:absolute;left:0;right:0;text-align:center;font-family:'Archivo Black';line-height:.86;
  color:#2a1547;z-index:1;
  text-shadow:1px 1px 0 #241141,2px 2px 0 #221040,3px 3px 0 #1f0e3b,4px 4px 0 #1c0d36,
    5px 5px 0 #190b31,6px 6px 0 #170a2d,7px 7px 0 #150928,8px 9px 12px rgba(0,0,0,.6);}}

.subject{{position:absolute;left:50%;top:224px;transform:translateX(-50%);
  height:620px;z-index:5;
  filter:drop-shadow(0 18px 30px rgba(0,0,0,.6)) drop-shadow(0 0 40px rgba(150,80,230,.45));}}
.subjglow{{position:absolute;left:50%;top:334px;transform:translateX(-50%);
  width:520px;height:560px;z-index:4;border-radius:50%;
  background:radial-gradient(circle,rgba(170,100,240,.5),rgba(120,50,200,.15) 55%,rgba(0,0,0,0) 72%);
  filter:blur(20px)}}
.bottomscrim{{position:absolute;left:0;right:0;bottom:0;height:430px;z-index:6;pointer-events:none;
  background:linear-gradient(180deg,rgba(12,4,26,0) 0%,rgba(12,4,26,.35) 34%,rgba(10,3,22,.72) 62%,rgba(8,2,18,.9) 100%)}}

.saturday{{top:600px;z-index:7;font-family:'Dancing Script';font-weight:700;font-size:124px;line-height:.8;
  color:#fff;text-shadow:0 0 22px rgba(200,150,255,.9),0 0 46px rgba(150,80,230,.7),0 6px 14px rgba(0,0,0,.5)}}
.tag{{top:756px;z-index:8;font-family:'Great Vibes';font-size:56px;color:#f6d98a;line-height:1;
  text-shadow:0 0 18px rgba(240,200,90,.55),0 2px 8px rgba(0,0,0,.65)}}

.honoring{{top:830px;z-index:8;font-family:'Barlow Condensed';font-weight:600;letter-spacing:10px;
  font-size:24px;color:#f4d27a;text-shadow:0 0 12px rgba(240,200,90,.5)}}
.honoring:before,.honoring:after{{content:'';display:inline-block;width:38px;height:1px;vertical-align:middle;margin:0 14px;background:#e9b949;opacity:.7}}
.name{{top:856px;z-index:8;font-family:'Barlow Condensed';font-weight:700;font-style:italic;
  font-size:58px;letter-spacing:1px;color:#fff;
  text-shadow:0 2px 0 #6a4aa0,0 0 20px rgba(150,90,230,.55),0 4px 12px rgba(0,0,0,.5)}}
.degree{{top:922px;z-index:8;font-family:'Barlow Condensed';font-weight:600;letter-spacing:4px;
  font-size:23px;color:#f4d27a}}
.degree b{{color:#fff;font-weight:700}}

/* bottom footer */
.venue{{top:958px;z-index:8;font-family:'Barlow Condensed';font-weight:700;letter-spacing:3px;font-size:26px;color:#fff;
  text-shadow:0 0 12px rgba(150,90,230,.5)}}
.addr-wrap{{top:1000px;z-index:8}}
.addr{{display:inline-block;font-family:'Barlow Condensed';font-weight:600;letter-spacing:2px;
  font-size:23px;line-height:1;color:#1a0636;background:linear-gradient(90deg,#e9b949,#ffe9a8,#f0c85a);
  padding:6px 24px;border-radius:18px;box-shadow:0 5px 14px rgba(0,0,0,.42)}}
.badge{{position:absolute;z-index:8;font-family:'Oswald';font-weight:700;color:#fff;text-align:center;line-height:1;
  display:flex;flex-direction:column;align-items:center}}
.badge.left{{left:52px;top:952px}}
.badge.right{{right:52px;top:952px}}
.badge .big2{{font-size:52px;color:#f4d27a;text-shadow:0 0 14px rgba(240,200,90,.55)}}
.badge .sub{{margin-top:6px;font-size:20px;letter-spacing:6px;color:#efe7ff}}
</style></head><body>
<div id="flyer">
  <svg class="grunge" xmlns="http://www.w3.org/2000/svg"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch"/></filter><rect width="100%" height="100%" filter="url(#n)"/></svg>
  <svg class="grunge2" xmlns="http://www.w3.org/2000/svg"><filter id="n2"><feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="3"/><feColorMatrix values="0 0 0 0 0.15  0 0 0 0 0.05  0 0 0 0 0.28  0 0 0 1 0"/></filter><rect width="100%" height="100%" filter="url(#n2)"/></svg>
  {sparkles()}
  {DECO}
  <div class="vignette"></div>
  <div class="frame"></div>

  <div class="layer invite">YOU ARE CORDIALLY INVITED TO</div>
  <div class="layer classof">CLASS OF <b>2026</b></div>

  <div class="big-ext grad" style="top:150px;font-size:132px;letter-spacing:2px">GRADUATION</div>
  <div class="layer big grad" style="z-index:2">GRADUATION</div>
  <div class="big-ext party" style="top:272px;font-size:170px;letter-spacing:1px">PARTY</div>
  <div class="layer big party" style="z-index:2">PARTY</div>

  <div class="subjglow"></div>
  <img class="subject" src="data:image/png;base64,{CUTOUT_B64}"/>
  <div class="bottomscrim"></div>

  <div class="layer saturday">Saturday</div>
  <div class="layer tag">Let's celebrate this amazing achievement!</div>

  <div class="layer honoring">HONORING</div>
  <div class="layer name">MR HILLARY NWACHUKWU UMEH JR</div>
  <div class="layer degree"><b>MS</b> · INFORMATION TECHNOLOGY MANAGEMENT · <b>GRADUATE</b></div>

  <div class="layer venue">GARDENVILLE RECREATION CENTER</div>
  <div class="layer addr-wrap"><span class="addr">6219 SYMMES RD &middot; GIBSONTON, FL 33534</span></div>

  <div class="badge left"><div class="big2">7&ndash;10</div><div class="sub">PM</div></div>
  <div class="badge right"><div class="big2">15</div><div class="sub">AUG</div></div>
</div>
</body></html>"""

out = os.path.join(ROOT, "build", "flyer.html")
with open(out, "w") as f:
    f.write(HTML)
print("wrote", out, len(HTML), "bytes")
