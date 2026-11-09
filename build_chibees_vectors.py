#!/usr/bin/env python3
"""Deterministic Chibees reconstruction. No autotracing; all artwork uses M/L/C/Z.
Requires existing fontTools, Pillow, PyMuPDF, ezdxf and rsvg-convert.
Coordinates refer to the supplied 1080 x 690 crop; technical scale assumes 50 in height.
"""
from pathlib import Path
from dataclasses import dataclass, replace
from collections import Counter
import re, math, json, hashlib, subprocess, zipfile, html
import xml.etree.ElementTree as ET
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from fontTools.pens.qu2cuPen import Qu2CuPen
import fitz, ezdxf

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'exports'
QA=ROOT/'verification'
RED='#E22B24'; GREEN='#198C38'; GOLD='#F6C518'; INK='#231915'; AMBER='#E58E1A'; CREAM='#FAF7F0'; WHITE='#FFFFFF'
LAYERS=['01_Cabinet_Arch','02_Woodgrain_And_Neon_FX','03_Sombrero_Crest','04_Splash_Accents','05_Wordmark_Chibees_Outlined','06_Golden_Swoosh','07_Subtitle_Outlined']
CMYK={RED:(0,.92,.95,0),GREEN:(.84,0,.85,.23),GOLD:(0,.20,.95,0),INK:(.40,.50,.50,.90),AMBER:(0,.43,.89,.10),CREAM:(0,.012,.04,.02),WHITE:(0,0,0,0)}

def n(x):
 s=f'{x:.5f}'.rstrip('0').rstrip('.')
 return s if s and s!='-0' else '0'

def commands(d):
 ts=re.findall(r'[MCLZ]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',d)
 out=[];i=0
 while i<len(ts):
  cmd=ts[i];i+=1;k={'M':2,'L':2,'C':6,'Z':0}[cmd]
  out.append((cmd,tuple(float(x) for x in ts[i:i+k])));i+=k
 return out

def fmt(cs): return ' '.join(c+(' '+' '.join(n(v) for v in p) if p else '') for c,p in cs)
def transform(d,a=1,b=0,c=0,e=1,tx=0,ty=0):
 out=[]
 for op,p in commands(d):
  q=[]
  for x,y in zip(p[::2],p[1::2]):q.extend([a*x+c*y+tx,b*x+e*y+ty])
  out.append((op,q))
 return fmt(out)
def rect(x,y,w,h):return f'M {x} {y} L {x+w} {y} L {x+w} {y+h} L {x} {y+h} Z'
def ellipse(x,y,rx,ry=None):
 ry=ry or rx;k=.5522847498307936
 return fmt([('M',(x+rx,y)),('C',(x+rx,y+k*ry,x+k*rx,y+ry,x,y+ry)),('C',(x-k*rx,y+ry,x-rx,y+k*ry,x-rx,y)),('C',(x-rx,y-k*ry,x-k*rx,y-ry,x,y-ry)),('C',(x+k*rx,y-ry,x+rx,y-k*ry,x+rx,y)),('Z',())])
@dataclass
class Shape:
 d:str
 fill:str|None
 layer:str
 name:str
 stroke:str|None=None
 sw:float=1
 opacity:float=1

def P(d,fill,layer,name,stroke=None,sw=1,opacity=1):return Shape(d,fill,layer,name,stroke,sw,opacity)

def move_shapes(ss,scale=1,x=0,y=0):return [replace(s,d=transform(s.d,a=scale,e=scale,tx=x,ty=y),sw=s.sw*scale) for s in ss]

class OutlinePen(BasePen):
 def __init__(self,gs):super().__init__(gs);self.ops=[]
 def _moveTo(self,p):self.ops.append(('M',p))
 def _lineTo(self,p):self.ops.append(('L',p))
 def _curveToOne(self,a,b,c):self.ops.append(('C',a+b+c))
 def _closePath(self):self.ops.append(('Z',()))
 def _endPath(self):pass
FONT=Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
_font=None

def label(text,x,y,size=12,color=INK,tracking=0,center=False,layer='08_Specifications',name='label'):
 global _font
 if _font is None:_font=TTFont(FONT)
 gs=_font.getGlyphSet();cmap=_font.getBestCmap();upm=_font['head'].unitsPerEm
 raw=[];cursor=0
 for ch in text:
  gn=cmap.get(ord(ch),'space');pen=OutlinePen(gs)
  gs[gn].draw(Qu2CuPen(pen,max_err=.35,all_cubic=True))
  raw.extend(commands(transform(fmt(pen.ops),a=size/upm,e=-size/upm,tx=cursor)))
  cursor+=gs[gn].width*size/upm+tracking
 d=transform(fmt(raw),tx=x-(cursor-tracking)/2 if center else x,ty=y)
 return P(d,color,layer,name)

CABINET='M 190 254 L 264 254 C 280 254 285 250 293 237 C 341 155 440 104 547 104 C 654 104 753 155 801 237 C 809 250 814 254 830 254 L 904 254 C 931 254 947 272 947 301 L 947 512 C 947 544 934 560 902 560 L 192 560 C 160 560 147 544 147 512 L 147 301 C 147 272 163 254 190 254 Z'
# Both e glyphs share exactly the same source control points. No photographed cursor input.
E_GLYPH='M 69 55 C 53 61 36 63 24 62 C 21 80 25 91 37 92 C 48 93 57 83 62 76 L 72 82 C 64 101 50 111 32 109 C 5 107 -2 89 1 66 C 4 39 18 10 43 7 C 65 4 77 16 77 31 C 77 41 74 49 69 55 Z M 26 49 C 39 49 52 43 54 29 C 55 22 51 18 46 19 C 37 20 30 34 26 49 Z'

def master():
 ss=[P(CABINET,CREAM,LAYERS[0],'cabinet', '#DDD3BF',3)]
 # Subdued closed wood-grain ribbons, clipped by the bounds by construction.
 for j in range(17):
  y=278+j*15.3
  d=f'M 168 {y} C 300 {y-1.6} 416 {y+1.3} 544 {y} C 678 {y-1.5} 800 {y+1.4} 926 {y} L 926 {y+.45} C 790 {y+1.7} 672 {y-.9} 544 {y+.5} C 416 {y+1.8} 300 {y-1.1} 168 {y+.5} Z'
  ss.append(P(d,'#EBE3D3',LAYERS[1],f'woodgrain_{j+1:02}'))
 # Hat: no font or bitmap components. All contours are cubic or straight segments.
 hat=[]
 def h(d,f,name,stroke=INK,w=3):hat.append(P(d,f,LAYERS[2],name,stroke,w))
 h('M 393 224 C 383 237 387 256 407 265 C 426 274 460 278 482 275 C 491 274 490 265 482 264 C 463 263 444 258 430 249 C 416 238 406 230 393 224 Z',GOLD,'left_under_curl',INK,5)
 h('M 579 257 C 579 277 604 290 633 285 C 658 282 681 268 695 249 C 674 250 649 254 631 255 C 612 256 597 256 579 257 Z',GOLD,'right_under_curl',INK,5)
 h('M 491 205 C 502 188 508 144 536 136 C 551 131 570 139 580 150 C 594 167 598 192 608 210 C 571 220 530 219 491 205 Z',GOLD,'crown',INK,5)
 h('M 499 195 C 509 172 515 157 526 147 C 516 172 519 192 526 205 L 499 207 Z',AMBER,'crown_amber',None)
 for j in range(4):
  y=155+j*9
  h(f'M {523-j*3} {y} C 539 {y-4} 560 {y-3} {576+j*3} {y+2} C 557 {y+.1} 539 {y-.4} {523-j*3} {y+1.8} Z',AMBER,f'crown_woodcut_{j}',None)
 h('M 499 191 C 533 198 568 197 599 195 L 609 219 C 567 225 527 220 491 211 Z',RED,'crown_red_band',INK,2.7)
 h('M 497 201 L 512 195 L 526 207 L 543 199 L 558 212 L 577 202 L 590 215 L 603 206 L 609 220 C 570 226 530 222 491 212 Z',GREEN,'crown_green_band',None)
 h('M 495 202 L 512 194 L 527 206 L 543 198 L 558 210 L 576 201 L 591 212 L 602 205 L 605 209 L 590 218 L 575 207 L 557 216 L 542 204 L 526 212 L 512 200 L 493 209 Z',GOLD,'crown_zigzag',None)
 h('M 387 208 C 412 193 452 193 489 203 C 543 216 626 226 712 222 C 718 239 702 261 674 268 C 634 277 577 260 530 253 C 480 245 423 246 398 256 C 387 244 383 222 387 208 Z',GOLD,'brim_outer_lip',INK,5)
 h('M 393 211 C 427 204 455 205 492 213 C 551 228 633 235 707 227 C 706 241 696 250 677 255 C 629 262 581 247 531 241 C 479 233 430 230 399 241 Z',RED,'brim_red_field',INK,2.5)
 # Continuous chevron ribbon follows the tilted, curved brim; alternating lower green fields.
 xs=[395,426,457,488,519,550,581,612,643,674,705]
 top=[213,208,211,216,223,229,233,236,236,234,230]
 bot=[240,235,236,241,246,251,256,260,261,258,246]
 mid=[]
 for i,x in enumerate(xs):mid.append((x,top[i]+4 if i%2==0 else bot[i]-3))
 green='M '+ ' L '.join(f'{x} {y}' for x,y in mid)+' L '+' L '.join(f'{x} {y}' for x,y in reversed(list(zip(xs,bot))))+' Z'
 h(green,GREEN,'brim_green_triangles',None)
 ribbon='M '+' L '.join(f'{x} {y-2.7}' for x,y in mid)+' L '+' L '.join(f'{x} {y+2.7}' for x,y in reversed(mid))+' Z'
 h(ribbon,GOLD,'continuous_chevron_ribbon',None)
 for i in range(10):
  x=(xs[i]+xs[i+1])/2;y=(top[i]+top[i+1])/2+5 if i%2==0 else (bot[i]+bot[i+1])/2-3
  h(ellipse(x,y,2.1),GOLD,f'festive_dot_{i+1:02}',None)
 # Hand-drawn under-curl ribs, tapered closed shapes to remain portable vectors.
 for j in range(11):
  x=407+j*6;y=253+math.sin(j/10*math.pi)*10
  h(f'M {x} {y-4} C {x+3} {y} {x+5} {y+5} {x+8} {y+7} L {x+5} {y+7} C {x+2} {y+4} {x} {y} {x} {y-4} Z',INK,f'left_rib_{j}',None)
 for j in range(12):
  x=588+j*6;y=268+math.sin(j/11*math.pi)*8
  h(f'M {x} {y-6} C {x+2} {y-2} {x+1} {y+3} {x-2} {y+6} L {x+1} {y+6} C {x+5} {y+2} {x+5} {y-2} {x+3} {y-6} Z',INK,f'right_rib_{j}',None)
 # Reference slopes down to the right in screen coordinates. -3.5 in Cartesian coordinates.
 ang=math.radians(1.5);a=math.cos(ang);b=math.sin(ang)
 ss.extend(replace(s,d=transform(s.d,a=a,b=b,c=-b,e=a,tx=550-a*550+b*216,ty=216-b*550-a*216)) for s in hat)
 droplets=[('M 234 330 C 226 316 205 303 209 285 C 211 277 221 279 226 285 C 235 297 238 318 234 330 Z',RED,'top_red'),('M 225 342 C 210 332 181 332 176 319 C 173 310 182 307 190 310 C 205 315 219 330 225 342 Z',GREEN,'middle_green'),('M 224 356 C 207 350 187 345 177 352 C 168 360 176 369 186 368 C 201 366 213 362 224 356 Z',GOLD,'bottom_yellow')]
 for d,col,name in droplets:
  ss.append(P(d,col,LAYERS[3],'left_'+name))
  ss.append(P(transform(d,a=-1,tx=1094),col,LAYERS[3],'right_'+name))
 letters=[('C','M 374 337 C 376 351 370 366 356 370 C 344 373 335 367 337 356 C 339 345 347 342 346 334 C 345 323 329 326 319 332 C 287 352 270 390 271 427 C 271 454 279 470 300 472 C 323 474 343 455 344 433 C 344 427 341 424 333 426 L 334 414 L 371 410 C 375 424 374 443 367 460 C 352 487 327 498 295 495 C 253 492 233 473 235 434 C 237 389 258 345 291 324 C 323 303 368 304 374 337 Z'),
 ('h','M 387 336 L 418 325 L 415 381 C 427 369 440 364 452 370 C 466 377 465 394 465 410 L 464 443 C 464 451 467 455 473 455 L 471 468 L 442 469 C 437 463 437 453 437 443 L 438 409 C 439 394 436 389 430 391 C 423 393 417 402 415 414 L 413 470 L 383 474 L 387 336 Z'),
 ('i','M 484 374 L 514 368 L 512 430 C 512 440 512 443 520 442 L 519 455 C 508 461 491 459 486 452 C 482 447 483 435 483 427 Z'),
 ('i_dot',ellipse(499,339,16,15)),
 ('b','M 532 317 L 561 307 L 558 362 C 568 351 581 347 594 352 C 615 358 619 382 614 408 C 608 439 594 452 571 450 C 558 449 548 444 532 450 L 532 317 Z M 558 387 L 556 426 C 568 437 580 426 584 410 C 589 391 587 371 576 372 C 566 372 561 379 558 387 Z'),
 ('e_first',transform(E_GLYPH,tx=623,ty=336)),
 ('e_second',transform(E_GLYPH,tx=708,ty=347)),
 ('s','M 850 403 C 840 404 833 398 835 390 C 836 385 840 382 836 379 C 829 374 819 381 821 390 C 823 402 841 410 853 423 C 869 440 873 454 865 472 C 856 491 833 496 813 488 C 795 481 789 465 796 452 C 801 442 815 439 823 447 C 832 456 827 467 817 467 C 822 480 839 476 840 465 C 841 453 828 445 816 433 C 798 417 789 401 797 382 C 806 361 833 356 851 367 C 865 376 864 397 850 403 Z')]
 for name,d in letters:ss.append(P(d,RED,LAYERS[4],name,WHITE,6))
 ss.append(P('M 376 492 C 471 456 665 456 788 493 C 667 478 494 478 376 492 Z',GOLD,LAYERS[5],'golden_crescent'))
 subtitle=label('MEXICAN RESTAURANT',0,0,35,INK,tracking=6,layer=LAYERS[6],name='subtitle')
 # Fit to the photo width using geometry, retaining wide tracking.
 cs=commands(subtitle.d);xs=[p[i] for c,p in cs for i in range(0,len(p),2)];lo,hi=min(xs),max(xs)
 subtitle=replace(subtitle,d=transform(subtitle.d,a=604/(hi-lo),tx=247-lo*604/(hi-lo),ty=533))
 ss.append(subtitle)
 return ss

def keylined(ss,width=8):
 return [replace(s,fill=s.fill,stroke=WHITE,sw=width,name=s.name+'_halo') for s in ss if s.layer in LAYERS[2:] and s.name not in ['subtitle'] and not ('rib' in s.name or 'dot' in s.name or 'woodcut' in s.name)]+ss

def edition(base,kind):
 if kind=='exact':
  halo=[P(CABINET,None,LAYERS[1],f'daylight_warm_halo_{j}','#F2D99E',j*1.7,.015) for j in range(18,0,-1)]
  return halo+base
 if kind=='sticker':return [replace(s,stroke=INK,sw=8) if s.name=='cabinet' else s for s in base]
 if kind=='isolate':
  core=[s for s in base if s.layer in LAYERS[2:]]
  # Underpaint the outer hat contours only; local detail should not get individual halos.
  halos=[replace(s,fill=WHITE,stroke=WHITE,sw=8,name=s.name+'_halo') for s in core if s.name in ['crown','brim_outer_lip','left_under_curl','right_under_curl','golden_crescent','subtitle'] or s.layer==LAYERS[3]]
  return halos+core
 if kind=='mono':
  # One-ink positive/negative crest: filled compound contours, no white patches,
  # no hidden through-lines, and no live strokes for vinyl cutters.
  mhat=[
   ('mono_crown','M 491 203 C 502 188 508 144 536 136 C 551 131 570 139 580 150 C 594 167 598 192 608 210 L 602 209 C 592 190 590 168 576 154 C 566 144 551 138 538 142 C 514 150 510 187 498 204 Z'),
   ('mono_left_curl','M 393 248 C 404 267 450 281 482 276 C 494 274 494 264 483 262 C 457 261 433 253 418 247 L 408 249 C 432 260 459 266 481 267 C 486 268 486 271 480 271 C 450 275 416 263 402 249 Z'),
   ('mono_right_curl','M 577 257 C 580 283 608 293 636 285 C 660 279 680 268 695 249 L 688 251 C 674 266 657 275 634 280 C 612 285 590 278 584 258 Z'),
  ]
  ang=math.radians(1.5);a=math.cos(ang);b=math.sin(ang)
  ss=[P(transform(d,a=a,b=b,c=-b,e=a,tx=550-a*550+b*216,ty=216-b*550-a*216),INK,LAYERS[2],name) for name,d in mhat]
  outer=next(s for s in base if s.name=='brim_outer_lip')
  inner=next(s for s in base if s.name=='brim_red_field')
  ss.append(P(outer.d+' '+inner.d,INK,LAYERS[2],'mono_brim_compound'))
  for s in base:
   if s.layer==LAYERS[2] and (s.name in ['continuous_chevron_ribbon','crown_zigzag'] or 'dot' in s.name or 'woodcut' in s.name):
    ss.append(replace(s,fill=INK,stroke=None))
   elif s.layer in LAYERS[3:]:ss.append(replace(s,fill=INK,stroke=None))
  return ss
 raise ValueError(kind)

def anchors(d):
 out=[];cur=start=None;handles=[]
 for cmd,p in commands(d):
  if cmd=='M':cur=start=p;out.append(p)
  elif cmd=='L':cur=p;out.append(p)
  elif cmd=='C':
   handles.extend([(cur,p[:2]),(p[4:],p[2:4])]);cur=p[4:];out.append(cur)
  elif cmd=='Z':cur=start
 return out,handles

def wireframe(base,annotate=True):
 bottom=750 if annotate else 630
 ss=[P(rect(0,-60,1080,bottom+60),'#0A1118','00_Blueprint','background')]
 for x in range(20,1080,40):ss.append(P(f'M {x} -60 L {x} {bottom}',None,'00_Blueprint',f'grid_x{x}','#152B3A',.5))
 for y in range(-40,bottom,40):ss.append(P(f'M 0 {y} L 1080 {y}',None,'00_Blueprint',f'grid_y{y}','#152B3A',.5))
 geometry=base
 for s in geometry:
  ss.append(replace(s,fill=None,stroke='#F59E0B' if s.layer==LAYERS[2] else '#38BDF8',sw=.85,opacity=.18 if s.layer==LAYERS[1] else 1))
  an,hs=anchors(s.d)
  for j,(p,q) in enumerate(hs):
   if math.dist(p,q)>.2:ss.append(P(f'M {n(p[0])} {n(p[1])} L {n(q[0])} {n(q[1])}',None,'09_Tangent_Handles',f'{s.name}_t{j}','#F43F5E',.45,.15 if s.layer==LAYERS[1] else 1))
  for j,(x,y) in enumerate(an):ss.append(P(rect(x-1.25,y-1.25,2.5,2.5),WHITE,'10_Anchor_Nodes',f'{s.name}_a{j}','#0284C7',.4,.25 if s.layer==LAYERS[1] else 1))
 if annotate:
  count=sum(len(anchors(s.d)[0]) for s in geometry)
  ss.extend([label('CHIBEES / VECTOR CONSTRUCTION',68,14,21,WHITE),label(f'{count} ANCHOR COMMANDS / CUBIC BEZIER / ZERO LIVE TYPE',68,42,11,'#38BDF8'),label('01 CABINET / 02 GRAIN',56,603,11,'#38BDF8'),label('03 SOMBRERO',300,603,11,'#F59E0B'),label('04 SPLASHES',500,603,11,'#38BDF8'),label('05 CUSTOM LETTERING',700,603,11,'#38BDF8'),label('06 SWOOSH / 07 SUBTITLE',68,640,11,'#38BDF8'),label('WHITE: ANCHORS    ROSE: TANGENT HANDLES    CYAN / GOLD: PATHS',68,691,11,WHITE)])
 return ss

def svg(ss,path,night=False):
 parts=['<?xml version="1.0" encoding="UTF-8"?>','<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" viewBox="0 -60 1080 810" width="1080" height="810">','<title>Chibees Mexican Restaurant - outlined vector reconstruction</title>','<metadata>Source: sign_crop_1to1.png. Reconstructed from a photographed screen. Proposed colors; 50-inch height assumed from supplied brief.</metadata>']
 if night:
  parts.append('<defs><filter id="warmGlow" x="-30%" y="-40%" width="160%" height="180%"><feGaussianBlur stdDeviation="18"/></filter></defs>')
  parts.append(f'<path d="{CABINET}" fill="#FFD780" opacity="0.8" filter="url(#warmGlow)"/>')
 # Group by consecutive layer so stacking is preserved. Unique groups retain layer identity.
 counts=Counter();path_counts=Counter();prev=None
 for s in ss:
  if s.layer!=prev:
   if prev is not None:parts.append('</g>')
   counts[s.layer]+=1;gid=s.layer if counts[s.layer]==1 else f'{s.layer}_{counts[s.layer]}'
   parts.append(f'<g id="{gid}" data-layer="{s.layer}">');prev=s.layer
  path_counts[s.name]+=1
  pid=s.name if path_counts[s.name]==1 else f'{s.name}_{path_counts[s.name]}'
  parts.append(f'<path id="{html.escape(pid)}" d="{s.d}" fill="{s.fill or "none"}" fill-rule="evenodd"'+(f' stroke="{s.stroke}" stroke-width="{n(s.sw)}" stroke-linejoin="round" stroke-linecap="round"' if s.stroke else '')+(f' opacity="{n(s.opacity)}"' if s.opacity!=1 else '')+'/>')
 if prev:parts.append('</g>')
 parts.append('</svg>');path.write_text('\n'.join(parts))

def night_scene(base):
 ss=[P(rect(0,-60,1080,810),'#21191A','00_Night','night_backdrop')]
 for row,y in enumerate(range(-40,760,42)):
  for col,x in enumerate(range(-100,1100,160)):
   x+=80*(row%2)
   ss.append(P(rect(x,y,155,37),'#302123' if (row+col)%3 else '#352427','00_Night',f'brick_{row}_{col}'))
 # Concentric vector glow rings: fully portable to SVG/PDF; no embedded raster.
 for j in range(22,0,-1):
  ss.append(P(CABINET,None,LAYERS[1],f'warm_halo_{j}','#725136',j*2.4,.025+(22-j)*.001))
 ss.extend(base)
 ss.extend([label('PERSPECTIVE BY NIGHT',540,16,23,CREAM,2,True),label('50-INCH BACKLIT CABINET / FRONTAL NIGHT STUDY',540,47,10,'#DBBD83',1.2,True)])
 ss.extend([P('M 963 104 L 995 104 M 963 560 L 995 560 M 983 104 L 983 560 M 976 114 L 983 104 L 990 114 M 976 550 L 983 560 L 990 550',None,'08_Specifications','height_dimension',GOLD,1.3),label('50"',1008,337,18,GOLD),label('1270 mm',540,636,17,CREAM,1,True),label('WARM LED HALO / CREAM ACRYLIC FACE / DIMENSIONS SUBJECT TO SITE CHECK',540,677,10,'#DBBD83',.3,True)])
 return ss

# Minimal PDF writer: true DeviceCMYK paths, optional-content layers, no fonts/images.
def cmyk(color):
 if color in CMYK:return CMYK[color]
 rgb=[int(color[i:i+2],16)/255 for i in (1,3,5)];k=1-max(rgb)
 return (0,0,0,1) if k==1 else tuple((1-v-k)/(1-k) for v in rgb)+(k,)

def pdf_ops(ss,layer_refs=None):
 out=['1 J 1 j'];prev=None
 for s in ss:
  if layer_refs and s.layer!=prev:
   if prev is not None:out.append('EMC')
   out.append(f'/OC /L{layer_refs[s.layer]} BDC');prev=s.layer
  out.append('q')
  if s.opacity!=1:out.append(f'/A{int(round(s.opacity*1000))} gs')
  if s.fill:out.append(' '.join(n(v) for v in cmyk(s.fill))+' k')
  if s.stroke:out.extend([' '.join(n(v) for v in cmyk(s.stroke))+' K',f'{n(s.sw)} w'])
  for cmd,p in commands(s.d):out.append(' '.join(n(v) for v in p)+(' '+{'M':'m','L':'l','C':'c','Z':'h'}[cmd]))
  out.append('B*' if s.fill and s.stroke else 'f*' if s.fill else 'S' if s.stroke else 'n');out.append('Q')
 if layer_refs and prev is not None:out.append('EMC')
 return '\n'.join(out)

def pdf_write(pages,path,size=(1080,810),layered=False):
 objs=[None,None]
 def add(b):objs.append(b.encode() if isinstance(b,str) else b);return len(objs)
 def stream(data,extra=''):
  data=data.encode() if isinstance(data,str) else data
  return add(f'<< /Length {len(data)} {extra} >>\nstream\n'.encode()+data+b'\nendstream')
 layers=list(dict.fromkeys(s.layer for page in pages for s in page));lr={};ocgs=[]
 if layered:
  for i,l in enumerate(layers):
   ref=add(f'<< /Type /OCG /Name ({l}) /Intent [/View /Design] >>');lr[l]=i;ocgs.append(ref)
 alphas=sorted(set(int(round(s.opacity*1000)) for pg in pages for s in pg if s.opacity!=1));ar={a:add(f'<< /Type /ExtGState /ca {a/1000} /CA {a/1000} >>') for a in alphas}
 metadata='''<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?><x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:pdf="http://ns.adobe.com/pdf/1.3/" xmlns:xmp="http://ns.adobe.com/xap/1.0/" xmlns:xmpTPg="http://ns.adobe.com/xap/1.0/t/pg/" xmp:CreatorTool="Chibees deterministic cubic vector generator" pdf:Producer="Chibees PDF-compatible vector master" xmpTPg:ColorMode="CMYK"><dc:description><rdf:Alt><rdf:li xml:lang="x-default">CMYK path master; RGB red #E22B24; process red 0/92/95/0; suggested Pantone 485 C or 1795 C, physical proof required. PDF-compatible AI; no proprietary Illustrator editing data. 50 inch cabinet height is an assumption from brief.</rdf:li></rdf:Alt></dc:description></rdf:Description></rdf:RDF></x:xmpmeta><?xpacket end="w"?>'''
 meta=stream(metadata.encode('utf8'),'/Type /Metadata /Subtype /XML')
 page_ids=[]
 for ss in pages:
  w,h=size;content=f'q\n1 0 0 -1 0 {h} cm\n'+pdf_ops(ss,lr if layered else None)+'\nQ'
  cs=stream(content)
  resources='<< /ProcSet [/PDF]'
  if ar:resources+=' /ExtGState << '+' '.join(f'/A{a} {r} 0 R' for a,r in ar.items())+' >>'
  if layered:resources+=' /Properties << '+' '.join(f'/L{i} {r} 0 R' for i,r in enumerate(ocgs))+' >>'
  resources+=' >>'
  page_ids.append(add(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {w} {h}] /TrimBox [0 0 {w} {h}] /Resources {resources} /Contents {cs} 0 R >>'))
 oc=''
 if layered:
  refs=' '.join(f'{r} 0 R' for r in ocgs);oc=f' /OCProperties << /OCGs [{refs}] /D << /Name (Chibees Layers) /Order [{refs}] /ON [{refs}] >> >>'
 objs[0]=f'<< /Type /Catalog /Pages 2 0 R /Metadata {meta} 0 R{oc} >>'.encode();objs[1]=f'<< /Type /Pages /Count {len(page_ids)} /Kids ['.encode()+ ' '.join(f'{r} 0 R' for r in page_ids).encode()+b'] >>'
 info=add('<< /Title (Chibees - Outlined CMYK Vector Master) /Creator (Deterministic Cubic Bezier Generator) /Producer (PDF 1.7 vector export) /CreationDate (D:20261109000000Z) >>')
 data=bytearray(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3\n% PDF-compatible Adobe Illustrator interchange; CMYK vectors and OCG layers\n')
 offsets=[0]
 for i,o in enumerate(objs,1):offsets.append(len(data));data.extend(f'{i} 0 obj\n'.encode()+o+b'\nendobj\n')
 start=len(data);data.extend(f'xref\n0 {len(objs)+1}\n0000000000 65535 f \n'.encode())
 for off in offsets[1:]:data.extend(f'{off:010} 00000 n \n'.encode())
 data.extend(f'trailer\n<< /Size {len(objs)+1} /Root 1 0 R /Info {info} 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode());path.write_bytes(data)

def eps_write(ss,path):
 # Tight art bounds: 800 x 456 design units, exported at 1 pt per unit.
 out=['%!PS-Adobe-3.0 EPSF-3.0','%%BoundingBox: 0 0 812 468','%%HiResBoundingBox: 0 0 812 468','%%LanguageLevel: 3','%%DocumentProcessColors: Cyan Magenta Yellow Black','%%Creator: Chibees Cubic Vector Generator','%%Title: Chibees CMYK Production Master','%%Pages: 1','%%EndComments','%%BeginProlog','/m {moveto} bind def /l {lineto} bind def /c {curveto} bind def /h {closepath} bind def','%%EndProlog','gsave','-141 566 translate 1 -1 scale','1 setlinejoin 1 setlinecap']
 for s in ss:
  out.extend(['gsave',f'%%Layer: {s.layer}','newpath'])
  for c,p in commands(s.d):out.append(' '.join(n(v) for v in p)+' '+{'M':'m','L':'l','C':'c','Z':'h'}[c])
  if s.fill:out.extend(['gsave',' '.join(n(v) for v in cmyk(s.fill))+' setcmykcolor','eofill','grestore'])
  if s.stroke:out.extend([' '.join(n(v) for v in cmyk(s.stroke))+' setcmykcolor',f'{n(s.sw)} setlinewidth','stroke'])
  out.append('grestore')
 out.extend(['grestore','showpage','%%EOF']);path.write_text('\n'.join(out))

# Adaptive cubic subdivision; distance bound from control polygon to chord.
def flat_cubic(p0,p1,p2,p3,tol):
 def distance(p,a,b):
  dx=b[0]-a[0];dy=b[1]-a[1]
  if dx*dx+dy*dy<1e-20:return math.dist(p,a)
  t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
  return math.dist(p,(a[0]+t*dx,a[1]+t*dy))
 if max(distance(p1,p0,p3),distance(p2,p0,p3))<=tol:return [p3]
 def mid(a,b):return ((a[0]+b[0])/2,(a[1]+b[1])/2)
 a,b,c=mid(p0,p1),mid(p1,p2),mid(p2,p3);d,e=mid(a,b),mid(b,c);f=mid(d,e)
 return flat_cubic(p0,a,d,f,tol)+flat_cubic(f,e,c,p3,tol)

def contours(d,tol=.01):
 out=[];pts=[];cur=None
 for c,p in commands(d):
  if c=='M':
   if pts:out.append((pts,False))
   pts=[p];cur=p
  elif c=='L':pts.append(p);cur=p
  elif c=='C':pts.extend(flat_cubic(cur,p[:2],p[2:4],p[4:],tol));cur=p[4:]
  elif c=='Z':
   if len(pts)>1 and math.dist(pts[-1],pts[0])<1e-6:pts.pop()
   out.append((pts,True));pts=[]
 if pts:out.append((pts,False))
 return out

def dxf_write(base,path):
 previous=ezdxf.options.write_fixed_meta_data_for_testing
 ezdxf.options.write_fixed_meta_data_for_testing=True
 doc=ezdxf.new('R2010');doc.units=4;doc.header['$INSUNITS']=4;doc.header['$MEASUREMENT']=1
 # Freeze volatile metadata/handles to keep repeat builds deterministic.
 doc.header['$TDCREATE']=doc.header['$TDUPDATE']=2461353.5
 doc.header['$FINGERPRINTGUID']='{00000000-0000-0000-0000-000028012740}'
 doc.header['$VERSIONGUID']='{00000000-0000-0000-0000-000028012741}'
 layers={'CUT_CABINET':1,'VINYL_RED':1,'VINYL_GREEN':3,'VINYL_GOLD':2,'VINYL_ESPRESSO':7,'DETAIL_ENGRAVE':8}
 for name,col in layers.items():doc.layers.new(name,dxfattribs={'color':col})
 msp=doc.modelspace();scale=1270/456;counts=Counter()
 for s in base:
  if s.name=='cabinet':layer='CUT_CABINET'
  elif s.layer==LAYERS[1]:layer='DETAIL_ENGRAVE'
  else:layer={RED:'VINYL_RED',GREEN:'VINYL_GREEN',GOLD:'VINYL_GOLD',INK:'VINYL_ESPRESSO'}.get(s.fill,'DETAIL_ENGRAVE')
  for points,closed in contours(s.d,tol=.02/scale):
   if not closed:raise ValueError('Production contour is open: '+s.name)
   if len(points)<3:continue
   pts=[((x-147)*scale,(560-y)*scale) for x,y in points]
   msp.add_lwpolyline(pts,close=True,dxfattribs={'layer':layer});counts[layer]+=1
 doc.set_modelspace_vport(height=1500,center=(1100,635))
 # Required class discovery iterates a Python set. Freeze its insertion order
 # before export so different PYTHONHASHSEED values cannot change the file.
 doc.classes.add_required_classes(doc.dxfversion)
 doc.classes.classes=dict(sorted(doc.classes.classes.items()))
 # ezdxf writes a timestamp in $TDUPDATE on save; fixed_metadata makes output stable.
 try:doc.saveas(path)
 finally:ezdxf.options.write_fixed_meta_data_for_testing=previous
 return dict(counts)

def spec_pages(base,stats):
 def header(num,title,sub):
  return [P(rect(0,0,1080,810),WHITE,'00_Paper','paper'),P(rect(48,43,42,4),RED,'08_Specifications','accent'),label('CHIBEES / VECTOR PRODUCTION',48,73,12,INK,1),label(title,48,112,28),label(sub,48,139,10,'#766A60'),label(f'{num:02} / 04',1032,770,11,INK,center=True),label('CHIBEES - MEXICAN RESTAURANT / CONTEST 2801274',48,770,9,'#766A60')]
 pages=[]
 p=header(1,'CABINET MASTER + COLOR SPECIFICATION','Cubic reconstruction from the employer photograph / color separations are proposed production targets')
 p+=move_shapes(base,.78,114,84)
 p+=[label('COLOR',56,569,10),label('RGB / HEX',245,569,10),label('CMYK %',438,569,10),label('SPOT COLOR GUIDANCE',668,569,10)]
 rows=[('Fiesta chili red',RED,'0 / 92 / 95 / 0','485 C or 1795 C - visual target'),('Jalapeno green',GREEN,'84 / 0 / 85 / 23','Match by approved physical swatch'),('Marigold yellow',GOLD,'0 / 20 / 95 / 0','Match by approved physical swatch'),('Espresso',INK,'40 / 50 / 50 / 90','Rich black; small type: 100 K option'),('Warm acrylic',CREAM,'0 / 1.2 / 4 / 2','Substrate / unprinted white option')]
 for i,(title,col,cm,spot) in enumerate(rows):
  y=595+i*25;p.extend([P(rect(54,y-10,15,15),col,'08_Specifications',f'swatch{i}'),label(title,80,y+1,10),label(col,245,y+1,10),label(cm,438,y+1,10),label(spot,668,y+1,10)])
 p+=[label('Process CMYK artwork. Pantone names are suggestions, not measured matches or embedded spot separations.',54,730,10)]
 pages.append(p)
 p=header(2,'PRINT / STICKER + TRANSPARENT LOCKUP','Two applications share the exact same custom glyphs, hat contours and R / G / Y accent order')
 p+=[P(rect(48,174,476,399),'#F3EEE5','00_Paper','sticker_panel'),P(rect(552,174,480,399),'#C9AA7C','00_Paper','kraft_panel')]
 p+=move_shapes(edition(base,'sticker'),.53,-5,210)
 p+=move_shapes(edition(base,'isolate'),.53,499,210)
 p+=[label('01 / FRAMED PRINT + STICKER',70,210,13),label('02 / WHITE-KEYLINE ISOLATE',574,210,13),label('Dark cabinet border / restrained vector grain',70,550,10),label('Transparent SVG / white is intentional artwork',574,550,10)]
 for y,t in [(620,'All logo letters are paths; there are no live fonts or linked images.'),(647,'White keyline requires white ink when printing on a non-white substrate.'),(674,'Sticker cutter: use the cabinet outline. Add vendor-specified bleed before nesting.'),(701,'Mono edition is one espresso ink with open hat linework and solid custom lettering.')]:p.append(label(t,60,y,12))
 pages.append(p)
 p=header(3,'PATH AUDIT / CURSOR REMOVAL','The two e glyphs use identical cubic control points with translation only; no photographed cursor is traced')
 p+=move_shapes(wireframe(base,False),.59,30,212)
 # Two enlarged exact copies of the source e glyph, at right.
 for i,x in enumerate((710,855)):
  p.append(P(transform(E_GLYPH,a=1.45,e=1.45,tx=x,ty=250),RED,LAYERS[4],f'audit_e_{i}'))
 p+=[label('e',0,0,1)] if False else []
 p.extend([label('MATCHING CUBIC GEOMETRY',708,216,13),label('e1: x = 623, y = 336',710,450,10),label('e2: x = 708, y = 347',710,471,10),label('Translation: +85, +11',710,492,10),label('No crosshair paths',710,523,11),label(f'{stats["art_anchor_commands"]} anchor commands / {stats["art_cubic_segments"]} cubic segments',60,637,13),label(f'{stats["art_paths"]} master paths / 7 artwork layers / 0 live text / 0 raster images',60,664,12),label('Screen moire, pixel grid and cursor are omitted. Obscured micro-details are reconstructed.',60,697,11),label('Outline view exposes actual geometry; node count includes each M, L and C endpoint.',60,721,10)])
 pages.append(p)
 p=header(4,'50-INCH CABINET / SCALING GUIDE','Dimensional model assumes 50 inches is the overall cabinet height; verify on site before fabrication')
 p+=move_shapes(base,.58,46,123)
 p+=[P('M 616 183 L 647 183 M 616 448 L 647 448 M 636 183 L 636 448',None,'08_Specifications','dim',INK,1),label('1270 mm / 50"',667,308,15),label('Cabinet width: 2228.07 mm / 87.719"',667,342,11),label('DXF units: millimeters / AC1024',667,369,11),label('Closed LWPOLYLINE contours',667,396,11),label('Curve chord tolerance: 0.02 mm',667,423,11)]
 rows=[('EXTERIOR CABINET','1270 mm high','1:1 DXF / site measurement required'),('TAKEAWAY BAG','150 mm high','263.16 mm wide / proof keyline'),('MENU LOCKUP','75 mm high','131.58 mm wide / omit tiny grain if needed'),('STICKER','50 mm high','87.72 mm wide / vendor bleed + cut setup')]
 for i,(a,b,c) in enumerate(rows):
  y=511+i*42;p.extend([P(f'M 55 {y-14} L 1023 {y-14}',None,'08_Specifications',f'rule{i}','#D8CEC0',.6),label(a,60,y+5,11),label(b,335,y+5,11),label(c,530,y+5,11)])
 p.extend([label('DXF: CUT_CABINET is the exterior cut. VINYL_* are artwork contours; DETAIL_ENGRAVE is decorative.',60,704,10),label('Tool diameter, kerf, offsets, depth, workholding and electrical construction are fabricator setup items.',60,726,10)])
 pages.append(p)
 return pages

def render_svg(src,dst,w,h):
 subprocess.run(['rsvg-convert','-w',str(w),'-h',str(h),str(src),'-o',str(dst)],check=True)
 im=Image.open(dst).convert('RGBA');im.save(dst,dpi=(300,300))

def validate(base):
 report={}
 for f in sorted(OUT.glob('*.svg')):
  tree=ET.parse(f);tags=[e.tag.split('}')[-1] for e in tree.iter()]
  assert 'text' not in tags and 'image' not in tags,(f,'non-vector content')
  ids=[e.attrib['id'] for e in tree.iter() if 'id' in e.attrib];assert len(ids)==len(set(ids)),f
  for el in tree.iter():
   if el.tag.endswith('path'):
    d=el.attrib['d'];assert not re.search('[a-zABDHQSTV]',d),f;commands(d)
  report[f.name]={'paths':tags.count('path'),'text_elements':0,'raster_images':0}
 d1=next(s.d for s in base if s.name=='e_first');d2=next(s.d for s in base if s.name=='e_second')
 assert transform(d1,tx=85,ty=11)==d2
 for side in ['left','right']:
  assert [next(s.fill for s in base if s.name==f'{side}_{name}') for name in ['top_red','middle_green','bottom_yellow']]==[RED,GREEN,GOLD]
 for f in [OUT/'Chibees_Sign_Master_Layered.ai',OUT/'Chibees_Sign_Press_Ready_CMYK.pdf']:
  doc=fitz.open(f);assert len(doc)==(1 if f.suffix=='.ai' else 4)
  assert all(not p.get_images() and not p.get_fonts() for p in doc)
  for page in doc:
   stream=page.read_contents();assert b' rg' not in stream and b' RG' not in stream
  report[f.name]={'pages':len(doc),'fonts':0,'images':0,'vector_paths':sum(len(p.get_drawings()) for p in doc),'ocg_layers':len(doc.get_ocgs())}
 doc=ezdxf.readfile(OUT/'Chibees_Sign_50inch_CNC_Router.dxf');audit=doc.audit();assert not audit.has_errors
 entities=list(doc.modelspace());assert all(e.dxftype()=='LWPOLYLINE' and e.closed for e in entities)
 cabinet=list(doc.modelspace().query('LWPOLYLINE[layer=="CUT_CABINET"]'));assert len(cabinet)==1
 pts=list(cabinet[0].get_points());h=max(p[1] for p in pts)-min(p[1] for p in pts);assert abs(h-1270)<1e-6
 report['dxf']={'version':doc.dxfversion,'closed_polylines':len(entities),'cabinet_height_mm':h,'cabinet_width_mm':max(p[0] for p in pts)-min(p[0] for p in pts),'audit_errors':0,'flattening_tolerance_mm':.02}
 for name,sz in [('Chibees_Sign_4K_Transparent.png',(4000,3000)),('Chibees_Sign_Exact_Cabinet_Preview.png',(2400,1800))]:
  im=Image.open(OUT/name);assert im.size==sz;assert im.mode=='RGBA';report[name]={'size':list(im.size),'dpi':list(im.info['dpi']),'alpha_extrema':im.getextrema()[3]}
 assert Image.open(OUT/'Chibees_Sign_4K_Transparent.png').getpixel((0,0))[3]==0
 report['matching_e_geometry']=True;report['splash_order_both_sides']=['red','green','yellow']
 eps=(OUT/'Chibees_Sign_Press_Ready_CMYK.eps').read_text()
 assert eps.startswith('%!PS-Adobe-3.0 EPSF-3.0') and '%%LanguageLevel: 3' in eps
 assert '%%DocumentProcessColors: Cyan Magenta Yellow Black' in eps
 assert not re.search(r'\b(?:setrgbcolor|colorimage|findfont|show)\b',eps)
 assert eps.count('newpath')==len(base)
 report['eps']={'language_level':3,'process':'CMYK','paths':eps.count('newpath'),'validation':'structural and path parity; no PostScript interpreter available'}
 mono=ET.parse(OUT/'Chibees_Sign_Monochrome_Vector.svg')
 mpaths=[el for el in mono.iter() if el.tag.endswith('path')]
 assert all(el.attrib.get('fill')==INK and 'stroke' not in el.attrib and el.attrib['d'].endswith('Z') for el in mpaths)
 report['mono']={'inks':1,'live_strokes':0,'all_contours_closed':True}
 return report

def main():
 OUT.mkdir(exist_ok=True);QA.mkdir(exist_ok=True)
 base=master();ops=Counter(c for s in base for c,p in commands(s.d))
 stats={'art_paths':len(base),'art_anchor_commands':ops['M']+ops['L']+ops['C'],'art_cubic_segments':ops['C'],'art_line_segments':ops['L'],'art_contours':ops['M'],'art_layers':len(set(s.layer for s in base)),'per_layer':{l:{'paths':sum(s.layer==l for s in base),'anchors':sum(len(anchors(s.d)[0]) for s in base if s.layer==l)} for l in LAYERS}}
 names={'exact':'Chibees_Sign_Exact_Cabinet_RGB','sticker':'Chibees_Sign_Framed_Sticker_Print','isolate':'Chibees_Sign_Transparent_Isolate','mono':'Chibees_Sign_Monochrome_Vector'}
 for kind,name in names.items():svg(edition(base,kind),OUT/(name+'.svg'))
 svg(night_scene(base),OUT/'Chibees_Sign_Neon_Night_Edition.svg')
 svg(wireframe(base),OUT/'Chibees_Sign_CtrlY_Wireframe_Blueprint.svg')
 pdf_write([move_shapes(base,1,0,60)],OUT/'Chibees_Sign_Master_Layered.ai',layered=True)
 eps_write(base,OUT/'Chibees_Sign_Press_Ready_CMYK.eps')
 pdf_write(spec_pages(base,stats),OUT/'Chibees_Sign_Press_Ready_CMYK.pdf')
 stats['dxf_layers']=dxf_write(base,OUT/'Chibees_Sign_50inch_CNC_Router.dxf')
 render_svg(OUT/(names['isolate']+'.svg'),OUT/'Chibees_Sign_4K_Transparent.png',4000,3000)
 render_svg(OUT/(names['exact']+'.svg'),OUT/'Chibees_Sign_Exact_Cabinet_Preview.png',2400,1800)
 for src in sorted(OUT.glob('*.svg')):render_svg(src,QA/(src.stem+'.png'),1080,810)
 doc=fitz.open(OUT/'Chibees_Sign_Press_Ready_CMYK.pdf')
 for i,p in enumerate(doc):p.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False).save(QA/f'spec_page_{i+1}.png')
 ai=fitz.open(OUT/'Chibees_Sign_Master_Layered.ai');ai[0].get_pixmap(alpha=False).save(QA/'ai_pdf_compatibility.png')
 report={'geometry':stats,'checks':validate(base),'source_sha256':hashlib.sha256((ROOT/'ref/sign_crop_1to1.png').read_bytes()).hexdigest(),'font_sha256':hashlib.sha256(FONT.read_bytes()).hexdigest(),'limitations':['Reconstruction of a photographed screen, not a source-art exactness certification.','50-inch cabinet height is a supplied design assumption, not a measured field dimension.','AI is a valid layered PDF-compatible interchange file, without proprietary Illustrator editing data; Illustrator round-trip untested.','Pantone references are suggested visual targets, not spot plates or measured matches.','DeviceCMYK PDF/EPS; no printer ICC profile or PDF/X certification.','DXF is nominal contour geometry, not kerf-compensated toolpaths.']}
 (OUT/'Chibees_Verification_Report.json').write_text(json.dumps(report,indent=2)+'\n')
 readme=f'''# Chibees vector engineering pack\n\nRebuild: `python3 build_chibees_vectors.py` from the project root.\n\nThe 6 SVG editions contain only outlined path artwork. Master: {stats['art_paths']} paths, {stats['art_anchor_commands']} anchor commands, {stats['art_cubic_segments']} cubic segments, 7 layers. Anchor count is M + L + C endpoints, including repeated closure endpoints; it is not a claim about Illustrator's UI node count.\n\n## Color\n- Fiesta red: #E22B24 / CMYK 0,92,95,0. Suggested Pantone 485 C or 1795 C; approve a physical swatch.\n- Green: #198C38 / CMYK 84,0,85,23.\n- Yellow: #F6C518 / CMYK 0,20,95,0.\n- Espresso: #231915 / CMYK 40,50,50,90.\n- Amber: #E58E1A / CMYK 0,43,89,10.\n\n## Production scope\n- Master .ai is a valid PDF 1.7 file with 7 optional-content layers, DeviceCMYK paths and XMP metadata. Opens through PDF-compatible import; not proprietary native AI editing data. Adobe Illustrator import/layer retention has not been interactively tested.\n- EPS is PostScript Level 3 with process CMYK operators and no font/image references.\n- 4-page PDF is a vector specification book in DeviceCMYK. No supplied printer ICC profile, OutputIntent or PDF/X certification; press acceptance requires printer proof. SVG effects are display treatments, not lighting construction plans.\n- The DXF is R2010 / AC1024 in mm: height 1270.00, width 2228.07, inferred from the reconstructed silhouette. All entities are closed LWPOLYLINE; cubic curves are adaptively flattened to 0.02 mm chord tolerance. CUT_CABINET is the exterior cut; VINYL_* are color artwork boundaries; DETAIL_ENGRAVE contains decoration. Color shapes overlap intentionally; CAM operator must select/boolean the desired plates, set tool/kerf/depth, and omit small detail where unsuitable.\n- White keyline is visible white artwork. Transparent PNG includes white artwork and a fully transparent background. On kraft media it needs white ink or a white vinyl substrate.\n- PNG dimensions: 4000 x 3000 and 2400 x 1800; 300 DPI metadata.\n\n## Source fidelity\nReconstruction from `ref/sign_crop_1to1.png`. The source is a photo of a display with moire and a cursor over the second e. Both e glyphs are exact translations of the same clean Bezier source (+85,+11 design units). Cabinet is symmetric; splash order is red/green/yellow on both sides. Micro-detail hidden by blur is reconstructed, not claimed as measured. 50-inch cabinet height follows the supplied brief and must be field-confirmed.\n\nNo platform submission or publication is performed by this generator.\n'''
 (OUT/'README_Production.md').write_text(readme)
 # Portable geometry snapshot lets other collaborators inspect points without importing fonts.
 (OUT/'Chibees_Master_Path_Data.json').write_text(json.dumps([s.__dict__ for s in base],indent=2)+'\n')
 manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.is_file() and p.suffix!='.zip' and p.name!='SHA256SUMS.txt'}
 (OUT/'SHA256SUMS.txt').write_text(''.join(f'{digest}  {name}\n' for name,digest in manifest.items()))
 archive=OUT/'Chibees_Mexican_Restaurant_Master_Vector_Pack.zip'
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(OUT.iterdir()):
   if p.is_file() and p.suffix!='.zip':
    info=zipfile.ZipInfo(p.name,(2026,11,9,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,p.read_bytes())
  info=zipfile.ZipInfo('build_chibees_vectors.py',(2026,11,9,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,Path(__file__).read_bytes())
 print(json.dumps({'geometry':stats,'validation':'passed','archive':str(archive)},indent=2))

if __name__=='__main__':main()
