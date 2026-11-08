"""Happy Diwali greeting video from Galaland (with real Hot Wheels photos, see CREDITS.md)."""
import math, random, subprocess, wave, sys, json
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageChops

W, H, FPS = 1080, 1920, 30
DUR = 29.0
NF = int(DUR * FPS)
R = random.Random(11)
LATIN = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
DEVA = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
GOLD, MAROON, WHITE, BLACK = (255, 200, 60), (90, 0, 20), (255, 255, 255), (0, 0, 0)
CREAM = (255, 240, 205)

@lru_cache(None)
def F(size, path=LATIN): return ImageFont.truetype(path, max(4, int(size)), layout_engine=ImageFont.Layout.RAQM)
def clamp(t): return min(max(t, 0.0), 1.0)
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_back(t):
    t = clamp(t); c = 1.7
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

def text(d, s, xy, size, fill=WHITE, stroke=6, sfill=MAROON, path=LATIN):
    if size >= 5: d.text(xy, s, font=F(size, path), fill=fill, stroke_width=stroke, stroke_fill=sfill, anchor="mm")

GRAD = np.zeros((400, 1, 3))
for k, (a, b) in enumerate([((255, 245, 180), (255, 200, 50)), ((255, 200, 50), (200, 120, 10))]):
    t = np.linspace(0, 1, 200)[:, None]
    GRAD[k * 200:(k + 1) * 200, 0] = np.array(a) * (1 - t) + np.array(b) * t
def gold_text(img, s, center, size, path=LATIN, stroke=None, alpha=1.0):
    if size < 6 or alpha <= 0: return
    f = F(size, path); stroke = int(size * 0.07) if stroke is None else stroke
    l, t_, r, b = f.getbbox(s, stroke_width=stroke)
    w, h = r - l + 4, b - t_ + 4
    mask_s = Image.new("L", (w, h)); ImageDraw.Draw(mask_s).text((-l + 2, -t_ + 2), s, font=f, fill=255, stroke_width=stroke)
    mask_f = Image.new("L", (w, h)); ImageDraw.Draw(mask_f).text((-l + 2, -t_ + 2), s, font=f, fill=255)
    grad = Image.fromarray(np.repeat(np.array(Image.fromarray(GRAD.astype(np.uint8)).resize((1, h))), w, axis=1), "RGB")
    if alpha < 1:
        mask_s = mask_s.point(lambda v: int(v * alpha)); mask_f = mask_f.point(lambda v: int(v * alpha))
    x0, y0 = int(center[0] - w / 2), int(center[1] - h / 2)
    img.paste(Image.new("RGB", (w, h), MAROON), (x0, y0), mask_s)
    img.paste(grad, (x0, y0), mask_f)

# ---------------------------------------------------------------- static layers
def vgrad(top, mid, bot):
    t = np.linspace(0, 1, H)[:, None]
    a = np.where(t < 0.6, np.array(top) * (1 - t / 0.6) + np.array(mid) * (t / 0.6),
                 np.array(mid) * (1 - (t - 0.6) / 0.4) + np.array(bot) * ((t - 0.6) / 0.4))
    return Image.fromarray(np.repeat(a[:, None, :], W, axis=1).astype(np.uint8), "RGB")
BG = vgrad((12, 4, 40), (70, 10, 60), (130, 30, 20))
STARS = [(R.uniform(0, W), R.uniform(0, H * 0.6), R.uniform(0, 6.28), R.uniform(1.5, 3.5)) for _ in range(120)]

def make_toran():
    im = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [0, 270, 540, 810, 1080]
    for a, b in zip(pts, pts[1:]):
        for k in range(26):
            u = k / 25; x = a + (b - a) * u; y = 40 + 95 * math.sin(math.pi * u)
            col = (255, 140, 0) if k % 2 else (255, 205, 20)
            d.ellipse([x - 19, y - 19, x + 19, y + 19], fill=col, outline=(200, 80, 0), width=2)
            for p in range(6):
                ang = p * math.pi / 3
                d.ellipse([x + 9 * math.cos(ang) - 6, y + 9 * math.sin(ang) - 6, x + 9 * math.cos(ang) + 6, y + 9 * math.sin(ang) + 6], fill=(255, 175, 0) if k % 2 else (255, 230, 80))
    for x in pts:
        for j in range(5):
            y = 40 + j * 34
            d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(255, 140, 0) if j % 2 else (255, 205, 20), outline=(200, 80, 0), width=2)
        d.polygon([(x - 14, 210), (x + 14, 210), (x, 250)], fill=(40, 150, 40))
    return im
TORAN = make_toran()

def make_rangoli(S=1000):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2
    rings = [(470, 32, (230, 30, 120)), (420, 24, (255, 140, 0)), (360, 16, (255, 220, 0)), (300, 16, (30, 170, 80)),
             (240, 12, (40, 120, 230)), (180, 12, (230, 30, 120)), (120, 8, (255, 140, 0))]
    for rad, n, col in rings:
        for k in range(n):
            a = 2 * math.pi * k / n; pl = rad * 0.32; pw = math.pi / n * 0.9
            tip = (c + rad * math.cos(a), c + rad * math.sin(a))
            base = rad - pl
            l = (c + base * math.cos(a - pw), c + base * math.sin(a - pw)); r = (c + base * math.cos(a + pw), c + base * math.sin(a + pw))
            mid = (c + (base + pl * 0.45) * math.cos(a), c + (base + pl * 0.45) * math.sin(a))
            d.polygon([l, tip, r, (c + (base - 8) * math.cos(a), c + (base - 8) * math.sin(a))], fill=col, outline=WHITE, width=3)
            d.ellipse([mid[0] - 5, mid[1] - 5, mid[0] + 5, mid[1] + 5], fill=WHITE)
    for k in range(64):
        a = 2 * math.pi * k / 64; x, y = c + 490 * math.cos(a), c + 490 * math.sin(a)
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=WHITE)
    d.ellipse([c - 70, c - 70, c + 70, c + 70], fill=(255, 220, 0), outline=WHITE, width=5)
    d.ellipse([c - 35, c - 35, c + 35, c + 35], fill=(230, 30, 120))
    return im
RANGOLI = make_rangoli()

# ---------------------------------------------------------------- photos (real Hot Wheels)
PH = {}
def framed(i, box=(820, 600)):
    if i in PH: return PH[i]
    im = ImageOps.exif_transpose(Image.open(f"photos/{i:02d}.jpg")).convert("RGB")
    im = ImageOps.fit(im, box, Image.LANCZOS) if i != 15 else ImageOps.fit(im, (box[1], box[1]), Image.LANCZOS)
    w, h = im.size; pad = 26
    fr = Image.new("RGBA", (w + 2 * pad + 40, h + 2 * pad + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(fr)
    d.rounded_rectangle([20, 26, w + 2 * pad + 20, h + 2 * pad + 32], 26, fill=(0, 0, 0, 140))
    fr = fr.filter(ImageFilter.GaussianBlur(10)); d = ImageDraw.Draw(fr)
    d.rounded_rectangle([20, 20, w + 2 * pad + 20, h + 2 * pad + 20], 26, fill=(230, 160, 30), outline=(120, 40, 0), width=4)
    d.rounded_rectangle([30, 30, w + 2 * pad + 10, h + 2 * pad + 10], 20, outline=(255, 235, 150), width=4)
    for k in range(0, w + 2 * pad, 34):
        d.ellipse([20 + k + 14, 22, 20 + k + 22, 30], fill=(255, 245, 190)); d.ellipse([20 + k + 14, h + 2 * pad + 10, 20 + k + 22, h + 2 * pad + 18], fill=(255, 245, 190))
    fr.paste(im, (20 + pad, 20 + pad))
    PH[i] = fr
    return fr
def paste_photo(img, i, lt, cy, sway=True):
    fr = framed(i)
    s = ease_back(lt / 0.45) * (1 + 0.03 * math.sin(lt * 2))
    if s < 0.03: return
    f2 = fr.resize((int(fr.width * s), int(fr.height * s)), Image.BILINEAR)
    if sway: f2 = f2.rotate(1.5 * math.sin(lt * 1.7), resample=Image.BILINEAR, expand=True)
    img.paste(f2, (int(W / 2 - f2.width / 2), int(cy - f2.height / 2)), f2)

# ---------------------------------------------------------------- lights
PALETTES = [[(255, 210, 80), (255, 240, 170)], [(255, 60, 80), (255, 160, 120)], [(80, 255, 120), (200, 255, 160)],
            [(255, 90, 220), (255, 180, 240)], [(90, 160, 255), (200, 220, 255)], [(255, 150, 30), (255, 220, 120)]]
BURSTS = []
t = 0.4
while t < 27:
    gap = 0.28 if t > 20 else R.uniform(0.5, 0.9)
    BURSTS.append(dict(t0=t, x=R.uniform(140, W - 140), y=R.uniform(220, 900), pal=R.choice(PALETTES), n=R.randint(50, 80),
                       sp=R.uniform(320, 520), seed=R.randint(0, 10**6), rx=R.uniform(200, W - 200)))
    t += gap
for b in BURSTS:
    rr = random.Random(b["seed"])
    b["parts"] = [(2 * math.pi * k / b["n"] + rr.uniform(-.05, .05), b["sp"] * rr.uniform(0.75, 1.15), rr.random()) for k in range(b["n"])]
LIFE, RISE = 1.8, 0.6
def fireworks(g, t):
    for b in BURSTS:
        a = t - b["t0"]
        if -RISE < a < 0:
            u = (a + RISE) / RISE; x = b["rx"] + (b["x"] - b["rx"]) * u; y = H * 0.75 + (b["y"] - H * 0.75) * ease_out(u)
            g.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 220, 150))
            g.line([x, y, x - (b["x"] - b["rx"]) * 0.05, y + 60], fill=(180, 120, 60), width=3)
        elif 0 <= a < LIFE:
            fade = (1 - a / LIFE) ** 1.4; k = 2.2
            for ang, v, ph in b["parts"]:
                def pos(aa):
                    dist = v * (1 - math.exp(-k * aa)) / k
                    return b["x"] + dist * math.cos(ang), b["y"] + dist * math.sin(ang) + 60 * aa * aa
                x1, y1 = pos(max(0, a - 0.08)); x2, y2 = pos(a)
                tw = 1.0 if a < 0.9 else (0.4 + 0.6 * (math.sin(t * 40 + ph * 20) > 0))
                col = b["pal"][0 if ph < 0.6 else 1]
                col = tuple(int(c * fade * tw) for c in col)
                g.line([x1, y1, x2, y2], fill=col, width=6)
            if a < 0.12:
                r = 60 * (1 - a / 0.12); g.ellipse([b["x"] - r, b["y"] - r, b["x"] + r, b["y"] + r], fill=(255, 255, 230))

def add_glow(img, glow, blur=6, strength=1.0, sharp=True):
    small = glow.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(blur))
    halo = small.resize((W, H), Image.BILINEAR)
    if strength != 1.0: halo = halo.point(lambda v: min(255, int(v * strength)))
    out = ImageChops.add(img, halo)
    return ImageChops.add(out, glow) if sharp else out

def diya(d, g, x, y, s, t, ph):
    d.chord([x - 70 * s, y - 50 * s, x + 70 * s, y + 45 * s], 0, 180, fill=(170, 60, 15), outline=(90, 25, 5), width=3)
    d.polygon([(x + 55 * s, y - 2 * s), (x + 95 * s, y - 14 * s), (x + 62 * s, y + 14 * s)], fill=(170, 60, 15), outline=(90, 25, 5))
    d.ellipse([x - 70 * s, y - 14 * s, x + 70 * s, y + 10 * s], fill=(215, 105, 35), outline=(90, 25, 5), width=3)
    d.ellipse([x - 55 * s, y - 7 * s, x + 55 * s, y + 5 * s], fill=(120, 50, 10))
    for k in range(7):
        xx = x - 45 * s + k * 15 * s
        d.ellipse([xx - 4 * s, y + 22 * s, xx + 4 * s, y + 30 * s], fill=(255, 210, 60))
    fx, fy = x + 85 * s, y - 14 * s
    fl = 1 + 0.15 * math.sin(t * 17 + ph) + 0.08 * math.sin(t * 31 + ph * 2)
    hgt = 62 * s * fl; wd = 17 * s; sw = 4 * s * math.sin(t * 9 + ph)
    def drop(hh, ww, col, dd):
        pts = [(fx + sw, fy - hh)]
        for k in range(13):
            a = math.pi * k / 12
            pts.append((fx + ww * math.cos(math.pi - a), fy - ww * 0.2 + ww * math.sin(a) * 0.9))
        dd.polygon(pts, fill=col)
    g.ellipse([fx - 90 * s, fy - 120 * s, fx + 90 * s, fy + 40 * s], fill=(160, 70, 10))
    drop(hgt, wd, (255, 120, 10), d); drop(hgt * 0.75, wd * 0.7, (255, 210, 40), d); drop(hgt * 0.4, wd * 0.4, (255, 255, 220), d)
    drop(hgt, wd, (255, 150, 30), g)

def lantern(d, g, x, t, ph, top=0, L=360):
    sw = 0.08 * math.sin(t * 1.6 + ph)
    cx, cy = x + L * math.sin(sw), top + L * math.cos(sw)
    d.line([x, top, cx, cy - 70], fill=(220, 180, 120), width=3)
    pts = []
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8 + sw; rr = 80 if k % 2 == 0 else 50
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=(230, 60, 20), outline=(255, 210, 60), width=4)
    d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(255, 200, 60))
    for k in range(5):
        d.line([cx - 24 + k * 12, cy + 60, cx - 30 + k * 15, cy + 140 + 6 * math.sin(t * 3 + k)], fill=(255, 190, 40), width=4)
    g.ellipse([cx - 110, cy - 110, cx + 110, cy + 110], fill=(150, 50, 10))

COINS = [dict(x=R.uniform(40, W - 40), y=R.uniform(-H, 0), v=R.uniform(350, 650), ph=R.uniform(0, 6.28), s=R.uniform(26, 44)) for _ in range(45)]
def coins(d, t):
    for c in COINS:
        y = c["y"] + c["v"] * t
        if y > H + 60: continue
        w = c["s"] * abs(math.cos(t * 5 + c["ph"])) + 3; s = c["s"]
        d.ellipse([c["x"] - w, y - s, c["x"] + w, y + s], fill=(250, 190, 30), outline=(170, 100, 0), width=3)
        if w > 14: d.ellipse([c["x"] - w * 0.6, y - s * 0.6, c["x"] + w * 0.6, y + s * 0.6], outline=(255, 235, 140), width=3)

SPARKS = [(R.uniform(0, W), R.uniform(0, H), R.uniform(0, 6.28), R.uniform(8, 22)) for _ in range(50)]
def sparkles(d, t):
    for (sx, sy, ph, sz) in SPARKS:
        r = sz * max(0, math.sin(t * 4 + ph))
        if r > 1:
            d.polygon([(sx, sy - r), (sx + r * .2, sy - r * .2), (sx + r, sy), (sx + r * .2, sy + r * .2), (sx, sy + r),
                       (sx - r * .2, sy + r * .2), (sx - r, sy), (sx - r * .2, sy - r * .2)], fill=(255, 235, 160))

DIYA_X = [110, 330, 550, 770, 990]

# ---------------------------------------------------------------- frame composition
def base(t, rangoli_cy=None, rangoli_alpha=0.0):
    img = BG.copy(); d = ImageDraw.Draw(img)
    for (sx, sy, ph, sz) in STARS:
        v = int(150 + 105 * math.sin(t * 2 + ph)); r = sz
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(v, v, min(255, v + 30)))
    g = Image.new("RGB", (W, H)); fireworks(ImageDraw.Draw(g), GT)
    img = add_glow(img, g, 5, 1.3)
    if rangoli_cy is not None and rangoli_alpha > 0:
        r = RANGOLI.rotate(t * 18, resample=Image.BILINEAR)
        sc = 0.75 + 0.25 * ease_out(rangoli_alpha)
        r = r.resize((int(1000 * sc), int(1000 * sc)), Image.BILINEAR)
        if rangoli_alpha < 1: r.putalpha(r.getchannel("A").point(lambda v: int(v * rangoli_alpha)))
        img.paste(r, (int(W / 2 - r.width / 2), int(rangoli_cy - r.height / 2)), r)
    return img

def finish(img, t, diyas=True, lanterns=True):
    d = ImageDraw.Draw(img); g = Image.new("RGB", (W, H)); gd = ImageDraw.Draw(g)
    if lanterns:
        lantern(d, gd, 110, t, 0.0, 120, 200); lantern(d, gd, 970, t, 1.7, 120, 200)
    if diyas:
        d.rectangle([0, 1780, W, H], fill=(60, 10, 10))
        for k, x in enumerate(DIYA_X): diya(d, gd, x - 30, 1800, 0.95, t, k * 1.3)
    img = add_glow(img, g, 10, 1.6, sharp=False)
    img.paste(TORAN, (0, 0), TORAN)
    return img

def scene_intro(t):
    img = base(t)
    img = finish(img, t)
    d = ImageDraw.Draw(img)
    a = ease_back((t - 0.3) / 0.6)
    gold_text(img, "शुभ दीपावली", (540, 620), 150 * a, DEVA)
    b = ease_back((t - 1.2) / 0.6)
    gold_text(img, "HAPPY", (540, 820), 130 * b, SERIF)
    c = ease_back((t - 1.6) / 0.6)
    gold_text(img, "DIWALI", (540, 980), 175 * c, SERIF)
    e = clamp((t - 2.6) / 0.5)
    if e > 0:
        y = 1200 + (1 - ease_out(e)) * 60
        text(d, "from all of us at", (540, y), 52, CREAM, 4)
        gold_text(img, "GALALAND", (540, y + 120), 120)
    sparkles(d, t)
    return img

def wish_scene(t, photo_seq, line1, line2, extra=None):
    img = base(t, 1080, clamp(t / 0.6))
    if extra == "coins": coins(ImageDraw.Draw(img), t)
    seg = 5.0 / len(photo_seq); n = min(int(t / seg), len(photo_seq) - 1)
    paste_photo(img, photo_seq[n], t - n * seg, 1100)
    img = finish(img, t, diyas=True, lanterns=False)
    d = ImageDraw.Draw(img)
    a = ease_back((t - 0.2) / 0.5); b = ease_back((t - 0.5) / 0.5)
    text(d, line1, (540, 330), 72 * a, CREAM, 6)
    gold_text(img, line2, (540, 470), 100 * b, SERIF)
    c = clamp((t - 0.8) / 0.5)
    if c > 0:
        text(d, "Happy Diwali from", (540, 1580), 46, CREAM, 4)
        gold_text(img, "GALALAND", (540, 1665), 80, alpha=c)
    sparkles(d, t * 1.3)
    return img

def scene_new(t): return wish_scene(t, [0, 9], "May this Diwali bring", "SHINY NEW CARS")
def scene_chase(t): return wish_scene(t, [5, 1], "lots of exciting", "CHASE CARS")
def scene_sth(t): return wish_scene(t, [15, 4], "and lucky", "STH FINDS!", "coins")

def scene_final(t):
    img = base(t, 1050, clamp(t / 0.8) * 0.55)
    img = finish(img, t)
    d = ImageDraw.Draw(img)
    gold_text(img, "शुभ दीपावली", (540, 420), 120 * ease_back(t / 0.6), DEVA)
    s = 1 + 0.03 * math.sin(t * 4)
    gold_text(img, "HAPPY DIWALI", (540, 620), 125 * ease_back((t - 0.3) / 0.6) * s, SERIF)
    a = clamp((t - 1.0) / 0.5)
    if a > 0:
        y = 840 + (1 - ease_out(a)) * 50
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ov).rounded_rectangle([90, y - 70, 990, y + 250], 40, fill=(40, 0, 30, int(170 * a)))
        img.paste(ov, (0, 0), ov); d = ImageDraw.Draw(img)
        for k, line in enumerate(["Wishing everyone", "light, joy, prosperity", "& great success!"]):
            text(d, line, (540, y + k * 90), 66, CREAM, 6)
    b = ease_back((t - 2.0) / 0.6)
    if b > 0:
        d.rounded_rectangle([540 - 330 * b, 1300 - 110 * b, 540 + 330 * b, 1300 + 110 * b], int(40 * b) + 1,
                            fill=(120, 0, 30), outline=GOLD, width=6)
        text(d, "Team", (540, 1245), 48 * b, CREAM, 3)
        gold_text(img, "GALALAND", (540, 1325), 105 * b)
    c = clamp((t - 3.0) / 0.5)
    if c > 0: text(d, "Diecast • Chase • STH", (540, 1500), 50, (255, 225, 150), 5)
    sparkles(d, t)
    return img

CREDITS = {k: v for k, v in json.load(open("credits.json")).items() if int(k) in (0, 1, 4, 5, 9, 15)}
def scene_credits(t):
    img = Image.new("RGB", (W, H), (20, 4, 20)); d = ImageDraw.Draw(img)
    gold_text(img, "Happy Diwali!", (540, 520), 110, SERIF)
    text(d, "Car photos: Wikimedia Commons", (540, 720), 42, CREAM, 0)
    y = 800
    for k, v in sorted(CREDITS.items(), key=lambda kv: int(kv[0])):
        text(d, f"{v['artist'][:28]} — {v['license']}", (540, y), 36, (210, 200, 200), 0); y += 62
    text(d, "Hot Wheels is a trademark of Mattel. Not affiliated.", (540, y + 60), 30, (160, 150, 150), 0)
    return img

SCENES = [(0, 5, scene_intro), (5, 10, scene_new), (10, 15, scene_chase), (15, 20, scene_sth), (20, 27, scene_final), (27, 29, scene_credits)]
CUTS = [s[0] for s in SCENES[1:]]
GT = 0.0
def frame(i):
    global GT
    t = i / FPS; GT = t
    for a, b, fn in SCENES:
        if a <= t < b: img = fn(t - a); break
    for c in CUTS:
        dt = t - c
        if 0 <= dt < 0.3: img = Image.blend(img, Image.new("RGB", (W, H), (255, 230, 170)), 0.8 * (1 - dt / 0.3))
    if t < 0.4: img = Image.blend(Image.new("RGB", (W, H)), img, t / 0.4)
    if t > DUR - 0.4: img = Image.blend(img, Image.new("RGB", (W, H)), (t - (DUR - 0.4)) / 0.4)
    return img

# ---------------------------------------------------------------- audio
SR = 44100; N = int(SR * DUR); audio = np.zeros(N); tt = np.arange(N) / SR; rng = np.random.default_rng(3)
def add(sig, start, gain=1.0):
    s = int(start * SR); e = min(N, s + len(sig))
    if 0 <= s < N: audio[s:e] += gain * sig[:e - s]
SA = 293.66
RATIO = {"S": 1, "R": 9/8, "G": 5/4, "m": 4/3, "P": 3/2, "D": 5/3, "N": 15/8, "S'": 2, "R'": 9/4, "G'": 5/2, ".D": 5/6, ".P": 3/4}
BPM = 104; Q = 60 / BPM
MUSIC_END = 27.0
# tanpura drone
for st in np.arange(0, MUSIC_END, Q * 4):
    for k, (f, off) in enumerate([(SA * 3 / 4, 0), (SA, 1), (SA, 2), (SA / 2, 3)]):
        L = int(3.5 * SR); x = np.arange(L) / SR
        sig = sum(np.sin(2 * np.pi * f * h * x * (1 + 0.0007 * h)) / h ** 0.8 for h in range(1, 9)) * np.exp(-x * 0.9) * np.minimum(1, x * 30)
        add(sig, st + off * Q, 0.035)
# tabla
def bayan(L=0.45):
    x = np.arange(int(L * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(75 + 40 * (1 - np.exp(-x * 6))) / SR) * np.exp(-x * 7) * 0.8
def dayan(f=520, L=0.25):
    x = np.arange(int(L * SR)) / SR
    return sum(np.sin(2 * np.pi * f * m * x) * a for m, a in [(1, 1), (2, .5), (3, .3), (4.2, .15)]) * np.exp(-x * 16) * 0.35
def slap(L=0.08):
    x = np.arange(int(L * SR)); return np.diff(rng.standard_normal(len(x) + 1)) * np.exp(-x / SR * 60) * 0.25
def mix(*sigs):
    out = np.zeros(max(len(x) for x in sigs))
    for x in sigs: out[:len(x)] += x
    return out
BOLS = {"dha": lambda: mix(bayan(), dayan()), "dhin": lambda: mix(bayan(0.3) * 0.7, dayan(560)), "na": lambda: dayan(620), "ta": lambda: mix(dayan(600), slap()),
        "tin": lambda: dayan(700, 0.15), "ge": lambda: bayan(0.25) * 0.6, "-": None}
PAT = "dha dhin dhin dha dha dhin dhin dha dha tin tin ta ta dhin dhin dha".split()
EIGHTH = Q / 2
k = 0
for st in np.arange(1.2, MUSIC_END, EIGHTH):
    b = PAT[k % 16]; k += 1
    if BOLS[b]: add(BOLS[b](), st, 0.9)
    if k % 2 == 0: add(dayan(900, 0.06) * 0.4, st + EIGHTH / 2)
# shehnai-like melody
def note(f, dur):
    L = int(dur * SR); x = np.arange(L) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * x) * np.minimum(1, x * 4)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    sig = sum(np.sin(h * ph) * a for h, a in [(1, 1), (2, .7), (3, .55), (4, .35), (5, .25), (6, .15), (7, .1)])
    env = np.minimum(1, x / 0.03) * np.minimum(1, (dur - x) / 0.06) * (0.85 + 0.15 * np.exp(-x * 3))
    return sig * env
A = [("G", 1), ("P", 1), ("D", 1), ("P", 1), ("G", 1), ("R", 1), ("S", 2), ("R", 1), ("G", 1), ("P", 1), ("G", 1), ("R", 4)]
B = [("G", 1), ("P", 1), ("D", 1), ("S'", 1), ("D", .5), ("S'", .5), ("D", 1), ("P", 1), ("G", 1), ("P", 1), ("G", 1), ("R", 1), ("S", 4)]
C = [("S'", 1), ("R'", 1), ("G'", 2), ("R'", 1), ("S'", 1), ("D", 2), ("P", 1), ("D", 1), ("S'", 1), ("D", 1), ("P", 2), ("G", 2)]
mel = A + B + C + B + A
st = 1.2 + Q * 4
for nm, beats in mel:
    if st > MUSIC_END - 0.5: break
    add(note(SA * RATIO[nm], beats * Q), st, 0.07); st += beats * Q
# temple bells
def bell(f=880, L=4.0):
    x = np.arange(int(L * SR)) / SR
    return sum(np.sin(2 * np.pi * f * m * x) * a * np.exp(-x * d) for m, a, d in [(1, 1, 1.0), (2.76, .5, 1.8), (5.4, .3, 3), (8.9, .15, 5)])
for st in [0.0, 20.0, 27.0]: add(bell(), st, 0.12)
# firework sounds
for b in BURSTS:
    L = int(1.6 * SR); x = np.arange(L) / SR
    boom = np.convolve(rng.standard_normal(L), np.ones(40) / 40, "same") * np.exp(-x * 5) * 1.4
    crack = np.zeros(L)
    for _ in range(40):
        p = int(rng.uniform(0.25, 1.4) * SR); crack[p:p + 300] += rng.standard_normal(300) * np.exp(-np.arange(300) / 40) * 0.5
    add(boom + crack * 0.6, b["t0"], 0.35 if b["t0"] < 20 else 0.25)
    wl = int(RISE * SR); xw = np.arange(wl) / SR
    add(np.sin(2 * np.pi * np.cumsum(1200 + 1500 * xw / RISE) / SR) * 0.04 * np.sin(np.pi * xw / RISE), b["t0"] - RISE)
audio *= np.clip((MUSIC_END + 1.5 - tt) / 1.5, 0, 1) * np.clip(tt / 0.3, 0, 1)
audio = np.tanh(audio / np.max(np.abs(audio)) * 1.3) * 0.85
with wave.open("audio_diwali.wav", "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((audio * 32767).astype(np.int16).tobytes())

if len(sys.argv) > 1 and sys.argv[1] == "preview":
    secs = [4.5, 8, 12.5, 18, 25.5]
    ims = [frame(int(s * FPS)).resize((W // 3, H // 3)) for s in secs]
    sh = Image.new("RGB", (W // 3 * len(ims), H // 3))
    for k, im in enumerate(ims): sh.paste(im, (k * W // 3, 0))
    sh.save("preview_diwali.png"); sys.exit()
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                      "-i", "-", "-i", "audio_diwali.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                      "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", "Galaland_Happy_Diwali.mp4"], stdin=subprocess.PIPE)
for i in range(NF): p.stdin.write(frame(i).tobytes())
p.stdin.close(); p.wait(); print("done")
