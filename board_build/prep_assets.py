#!/usr/bin/env python3
"""Board assets: transparent cutouts from SVG (bg rect stripped), facade crops, forensic crops, layer SVG fragments."""
import re, subprocess, pathlib, json
from PIL import Image, ImageEnhance, ImageFilter
R = pathlib.Path(__file__).resolve().parent.parent
OUT = R / "board_build" / "gen"; OUT.mkdir(exist_ok=True)

def cut(svg, name, bg_re=r'<rect width="1200" height="900" fill="#[0-9A-Fa-f]{6}"/>'):
    s = (R/"exports"/svg).read_text()
    s2 = re.sub(bg_re, '', s, count=1)
    tmp = OUT/(name+".svg"); tmp.write_text(s2)
    png = OUT/(name+".png")
    subprocess.run(["rsvg-convert","-w","2400",str(tmp),"-o",str(png)],check=True)
    im = Image.open(png).convert("RGBA"); bb = im.split()[3].getbbox()
    im.crop(bb).save(png); tmp.unlink()
    print(name, bb, Image.open(png).size)

cut("Chibees_Sign_Exact_Cabinet_RGB.svg","cut_exact")
cut("Chibees_Sign_Framed_Sticker_Print.svg","cut_framed")
cut("Chibees_Sign_Monochrome_Vector.svg","cut_mono")

# facade crops (day) from employer photo
ref = Image.open(R/"ref/sign_preview_1800.jpg").convert("RGB")
ref.crop((330,300,1430,960)).save(OUT/"facade_day.jpg", quality=95)

# forensic crops: employer crop vs vector render at same region
rc = Image.open(R/"ref/sign_crop_1to1.png").convert("RGB")
vr = Image.open(R/"assets/render_exact_svg.png").convert("RGB")
# ref -> vector mapping measured from cabinet extents
ref_box = (370,175,890,495)   # twin e + brim
sx = 1340/807.0; sy = 795/465.0
def m(b): return (int(130+(b[0]-143)*sx), int(160+(b[1]-100)*sy), int(130+(b[2]-143)*sx), int(160+(b[3]-100)*sy))
rc.crop(ref_box).resize((1040,640),Image.LANCZOS).save(OUT/"fx_ref.png")
vr.crop(m(ref_box)).resize((1040,640),Image.LANCZOS).save(OUT/"fx_vec.png")
loupe = (700,368,800,432)
rc.crop(loupe).resize((1000,640),Image.NEAREST).save(OUT/"loupe_ref.png")
vr.crop(m(loupe)).resize((1000,640),Image.LANCZOS).save(OUT/"loupe_vec.png")
print("vec box", m(ref_box), m(loupe))

t = Image.open(R/"assets/render_transparent_svg.png").convert("RGBA"); t.crop(t.split()[3].getbbox()).save(OUT/"transparent_crop.png")
# layer fragments
s = (R/"exports/Chibees_Sign_Exact_Cabinet_RGB.svg").read_text()
ids = re.findall(r'<g id="([^"]+)"', s)
pos = [s.find(f'<g id="{i}"') for i in ids]
end = s.rfind('</svg>')
frag = {}
for k,i in enumerate(ids):
    e = pos[k+1] if k+1 < len(ids) else end
    frag[i] = s[pos[k]:e]
json.dump(frag, open(OUT/"layers.json","w"))
print(list(frag), [len(v) for v in frag.values()])
