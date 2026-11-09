#!/usr/bin/env python3
"""Generate board1/2/3.html (1600x1200 CSS px) for Chibees contest #2801274. Run prep_assets.py first."""
import json, pathlib, re

R = pathlib.Path(__file__).resolve().parent.parent
G = "board_build/gen"
LAYERS = json.load(open(R / G / "layers.json"))

BASE_CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1600px;height:1200px;overflow:hidden}
body{position:relative;font-family:'Avenir Next','Helvetica Neue',Helvetica,Arial,sans-serif;color:#231915;-webkit-font-smoothing:antialiased}
.disp{font-family:Didot,'Bodoni 72','Playfair Display',Georgia,serif}
.cond{font-family:'Avenir Next Condensed','Helvetica Neue',Arial Narrow,sans-serif;text-transform:uppercase;letter-spacing:.14em;font-weight:600}
.abs{position:absolute}
"""

HEAD = ('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{t}</title><style>{c}</style></head><body>')


def write(name, title, css, body):
    (R / name).write_text(HEAD.format(t=title, c=BASE_CSS + css) + body + "</body></html>", encoding="utf-8")
    print("wrote", name)


# ───────────────────────── BOARD 1 ─────────────────────────
B1_CSS = r"""
body{background:#F4EEE4}
.stage{position:absolute;left:0;top:0;width:1600px;height:792px;overflow:hidden;
 background:radial-gradient(900px 560px at 50% 52%,#4A2C30 0%,#331E22 48%,#231618 100%)}
.stage:after{content:"";position:absolute;inset:0;background:radial-gradient(1400px 800px at 50% 50%,transparent 55%,rgba(0,0,0,.45) 100%)}
.hdr{position:absolute;left:0;right:0;top:20px;text-align:center;z-index:3;color:#F2B322;font-size:15px;letter-spacing:.22em;white-space:nowrap}
.hdr2{position:absolute;left:0;right:0;top:48px;text-align:center;z-index:3;color:rgba(250,248,244,.7);font-size:12.5px;letter-spacing:.3em}
.sign{position:absolute;left:50%;top:92px;height:660px;transform:translateX(-50%);z-index:2;
 filter:drop-shadow(0 0 70px rgba(242,179,34,.30)) drop-shadow(0 34px 38px rgba(0,0,0,.65))}
.strip{position:absolute;left:0;top:792px;width:1600px;height:408px;background:#F4EEE4;border-top:6px solid #DB3124;
 display:grid;grid-template-columns:1fr 1fr 1fr;gap:26px;padding:14px 28px 0}
.pn{position:relative;min-width:0}
.pt{font-size:13.5px;letter-spacing:.16em;color:#231915;padding-bottom:7px;border-bottom:2px solid #231915;margin-bottom:10px;display:flex;justify-content:space-between}
.pt i{font-style:normal;color:#DB3124}
.fx{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.fx figure{position:relative;margin:0}
.fx img{display:block;width:100%;height:136px;object-fit:cover;border:1px solid rgba(35,25,21,.35)}
.fx .l{position:absolute;left:0;bottom:0;font-size:9.5px;letter-spacing:.12em;padding:3px 7px;color:#fff}
.bad{background:#DB3124}.good{background:#1E823A}
.ring{position:absolute;width:44px;height:44px;border:2.5px solid #DB3124;border-radius:50%;box-shadow:0 0 0 1px #fff}
.cap{font-size:10px;letter-spacing:.1em;color:#5A4A44;margin:4px 0 8px;line-height:1.4}
.ctr img{display:block;width:100%;height:285px;object-fit:cover;object-position:50% 52%;border:1px solid #0b1118}
.cap2{font-size:11px;letter-spacing:.1em;color:#231915;line-height:1.55;margin-top:8px;text-align:center}
.sw{display:grid;grid-template-columns:50px 1fr;gap:12px;align-items:center;height:53px;border-bottom:1px solid rgba(35,25,21,.18)}
.sw .c{width:50px;height:38px;border:1px solid rgba(35,25,21,.5);border-radius:3px}
.sw b{display:block;font-size:14px;letter-spacing:.02em;font-weight:700}
.sw span{display:block;font-size:11.5px;color:#4A3C36;letter-spacing:.02em;margin-top:2px;font-variant-numeric:tabular-nums}
"""


def board1():
    sw = [
        ("Fiesta Chili Red", "#DB3124", "C:0 M:92 Y:95 K:0", "Pantone 485 C / 1795 C"),
        ("Jalapeño Green", "#1E823A", "C:84 M:0 Y:85 K:23", "Pantone 355 C"),
        ("Marigold Gold", "#F2B322", "C:0 M:20 Y:95 K:0", "Pantone 1235 C"),
        ("Amber Sombrero Shade", "#CE8420", "C:12 M:48 Y:95 K:2", "Pantone 7563 C"),
        ("Espresso Linework / Rich Black", "#181311", "C:40 M:50 Y:50 K:90", "Pantone Black 6 C"),
        ("Warm Acrylic Cabinet", "#FAF8F4", "C:0 M:1 Y:4 K:1", "Woodgrain + Neon Halo Layers Included"),
    ]
    rows = "".join(
        f'<div class="sw"><div class="c" style="background:{h}"></div><div><b>{n}</b>'
        f'<span>{h} &nbsp;·&nbsp; {c}</span><span>{p}</span></div></div>' for n, h, c, p in sw)
    body = f"""
<div class="stage">
 <div class="hdr cond">Exact 1:1 Cubic Bézier Vector Reconstruction · Zero Auto-Trace · 100% Outlined Fonts</div>
 <div class="hdr2 cond">CMYK + Pantone + AI / EPS / PDF / SVG / DXF</div>
 <img class="sign" src="{G}/cut_exact.png">
</div>
<div class="strip">
 <div class="pn">
  <div class="pt cond"><span>Forensic Zoom Audit</span><i>Photo → Vector</i></div>
  <div class="fx">
   <figure><img src="{G}/fx_ref.png"><span class="ring" style="left:150px;top:62px"></span><span class="l cond bad">Monitor photo · moiré + cursor</span></figure>
   <figure><img src="{G}/fx_vec.png"><span class="l cond good">Pure Bézier · cursor removed</span></figure>
  </div>
  <div class="cap cond">Twin “ee” + sombrero brim, same region</div>
  <div class="fx">
   <figure><img src="{G}/loupe_ref.png"><span class="l cond bad">Loupe · LCD grid + “+”</span></figure>
   <figure><img src="{G}/loupe_vec.png"><span class="l cond good">Loupe · razor-sharp curves</span></figure>
  </div>
 </div>
 <div class="pn ctr">
  <div class="pt cond"><span>Ctrl+Y Outline &amp; Node Blueprint</span><i>Illustrator view</i></div>
  <img src="assets/render_ctrly_svg.png">
  <div class="cap2 cond">7 named layers · 741 anchor endpoints · 369 cubic segments<br>0 &lt;text&gt; dependencies · 0 linked bitmaps</div>
 </div>
 <div class="pn">
  <div class="pt cond"><span>Print Color Specifications</span><i>CMYK + Pantone</i></div>
  {rows}
 </div>
</div>"""
    write("board1.html", "Chibees Board 1", B1_CSS, body)


# ───────────────────────── BOARD 2 ─────────────────────────
B2_CSS = r"""
body{background:linear-gradient(180deg,#F6F0E6 0%,#EDE4D6 100%)}
.top{position:absolute;left:0;top:0;width:1600px;height:744px}
.hd{position:absolute;left:28px;top:18px;right:28px;display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px solid #231915;padding-bottom:7px}
.hd h1{font-size:25px;font-weight:400;letter-spacing:.01em}
.hd span{font-size:12px;color:#DB3124}
.mock{position:absolute;left:24px;top:70px;width:1010px;height:564px;overflow:hidden;border-radius:4px;box-shadow:0 14px 36px rgba(35,25,21,.35)}
.mw{position:absolute;left:0;top:0;width:1376px;height:768px;transform:scale(.7340);transform-origin:0 0}
.mw>img{position:absolute;left:0;top:0;width:1376px;height:768px}
.lg{position:absolute;filter:drop-shadow(0 1.5px 1.5px rgba(0,0,0,.4))}
.lg i{position:absolute;inset:0;mix-blend-mode:multiply;opacity:.42}
.mtxt{position:absolute;left:548px;width:314px;text-align:center;color:#E8B84A;text-shadow:0 1px 2px rgba(0,0,0,.6)}
.mcap{position:absolute;left:24px;top:644px;width:1010px;display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.mcap div{font-size:10.5px;letter-spacing:.1em;line-height:1.45;color:#4A3C36;border-top:1.5px solid #231915;padding-top:6px}
.mcap b{display:block;color:#231915;font-size:11.5px;letter-spacing:.12em}
.fac{position:absolute;left:1054px;width:522px;height:313px;overflow:hidden;border-radius:4px;box-shadow:0 12px 30px rgba(35,25,21,.35)}
.fw{position:absolute;left:0;top:0;width:1100px;height:660px;transform:scale(.4745);transform-origin:0 0}
.fw>img{position:absolute;left:0;top:0;width:1100px;height:660px}
.fw .s{position:absolute;left:313px;top:75px;width:394px;height:auto}
.tag{position:absolute;left:12px;bottom:10px;z-index:4;background:rgba(24,19,17,.82);color:#F2B322;font-size:10.5px;padding:5px 9px}
.tag2{position:absolute;right:12px;top:10px;z-index:4;background:#DB3124;color:#fff;font-size:10.5px;padding:5px 9px}
.bot{position:absolute;left:0;top:744px;width:1600px;height:456px;background:#231618;padding:20px 28px 0;color:#FAF8F4}
.bot h2{font-size:13.5px;color:#F2B322;display:flex;justify-content:space-between;border-bottom:1px solid rgba(242,179,34,.5);padding-bottom:7px;margin-bottom:14px}
.bot h2 i{font-style:normal;color:rgba(250,248,244,.65)}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
.card .im{height:292px;border-radius:3px;overflow:hidden;display:flex;align-items:center;justify-content:center;border:1px solid rgba(250,248,244,.18)}
.card .im img{width:100%;height:100%;object-fit:cover;display:block}
.chk{background-color:#fff;background-image:linear-gradient(45deg,#d9d2c8 25%,transparent 25%,transparent 75%,#d9d2c8 75%),linear-gradient(45deg,#d9d2c8 25%,transparent 25%,transparent 75%,#d9d2c8 75%);background-size:20px 20px;background-position:0 0,10px 10px}
.card .n{margin-top:11px;font-size:14px;letter-spacing:.1em}
.card .n b{color:#F2B322;font-weight:700}
.card p{margin-top:5px;font-size:11.5px;line-height:1.45;color:rgba(250,248,244,.72);letter-spacing:.02em}
"""


def chevron(w, h, tri=22):
    cols = ["#DB3124", "#1E823A", "#F2B322"]
    n = int(w // tri) + 1
    pts = "".join(
        f'<polygon points="{i*tri},{h} {i*tri+tri/2},{h*0.15} {i*tri+tri},{h}" fill="{cols[i%3]}"/>' for i in range(n))
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect y="{h-5}" width="{w}" height="5" fill="#181311"/>{pts}</svg>')


def lg(src, cx, cy, w, ratio, shade=True, extra=""):
    h = w / ratio
    x, y = cx - w / 2, cy - h / 2
    sh = (f'<i style="background:url(assets/collateral_mockup_base.jpg) -{x:.1f}px -{y:.1f}px/1376px 768px no-repeat;'
          f'-webkit-mask:url({src}) center/100% 100% no-repeat"></i>') if shade else ""
    return (f'<div class="lg" style="left:{x:.1f}px;top:{y:.1f}px;width:{w}px;height:{h:.1f}px;{extra}">'
            f'<img src="{src}" style="width:100%;height:100%;display:block">{sh}</div>')


def board2():
    from PIL import Image
    def ar(p):
        w, h = Image.open(R / p).size
        return w / h
    a_tr, a_ex, a_fr, a_mo = (ar(f"{G}/transparent_crop.png"), ar(f"{G}/cut_exact.png"),
                              ar(f"{G}/cut_framed.png"), ar(f"{G}/cut_mono.png"))
    bag = lg(f"{G}/transparent_crop.png", 272, 462, 262, a_tr)
    # chevron strip along bag bottom edge (bag base slants ~3 deg)
    strip = (f'<div class="lg" style="left:90px;top:603px;width:366px;height:26px;transform:rotate(3.3deg);transform-origin:0 0;'
             f'mix-blend-mode:multiply;opacity:.92;filter:none">{chevron(366, 26)}</div>')
    menu = lg(f"{G}/cut_exact.png", 705, 336, 256, a_ex, shade=False,
              extra="filter:drop-shadow(0 0 14px rgba(242,179,34,.25)) drop-shadow(0 3px 4px rgba(0,0,0,.6))")
    menutxt = ('<div class="mtxt cond" style="top:446px;font-size:15px;letter-spacing:.34em">Menú Auténtico · Est. 2026</div>'
               '<div class="abs" style="left:620px;top:436px;width:170px;height:1.5px;background:#E8B84A;opacity:.8"></div>'
               '<div class="abs" style="left:620px;top:474px;width:170px;height:1.5px;background:#E8B84A;opacity:.8"></div>')
    st1 = lg(f"{G}/cut_framed.png", 990, 308, 122, a_fr)
    st2 = lg(f"{G}/cut_mono.png", 994, 540, 126, a_mo)
    mock = f'<div class="mock"><div class="mw"><img src="assets/collateral_mockup_base.jpg">{bag}{strip}{menu}{menutxt}{st1}{st2}</div></div>'

    glow_day = "filter:drop-shadow(0 6px 7px rgba(0,0,0,.55))"
    day = (f'<div class="fac" style="top:70px"><div class="fw"><img src="{G}/facade_day.jpg">'
           f'<img class="s" src="{G}/cut_exact.png" style="{glow_day}"></div>'
           f'<span class="tag cond">50″ Exterior Sign · Day</span></div>')
    night = (f'<div class="fac" style="top:395px"><div class="fw">'
             f'<img src="{G}/facade_day.jpg" style="filter:brightness(.26) contrast(1.15) saturate(.55) hue-rotate(-12deg)">'
             f'<div class="abs" style="inset:0;background:linear-gradient(180deg,rgba(14,22,48,.62),rgba(10,12,28,.35))"></div>'
             f'<div class="abs" style="left:150px;top:-40px;width:800px;height:520px;background:radial-gradient(closest-side,rgba(255,196,110,.55),rgba(255,150,60,.20) 55%,transparent 100%);mix-blend-mode:screen"></div>'
             f'<img class="s" src="{G}/cut_exact.png" style="filter:drop-shadow(0 0 26px rgba(255,214,140,.75)) drop-shadow(0 0 80px rgba(255,150,60,.5))">'
             f'</div><span class="tag cond">Perspective by Night · Backlit Halo</span></div>')
    mcap = ('<div class="mcap cond"><div><b>Kraft takeaway bag</b>Transparent lockup + fiesta chevron</div>'
            '<div><b>Menu folder</b>Exact master, gold foil caps</div>'
            '<div><b>Arch sticker · top</b>Framed print, die-cut</div>'
            '<div><b>Arch sticker · bottom</b>1-color espresso stamp</div></div>')

    cards = [
        ("01", "Exact Backlit Sign Cabinet Master", "assets/render_exact_svg.png", "",
         "Warm acrylic face, subtle woodgrain, neon-glow layer."),
        ("02", "Framed Print &amp; Die-Cut Sticker Master", "assets/render_framed_svg.png", "",
         "Dark #231915 contour border for bleed and cutline."),
        ("03", "Transparent Isolate Lockup", "assets/render_transparent_svg.png", "chk",
         "White keyline for kraft paper, dark menus and apparel."),
        ("04", "1-Color Screen-Print &amp; Vinyl Master", "assets/render_mono_svg.png", "",
         "Single-ink stamp, embossing and CNC decal."),
    ]
    cc = "".join(
        f'<div class="card"><div class="im {k}"><img src="{s}"></div><div class="n cond"><b>{n} ·</b> {t}</div><p>{d}</p></div>'
        for n, t, s, k, d in cards)
    body = f"""
<div class="top">
 <div class="hd"><h1 class="disp">Chibees — In Use: Packaging, Print &amp; Storefront</h1><span class="cond">Freelancer Contest #2801274 · Mexican Restaurant Sign Vectorization</span></div>
 {mock}{mcap}{day}{night}
</div>
<div class="bot">
 <h2 class="cond"><span>Four Production Master Variations</span><i>All SVG · pure cubic Bézier · outlined type</i></h2>
 <div class="grid">{cc}</div>
</div>"""
    write("board2.html", "Chibees Board 2", B2_CSS, body)


# ───────────────────────── BOARD 3 ─────────────────────────
B3_CSS = r"""
body{background:linear-gradient(180deg,#F6F0E6,#EDE4D6)}
.hd{position:absolute;left:28px;right:28px;top:18px;display:flex;justify-content:space-between;align-items:baseline;border-bottom:2px solid #231915;padding-bottom:7px}
.hd h1{font-size:25px;font-weight:400}
.hd span{font-size:12px;color:#DB3124}
.stack{position:absolute;left:28px;top:70px;width:690px;height:620px;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);grid-template-rows:repeat(4,1fr);gap:8px}
.cell{display:grid;grid-template-columns:200px 1fr;gap:12px;align-items:center;background:#EFE8DC;border:1px solid rgba(35,25,21,.25);padding:8px;border-radius:3px}
.cv{width:200px;height:122px;background:#B9AE9E;border-radius:2px;overflow:hidden}
.cv svg{width:100%;height:100%;display:block}
.ct{min-width:0}
.ct em{font-style:normal;color:#DB3124;font-size:18px;display:block;margin-bottom:4px}
.ct b{display:block;font-size:10.5px;line-height:1.3;overflow-wrap:anywhere}
.ct span{display:block;font-size:10.5px;color:#5A4A44;margin-top:5px}
.stack .ly{position:absolute;left:60px;top:150px;width:520px;height:312px;transform-style:preserve-3d}
.plane{position:absolute;left:0;top:0;width:520px;height:312px;transform-origin:50% 50%}
.plane svg{width:100%;height:100%;overflow:visible}
.stack .lab{position:absolute;right:16px;font-size:11px;color:#FAF8F4;letter-spacing:.1em;display:flex;gap:8px;align-items:center}
.stack .lab em{font-style:normal;color:#F2B322}
.stk{position:absolute;left:14px;top:12px;color:#F2B322;font-size:11.5px;z-index:2}
.tbl{position:absolute;left:744px;top:70px;width:828px;height:620px}
table{border-collapse:collapse;width:100%}
th{font-size:11px;text-align:left;padding:7px 8px;background:#231915;color:#F2B322}
td{font-size:12.5px;padding:0 8px;height:52px;border-bottom:1px solid rgba(35,25,21,.22);vertical-align:middle;letter-spacing:.01em}
td.n{font-weight:700;width:36px;color:#DB3124;font-variant-numeric:tabular-nums}
td.m{width:70px;font-variant-numeric:tabular-nums;text-align:right}
td b{font-size:13px}
td small{display:block;color:#5A4A44;font-size:11px;margin-top:2px}
.chips{margin-top:12px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.chips span{font-size:10px;padding:4px 8px;border:1px solid #231915;letter-spacing:.1em}
.sec{position:absolute;top:712px;height:466px}
.sec h2{font-size:13px;letter-spacing:.14em;padding-bottom:7px;border-bottom:2px solid #231915;margin-bottom:10px;display:flex;justify-content:space-between}
.sec h2 i{font-style:normal;color:#DB3124}
.sets{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.set{background:#231618;color:#FAF8F4;padding:12px;border-radius:3px;height:412px}
.set h3{font-size:12.5px;color:#F2B322;margin-bottom:8px;letter-spacing:.1em;line-height:1.35}
.set .two{display:grid;gap:8px}
.set img{display:block;width:100%;border:1px solid rgba(250,248,244,.2)}
.set .two img{height:150px;object-fit:contain}
.set .two img:first-child{background:#281A1D}.set .two img:last-child{background:#09111A}
.set p{font-size:11px;line-height:1.5;margin-top:8px;color:rgba(250,248,244,.78);letter-spacing:.02em}
.ft{font-size:10.5px;color:#5A4A44;margin-top:8px;line-height:1.5;letter-spacing:.03em}
"""

LAYER_META = [
    ("01_Cabinet_Arch", "Warm acrylic arched cabinet", 1, 14, "#FAF8F4"),
    ("02_Woodgrain_And_Neon_FX", "Woodgrain lines (authored at 3.5% opacity) + neon-glow display layer", 17, 102, "#F2B322"),
    ("03_Sombrero_Crest", "Base · Marigold · Amber shade · Green · Red · Espresso linework", 48, 261, "#1E823A"),
    ("04_Splash_Accents_RGB_Order", "Red top / Green middle / Yellow bottom, both sides", 6, 24, "#DB3124"),
    ("05_Wordmark_Chibees_Outlined", "Custom arched “Chibees” outlines", 8, 100, "#DB3124"),
    ("06_Golden_Swoosh", "Tapered golden arch", 1, 3, "#F2B322"),
    ("07_Subtitle_Mexican_Restaurant_Outlined", "“MEXICAN RESTAURANT” outlines", 1, 237, "#181311"),
]


def layer_svg(idx):
    frag = re.sub(r'\sid="[^"]*"', '', LAYERS[LAYER_META[idx][0]])
    if idx == 1:  # woodgrain is authored at ~3.5% opacity; boost for the thumbnail only
        frag = re.sub(r'opacity="0\.\d+"', 'opacity="0.9"', frag)
    return f'<svg viewBox="80 95 1040 640" xmlns="http://www.w3.org/2000/svg">{frag}</svg>'


def board3():
    cells = ""
    for i, (nm, d, p, a, _c) in enumerate(LAYER_META):
        bg = ' style="background:#FAF8F4"' if i == 1 else ''
        cells += (f'<div class="cell"><div class="cv"{bg}>{layer_svg(i)}</div>'
                  f'<div class="ct"><em class="cond">{i+1:02d}</em><b>{nm}</b><span>{p} paths · {a} anchors</span></div></div>')
    comp = "".join(re.sub(r'\sid="[^"]*"', '', LAYERS[m[0]]) for m in LAYER_META)
    cells += (f'<div class="cell" style="background:#231618"><div class="cv" style="background:#2B1D20"><svg viewBox="80 95 1040 640" xmlns="http://www.w3.org/2000/svg">{comp}</svg></div>'
              f'<div class="ct"><em class="cond" style="color:#F2B322">ALL</em><b style="color:#FAF8F4">Stacked master</b><span style="color:rgba(250,248,244,.7)">82 paths · 741 anchors</span></div></div>')
    stack = f'<div class="stack">{cells}</div>'

    rows = "".join(
        f'<tr><td class="n">{i+1:02d}</td><td><b>{nm}</b><small>{d}</small></td>'
        f'<td class="m">{p}</td><td class="m">{a}</td></tr>'
        for i, (nm, d, p, a, _c) in enumerate(LAYER_META))
    tot_p = sum(m[2] for m in LAYER_META); tot_a = sum(m[3] for m in LAYER_META)
    chips = "".join(f'<span class="cond">{c}</span>' for c in
                    ["Sombrero_Base", "Sombrero_Marigold", "Sombrero_Amber_Shade", "Sombrero_Jalapeno_Green",
                     "Sombrero_Fiesta_Red", "Sombrero_Linework"])
    tbl = (f'<div class="tbl"><table><tr><th class="cond">#</th><th class="cond">Illustrator layer</th>'
           f'<th class="cond" style="text-align:right">Paths</th><th class="cond" style="text-align:right">Anchors</th></tr>'
           f'{rows}<tr><td></td><td><b>Total</b><small>7 layers · 0 text · 0 raster</small></td>'
           f'<td class="m"><b>{tot_p}</b></td><td class="m"><b>{tot_a}</b></td></tr></table>'
           f'<div class="chips"><span class="cond" style="background:#231915;color:#F2B322">03 sub-layers</span>{chips}</div></div>')

    sets = f"""
<div class="sec" style="left:28px;width:900px">
 <h2 class="cond"><span>Dual Vector Master Sets · One ZIP</span><i>Exact photo-matched + geometric CAD</i></h2>
 <div class="sets">
  <div class="set"><h3 class="cond">Master Set A — 1:1 Exact Photo-Matched Cubic Bézier</h3>
   <div class="two" style="grid-template-columns:1fr"><img src="assets/render_exact_svg.png"><img src="assets/render_ctrly_svg.png"></div>
   <p>Exact cabinet render + Ctrl+Y outline blueprint. Both “e” glyphs share one clean outline; no cursor path exists.</p></div>
  <div class="set"><h3 class="cond">Master Set B — Precision Geometric CAD</h3>
   <img src="verification/PDF_Proofs.jpg" style="width:92%;margin:0 auto">
   <p>4-page CMYK specification book + 50″ (1270 mm) AutoCAD R2010 DXF, 106 closed LWPOLYLINE contours.</p></div>
 </div>
</div>"""
    chk_rows = [
        (".AI", "Layered Adobe Illustrator exchange file", "7 optional-content layers · 82 vector objects"),
        (".EPS", "PostScript Level 3, process CMYK", "No fonts, no images"),
        (".PDF", "4-page press-ready CMYK specification book", "DeviceCMYK · vector · zero fonts"),
        (".SVG", "6 outlined variants", "Exact · Framed · Transparent · Mono · Ctrl+Y · Neon night"),
        (".DXF", "50″ CNC router file", "R2010 · 1270 × 2228.07 mm · mm units"),
        (".PNG", "4000 × 3000 transparent", "300 DPI metadata"),
    ]
    cr = "".join(
        f'<tr><td class="n" style="width:70px;font-size:15px">{e}</td><td><b>{t}</b><small>{s}</small></td>'
        f'<td class="m" style="width:60px;color:#1E823A;font-size:20px;font-weight:700">✓</td></tr>'
        for e, t, s in chk_rows)
    check = f"""
<div class="sec" style="left:952px;width:620px">
 <h2 class="cond"><span>Complete Hand-Off Checklist</span><i>Included in the master pack</i></h2>
 <table><tr><th class="cond">Format</th><th class="cond">Content</th><th class="cond" style="text-align:right">Included</th></tr>{cr}</table>
 <p class="ft">Pantone values are suggested matches; confirm against a physical swatch book. CMYK files carry no printer ICC profile — request a press proof. DXF is a nominal outline: CAM setup (tool, kerf, depth) is a fabricator step.</p>
</div>"""
    body = (f'<div class="hd"><h1 class="disp">Chibees — Layer Anatomy &amp; Hand-Off Package</h1>'
            f'<span class="cond">Freelancer Contest #2801274 · Mexican Restaurant Sign Vectorization</span></div>'
            f'{stack}{tbl}{sets}{check}')
    write("board3.html", "Chibees Board 3", B3_CSS, body)


if __name__ == "__main__":
    board1(); board2(); board3()
