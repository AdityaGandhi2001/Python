"""Galaland - Happy Diwali (cinematic edit). Real photos from Wikimedia Commons, see CREDITS.md."""
import math, random, subprocess, wave, sys, json
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H, FPS = 1080, 1920, 30
BPM = 96; B = 60 / BPM
DUR = 28.0
NF = int(DUR * FPS)
rnd = random.Random(5)

def clamp(t): return min(max(t, 0.0), 1.0)
def eo(t): t = clamp(t); return 1 - (1 - t) ** 4            # ease-out quart
def eio(t): t = clamp(t); return t * t * (3 - 2 * t)          # smoothstep
def env(t, a, b, fi=0.6, fo=0.6):                             # fade in at a, out at b
    return clamp((t - a) / fi) * clamp((b - t) / fo)

@lru_cache(None)
def F(name, size): return ImageFont.truetype("fonts/" + name, int(size), layout_engine=ImageFont.Layout.RAQM)

# ------------------------------------------------------------------ photo plates
PLATES = {}
def plate(name, fx=0.5, fy=0.5, extra=1.18, blur=0):
    key = (name, blur)
    if key in PLATES: return PLATES[key]
    im = ImageOps.exif_transpose(Image.open("photos/" + name)).convert("RGB")
    tw, th = int(W * extra), int(H * extra)
    s = max(tw / im.width, th / im.height)
    im = im.resize((int(im.width * s + 1), int(im.height * s + 1)), Image.LANCZOS)
    x0 = int(clamp(fx - tw / im.width / 2) * im.width); x0 = min(x0, im.width - tw)
    y0 = int(clamp(fy - th / im.height / 2) * im.height); y0 = min(y0, im.height - th)
    im = im.crop((x0, y0, x0 + tw, y0 + th))
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    PLATES[key] = im
    return im

def kb(name, lt, dur, z0=1.0, z1=1.12, px=0.0, py=0.0, fx=0.5, fy=0.5, blur=0, punch=0.0):
    """Ken Burns move on a plate: zoom z0->z1, pan px/py (fraction of slack)."""
    im = plate(name, fx, fy, blur=blur)
    u = eio(lt / dur) * 0.85 + 0.15 * (lt / dur)
    z = z0 + (z1 - z0) * u + punch
    pw, ph = im.size
    cw, ch = pw / 1.18 / z * 1.0, ph / 1.18 / z
    cw, ch = W / z * (pw / (W * 1.18)) * 1.18 / 1.18, H / z * (ph / (H * 1.18)) * 1.18 / 1.18
    cw, ch = pw / z / 1.18, ph / z / 1.18
    cx = pw / 2 + px * (pw - cw) / 2 * (2 * u - 1)
    cy = ph / 2 + py * (ph - ch) / 2 * (2 * u - 1)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return np.asarray(im.resize((W, H), Image.BICUBIC, box=box), dtype=np.float32) / 255.0

# ------------------------------------------------------------------ grading / finishing
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.55 * np.clip(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2, 0, 1) ** 1.3)[..., None]
GRAIN = [np.asarray(Image.fromarray((np.random.default_rng(k).normal(128, 40, (H // 2, W // 2))).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), dtype=np.float32)[..., None] / 255 - 0.5 for k in range(6)]
def grade(x):
    x = np.clip(x, 0, 1)
    x = x * x * (3 - 2 * x) * 0.35 + x * 0.65                   # gentle S-curve
    lum = x.mean(axis=2, keepdims=True)
    warm = np.array([1.06, 0.98, 0.86], np.float32)
    shadow = np.array([0.02, 0.005, 0.03], np.float32)          # plum shadows
    x = x * warm * (0.75 + 0.25 * lum) / (0.75 + 0.25 * lum) + shadow * (1 - lum)
    return x * VIG

# embers rising
EMB = [dict(x=rnd.uniform(0, W), y0=rnd.uniform(0, H + 400), v=rnd.uniform(40, 140), sw=rnd.uniform(10, 40), ph=rnd.uniform(0, 6.3),
            r=rnd.uniform(1.5, 5.5), c=rnd.choice([(255, 170, 60), (255, 120, 30), (255, 210, 120)])) for _ in range(110)]
def embers(t, amt=1.0):
    g = Image.new("RGB", (W // 2, H // 2)); d = ImageDraw.Draw(g)
    for e in EMB:
        y = (e["y0"] - e["v"] * t) % (H + 400) - 200
        x = e["x"] + e["sw"] * math.sin(t * 0.9 + e["ph"])
        fl = (0.55 + 0.45 * math.sin(t * 6 + e["ph"] * 3)) * amt
        c = tuple(int(v * fl) for v in e["c"]); r = e["r"] / 2
        d.ellipse([x / 2 - r, y / 2 - r, x / 2 + r, y / 2 + r], fill=c)
    halo = g.filter(ImageFilter.GaussianBlur(4))
    a = (np.asarray(g, np.float32) + np.asarray(halo, np.float32) * 1.8) / 255
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255

def light_leak(t, t0, dur=1.0, hue=(1.0, 0.45, 0.12), side=1):
    u = (t - t0) / dur
    if not 0 <= u <= 1: return 0
    a = math.sin(math.pi * u)
    cx = W * (0.5 + side * (1.2 * u - 0.6)); cy = H * (0.35 + 0.3 * u)
    d2 = ((xx - cx) / (W * 0.55)) ** 2 + ((yy - cy) / (H * 0.45)) ** 2
    return (np.exp(-d2 * 1.6) * a * 0.85)[..., None] * np.array(hue, np.float32)

# ------------------------------------------------------------------ typography
GOLD_TOP, GOLD_BOT = np.array([255, 241, 196]), np.array([214, 150, 52])
def text_img(s, font, size, track=0, fill="gold"):
    f = F(font, size)
    if track == 0:
        l, t_, r, b = f.getbbox(s); w, h = r - l + 8, b - t_ + 8
        m = Image.new("L", (w, h)); ImageDraw.Draw(m).text((-l + 4, -t_ + 4), s, font=f, fill=255)
    else:
        adv = [f.getlength(c) + track for c in s]; w = int(sum(adv) - track + 8)
        asc, desc = f.getmetrics(); h = asc + desc + 8
        m = Image.new("L", (w, h)); dd = ImageDraw.Draw(m); x = 4
        for c, a in zip(s, adv): dd.text((x, 4), c, font=f, fill=255); x += a
    m = np.asarray(m, np.float32) / 255
    if fill == "gold":
        g = np.linspace(0, 1, m.shape[0])[:, None, None]
        col = (GOLD_TOP * (1 - g) + GOLD_BOT * g) / 255 * np.ones((1, m.shape[1], 1))
    else:
        col = np.ones((m.shape[0], m.shape[1], 3)) * np.array(fill, np.float32) / 255
    return col.astype(np.float32), m

TXT = {}
def T(key, *a, **k):
    if key not in TXT: TXT[key] = text_img(*a, **k)
    return TXT[key]

def put(frame, key, cx, cy, alpha=1.0, rise=0.0, blur=0.0, glow=0.35, scale=1.0):
    if alpha <= 0.003: return
    col, m = TXT[key]
    if scale != 1.0 or blur > 0.3:
        mi = Image.fromarray((m * 255).astype(np.uint8))
        if scale != 1.0: mi = mi.resize((max(1, int(mi.width * scale)), max(1, int(mi.height * scale))), Image.BILINEAR)
        if blur > 0.3: mi = mi.filter(ImageFilter.GaussianBlur(blur))
        m2 = np.asarray(mi, np.float32) / 255
        col = np.asarray(Image.fromarray((col * 255).astype(np.uint8)).resize((m2.shape[1], m2.shape[0]), Image.BILINEAR), np.float32) / 255
        m = m2
    h, w = m.shape
    x0, y0 = int(cx - w / 2), int(cy - h / 2 + rise)
    x1, y1 = x0 + w, y0 + h
    sx0, sy0 = max(0, -x0), max(0, -y0); x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(W, x1), min(H, y1)
    if x1 <= x0 or y1 <= y0: return
    mm = m[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)][..., None] * alpha
    cc = col[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
    if glow > 0:   # soft warm glow behind text
        gi = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(6, h * 0.12)))
        gm = np.asarray(gi, np.float32)[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)][..., None] / 255
        frame[y0:y1, x0:x1] += gm * glow * alpha * np.array([1.0, 0.55, 0.15], np.float32)
        # dark soft shadow for legibility
        frame[y0:y1, x0:x1] *= 1 - gm * 0.6 * alpha
    frame[y0:y1, x0:x1] = frame[y0:y1, x0:x1] * (1 - mm) + cc * mm

def reveal(frame, key, cx, cy, t, t_in, t_out, rise=40, glow=0.35, blur_amt=10):
    a = clamp((t - t_in) / 0.7) * clamp((t_out - t) / 0.5)
    if a <= 0: return
    u = eo((t - t_in) / 0.9)
    put(frame, key, cx, cy, alpha=a, rise=(1 - u) * rise, blur=(1 - u) * blur_amt, glow=glow)

def scrim(frame, cy, sigma, k):
    m = 1 - k * np.exp(-((np.arange(H, dtype=np.float32) - cy) / sigma) ** 2)
    frame *= m[:, None, None]

def hline(frame, cx, cy, half, alpha, thick=2):
    if alpha <= 0 or half < 2: return
    x0, x1 = int(cx - half), int(cx + half)
    ramp = np.abs(np.linspace(-1, 1, x1 - x0))[None, :, None]
    frame[int(cy):int(cy) + thick, x0:x1] = frame[int(cy):int(cy) + thick, x0:x1] * (1 - alpha * (1 - ramp)) + np.array([1, .85, .55], np.float32) * alpha * (1 - ramp)

# ------------------------------------------------------------------ product card (real Hot Wheels photo)
CARDS = {}
def card(name):
    if name in CARDS: return CARDS[name]
    im = ImageOps.exif_transpose(Image.open("photos/" + name)).convert("RGB")
    im = ImageOps.fit(im, (840, 840) if "15" in name else (840, 620), Image.LANCZOS)
    m = Image.new("L", im.size); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], 28, fill=255)
    CARDS[name] = (np.asarray(im, np.float32) / 255, np.asarray(m, np.float32) / 255)
    return CARDS[name]

def put_card(frame, name, lt, dur, cy=900):
    img, m = card(name)
    u = eo(lt / 0.8); out = clamp((lt - (dur - 0.35)) / 0.35)
    s = (0.86 + 0.14 * u) * (1 + 0.04 * lt / dur) * (1 - 0.06 * out)
    a = u * (1 - out)
    if a <= 0: return
    h, w = m.shape; nw, nh = int(w * s), int(h * s)
    im2 = np.asarray(Image.fromarray((img * 255).astype(np.uint8)).resize((nw, nh), Image.BICUBIC), np.float32) / 255
    m2 = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((nw, nh), Image.BILINEAR), np.float32) / 255
    # light sweep (glossy shine) across card
    sweep = (lt - 0.35) / 0.9
    if 0 < sweep < 1:
        gx = np.arange(nw)[None, :] + np.arange(nh)[:, None] * 0.6
        band = np.exp(-((gx - sweep * (nw + nh * 0.6)) / 60) ** 2)[..., None]
        im2 = np.clip(im2 + band * 0.35, 0, 1)
    # warm grade on the photo so it sits in the scene
    im2 = im2 * np.array([1.04, 0.97, 0.88], np.float32)
    x0 = int(W / 2 - nw / 2); y0 = int(cy - nh / 2 + (1 - u) * 60)
    # shadow + warm rim glow
    sh = Image.fromarray((m2 * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(30))
    shm = np.asarray(sh, np.float32)[..., None] / 255
    sy, sx = y0 + 30, x0
    region = frame[sy:sy + nh, sx:sx + nw]; region *= 1 - shm[:region.shape[0], :region.shape[1]] * 0.7 * a
    gl = np.asarray(Image.fromarray((m2 * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(45)), np.float32)[..., None] / 255
    frame[y0:y0 + nh, x0:x0 + nw] += gl * 0.25 * a * np.array([1, .55, .15], np.float32)
    mm = m2[..., None] * a
    frame[y0:y0 + nh, x0:x0 + nw] = frame[y0:y0 + nh, x0:x0 + nw] * (1 - mm) + im2 * mm

# ------------------------------------------------------------------ text assets
T("presents1", "GALALAND", "Montserrat-Medium.ttf", 46, track=22)
T("presents2", "PRESENTS", "Montserrat-Light.ttf", 26, track=14, fill=(235, 220, 200))
T("shubh", "शुभ दीपावली", "Tiro-Deva.ttf", 170)
T("happy", "Happy Diwali", "Playfair-Italic.ttf", 140)
T("fol", "THE FESTIVAL OF LIGHTS", "Montserrat-Light.ttf", 30, track=12, fill=(240, 225, 205))
T("this", "THIS DIWALI", "Montserrat-Medium.ttf", 30, track=16, fill=(240, 225, 205))
T("c1", "may your collection shine", "Playfair-Italic.ttf", 72, fill=(250, 240, 225))
T("c2", "with every Chase", "Playfair-Italic.ttf", 84, fill=(250, 240, 225))
T("c3", "& a lucky STH", "Playfair-Italic.ttf", 92)
T("w1", "Light.", "Playfair-Italic.ttf", 130)
T("w2", "Joy.", "Playfair-Italic.ttf", 130)
T("w3", "Prosperity.", "Playfair-Italic.ttf", 130)
T("wish1", "WISHING YOU & YOUR FAMILY", "Montserrat-Light.ttf", 34, track=10, fill=(245, 232, 215))
T("wish2", "a very Happy Diwali", "Playfair-Italic.ttf", 104)
T("end_sh", "शुभ दीपावली", "Tiro-Deva.ttf", 74)
T("end_logo", "GALALAND", "Cinzel-SemiBold.ttf", 128, track=10)
T("end_sub", "WISHES YOU A HAPPY DIWALI", "Montserrat-Light.ttf", 30, track=10, fill=(245, 232, 215))
T("end_tag", "DIECAST  ·  CHASE  ·  STH", "Montserrat-Medium.ttf", 26, track=8, fill=(220, 180, 110))

CRED = json.load(open("diwali_credits.json")); CARC = json.load(open("car_credits.json"))
lines = ["Photos via Wikimedia Commons"]
for v in list(CRED.values()) + [CARC[k] for k in ("0", "5", "15")]:
    lines.append(f"{v['artist'][:26]}  ·  {v['license']}")
lines.append("Hot Wheels is a trademark of Mattel. Not affiliated.")
for k, s in enumerate(lines): T(f"cr{k}", s, "Montserrat-Light.ttf", 27 if k else 32, fill=(200, 190, 180) if k else (240, 220, 180))

# ------------------------------------------------------------------ timeline (beats @ 96 BPM)
b = lambda n: n * B
S1, S2, S3, S4, S5, S6, S7, S8 = 0, b(7), b(13), b(17), b(26), b(30), b(34), 26.0
CARS = [("car00.jpg", "c1"), ("car05.jpg", "c2"), ("car15.jpg", "c3")]
SPARK = [("f19.jpg", 0.4, 0.5), ("f16.jpg", 0.35, 0.45), ("f19.jpg", 0.45, 0.5), ("f16.jpg", 0.3, 0.5)]

def shot(t):
    """Return (plate RGB float array, scene id, local time)."""
    if t < S2:  return kb("f21.jpg", t, S2, 1.0, 1.15, fx=0.5, fy=0.47), 1, t
    if t < S3:  return kb("f27.jpg", t - S2, S3 - S2, 1.08, 1.0, py=0.3), 2, t - S2
    if t < S4:  return kb("f06.jpg", t - S3, S4 - S3, 1.05, 1.18, px=0.6, fx=0.5, fy=0.45), 3, t - S3
    if t < S5:
        lt = t - S4
        return kb("f28.jpg", lt, S5 - S4, 1.0, 1.25, py=-0.4, blur=14), 4, lt
    if t < S6:
        lt = t - S5; n = min(int(lt / B), 3); nm, fx, fy = SPARK[n]
        return kb(nm, lt - n * B, B, 1.05 + 0.05 * n, 1.12 + 0.05 * n, fx=fx, fy=fy, punch=0.08 * math.exp(-(lt - n * B) * 8)), 5, lt
    if t < S7:
        lt = t - S6
        return kb("f23.jpg" if lt < b(2) else "f09.jpg", lt % b(2), b(2), 1.04, 1.14, px=0.5, fx=0.68 if lt < b(2) else 0.55, fy=0.45), 6, lt
    if t < S8:  return kb("f28.jpg", t - S7, S8 - S7, 1.0, 1.12, py=0.3, blur=6) * 0.8, 7, t - S7
    return np.zeros((H, W, 3), np.float32), 8, t - S8

XF = [S2, S3, S6, S7]   # cross-dissolve points
def frame(i):
    t = i / FPS
    x, sc, lt = shot(t)
    for c in XF:   # 0.5s dissolve from previous shot
        if c <= t < c + 0.5:
            px, _, _ = shot(c - 1 / FPS - (t - c) * 0)
            prev, _, _ = shot(c - 0.001)
            u = eio((t - c) / 0.5); x = prev * (1 - u) + x * u
    x = grade(x)
    if sc == 1: x *= eio(t / 1.6)                       # fade up from black
    if sc in (1, 2, 3, 6, 7): x += embers(t, 0.8)
    if sc == 4: x += embers(t, 1.0) * 0.8
    x += light_leak(t, S4 - 0.45, 1.1) + light_leak(t, S5 - 0.3, 0.8, (1, .6, .2), -1) + light_leak(t, S7 - 0.5, 1.2, (1, .4, .25), -1) + light_leak(t, 2.6, 1.6, (1, .5, .15))
    # ---- typography
    if sc == 1:
        reveal(x, "presents1", 540, 1460, t, 1.0, S2 - 0.4, rise=20, glow=0.2, blur_amt=6)
        reveal(x, "presents2", 540, 1530, t, 1.4, S2 - 0.4, rise=20, glow=0.0, blur_amt=4)
        hline(x, 540, 1500, 170 * eo((t - 1.2) / 1.0), env(t, 1.2, S2 - 0.4), 2)
    elif sc == 2:
        reveal(x, "shubh", 540, 1380, lt, 0.35, S3 - S2 - 0.15, rise=50, glow=0.6, blur_amt=14)
    elif sc == 3:
        scrim(x, 1620, 260, 0.78); reveal(x, "happy", 540, 1600, lt, 0.15, S4 - S3 - 0.1, rise=40, glow=0.45)
        reveal(x, "fol", 540, 1715, lt, 0.6, S4 - S3 - 0.1, rise=20, glow=0.0, blur_amt=4)
    elif sc == 4:
        seg = (S5 - S4) / 3; n = min(int(lt / seg), 2); l2 = lt - n * seg
        put_card(x, CARS[n][0], l2, seg, cy=900)
        reveal(x, "this", 540, 400, lt, 0.2, S5 - S4 - 0.2, rise=15, glow=0.0, blur_amt=3)
        hline(x, 540, 440, 130 * eo((lt - 0.4) / 0.8), env(lt, 0.4, S5 - S4 - 0.2), 2)
        reveal(x, CARS[n][1], 540, 1440, l2, 0.25, seg - 0.1, rise=30, glow=0.35 if n == 2 else 0.15)
    elif sc == 5:
        scrim(x, 1480, 330, 0.85)
        for k, key in enumerate(["w1", "w2", "w3"]):
            reveal(x, key, 540, 1300 + k * 170, lt, k * B * 1.0 + 0.05, S6 - S5 - 0.05, rise=30, glow=0.4, blur_amt=8)
        if lt % B < 0.08: x += (1 - (lt % B) / 0.08) * 0.25
    elif sc == 6:
        scrim(x, 1620, 250, 0.8); reveal(x, "wish1", 540, 1560, lt, 0.2, S7 - S6 - 0.1, rise=20, glow=0.0, blur_amt=4)
        reveal(x, "wish2", 540, 1680, lt, 0.6, S7 - S6 - 0.1, rise=40, glow=0.45)
    elif sc == 7:
        scrim(x, 1050, 380, 0.55)
        reveal(x, "end_sh", 540, 830, lt, 0.4, 99, rise=30, glow=0.5)
        reveal(x, "end_logo", 540, 990, lt, 0.9, 99, rise=30, glow=0.55, blur_amt=16)
        hline(x, 540, 1075, 330 * eo((lt - 1.4) / 1.2), clamp((lt - 1.4) / 0.6), 2)
        reveal(x, "end_sub", 540, 1130, lt, 1.7, 99, rise=15, glow=0.0, blur_amt=4)
        reveal(x, "end_tag", 540, 1200, lt, 2.3, 99, rise=10, glow=0.0, blur_amt=3)
        x *= 1 - eio((lt - (S8 - S7 - 0.9)) / 0.9)
    elif sc == 8:
        a = env(lt, 0.1, DUR - S8, 0.4, 0.4)
        for k in range(len(lines)):
            put(x, f"cr{k}", 540, 620 + k * 52 + (30 if k else 0), alpha=a, glow=0)
    x += GRAIN[i % 6] * 0.045
    return (np.clip(x, 0, 1) * 255).astype(np.uint8)

# ------------------------------------------------------------------ soundtrack
SR = 44100; N = int(SR * DUR)
rng = np.random.default_rng(9)
L_ = np.zeros(N); R_ = np.zeros(N); VERB = np.zeros((N, 2))
def mf(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, t0, gain=1.0, pan=0.0, send=0.2):
    s = int(t0 * SR); e = min(N, s + len(sig))
    if s >= N or e <= 0: return
    seg = sig[:e - s] * gain
    l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    L_[s:e] += seg * l; R_[s:e] += seg * r
    VERB[s:e, 0] += seg * send * l; VERB[s:e, 1] += seg * send * r

# pads
CHORDS = [[50, 57, 61, 64, 66], [47, 54, 57, 61, 62], [43, 50, 54, 59, 61], [45, 52, 57, 59, 64]]
BAR = 4 * B
nbars = int(25.5 / BAR) + 1
for k in range(nbars):
    t0 = k * BAR; dur = BAR + 1.6; n = int(dur * SR); x = np.arange(n) / SR
    e = np.minimum(1, x / 0.9) * np.clip((dur - x) / 1.6, 0, 1)
    for side, pan in ((-1, -0.7), (1, 0.7)):
        sig = np.zeros(n)
        for m in CHORDS[k % 4]:
            f0 = mf(m) * (1 + side * 0.0035)
            for h in range(1, 9):
                if f0 * h > 5000: break
                sig += np.sin(2 * np.pi * f0 * h * x + h * side) / h ** 1.6
        add(sig * e, t0, 0.012, pan, 0.6)
    # sub bass
    root = mf(CHORDS[k % 4][0] - 12)
    bs = (np.sin(2 * np.pi * root * x) + 0.3 * np.sin(4 * np.pi * root * x)) * np.minimum(1, x / 0.05) * np.clip((BAR - x) / 0.3, 0, 1)
    if t0 >= S4 - 0.01 and t0 < S7: add(bs, t0, 0.16, 0, 0.0)

# Karplus-Strong sitar
def sitar(f, dur, bright=0.996):
    n = int(dur * SR); P = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, P) * np.hanning(P) ** 0.3
    out = np.zeros(n + P + 1); out[:P] = buf
    i = P
    while i < n + P:
        j = min(i + P, n + P)
        out[i:j] = bright * 0.5 * (out[i - P:j - P] + out[i - P + 1:j - P + 1]) if i - P + 1 + (j - i) <= len(out) else out[i:j]
        i = j
    s = out[P:P + n]
    s = np.tanh(s * 2.2) * 0.6 + s * 0.4                         # jawari buzz
    s += 0.25 * np.sin(2 * np.pi * f * 3.01 * np.arange(n) / SR) * np.exp(-np.arange(n) / SR * 6)
    return s * np.exp(-np.arange(n) / SR * 1.2)
MEL = [(69, 1), (71, .5), (69, .5), (66, 1), (64, 1), (66, .5), (69, .5), (62, 2), (None, 1),
       (74, 1), (71, .5), (69, .5), (71, 1), (69, 1), (66, 1), (64, 1), (66, 2),
       (69, .5), (71, .5), (74, .5), (76, .5), (78, 1), (76, .5), (74, .5), (71, 1), (69, 1), (71, .5), (69, .5), (66, 2),
       (64, .5), (66, .5), (69, 1), (71, .5), (69, .5), (66, .5), (64, .5), (62, 1), (64, 1), (66, 2),
       (74, .5), (76, .5), (78, 1), (81, 1), (78, .5), (76, .5), (74, 1), (71, 1), (69, 2)]
t = S2
for m, d in MEL:
    if t > S7 - 0.1: break
    if m: add(sitar(mf(m), min(3.0, d * B + 1.2)), t, 0.32, 0.25, 0.35)
    t += d * B
for m, d in [(69, 1), (66, 1), (64, 1), (62, 5)]:
    add(sitar(mf(m), d * B + 1.5), t, 0.3, 0.25, 0.45); t += d * B
# tanpura drone (quiet)
for t0 in np.arange(0, 25.5, 2 * B):
    for k, m in enumerate([45, 50, 50, 38]):
        add(sitar(mf(m), 2.6, 0.9985), t0 + k * B / 2, 0.06, -0.3, 0.4)

# drums
def kick():
    x = np.arange(int(0.45 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(48 + 120 * np.exp(-x * 30)) / SR) * np.exp(-x * 7) + rng.normal(0, 1, len(x)) * np.exp(-x * 300) * 0.3
def clap():
    x = np.arange(int(0.5 * SR)) / SR; nz = rng.normal(0, 1, len(x)); nz = nz - np.convolve(nz, np.ones(6) / 6, "same")
    e = sum(np.exp(-np.maximum(0, x - o) * 80) * (x >= o) for o in (0, .012, .024)) * 0.5 + np.exp(-x * 14) * 0.4
    return nz * e
def shaker():
    x = np.arange(int(0.07 * SR)) / SR; nz = np.diff(rng.normal(0, 1, len(x) + 1))
    return nz * np.minimum(1, x / 0.01) * np.exp(-x * 60)
def dayan(f=560):
    x = np.arange(int(0.3 * SR)) / SR
    return sum(np.sin(2 * np.pi * f * m * x) * a for m, a in [(1, 1), (2, .5), (3, .3)]) * np.exp(-x * 14)
for k in range(int((S7 - S4) / B)):
    t0 = S4 + k * B
    if S5 <= t0 < S6 or True:
        add(kick(), t0, 0.75 if k % 2 == 0 else 0.55, 0, 0.05)
    if k % 2 == 1: add(clap(), t0, 0.32, 0.05, 0.35)
    for s in range(4):
        add(shaker(), t0 + s * B / 4, 0.10 * (1.0 if s % 2 else 0.6), 0.4, 0.1)
    if k % 4 == 3: add(dayan(600), t0 + B * 0.5, 0.12, -0.3, 0.3); add(dayan(700), t0 + B * 0.75, 0.10, -0.3, 0.3)
# risers + impacts
def riser(d):
    n = int(d * SR); x = np.arange(n) / SR; nz = rng.normal(0, 1, n)
    hp = nz - np.convolve(nz, np.ones(12) / 12, "same")
    return (hp * 0.6 + np.sin(2 * np.pi * np.cumsum(300 + 1500 * (x / d) ** 2) / SR) * 0.15) * (x / d) ** 2
def impact():
    x = np.arange(int(2.5 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(35 + 60 * np.exp(-x * 6)) / SR) * np.exp(-x * 2.2) + rng.normal(0, 1, len(x)) * np.exp(-x * 9) * 0.25
for tt_, d in [(S4, b(4)), (S5, b(2)), (S7, b(2))]:
    add(riser(d), tt_ - d, 0.22, 0, 0.3); add(impact(), tt_, 0.55, 0, 0.5)
def bell(f):
    x = np.arange(int(4 * SR)) / SR
    return sum(np.sin(2 * np.pi * f * m * x) * a * np.exp(-x * dd) for m, a, dd in [(1, 1, .9), (2.76, .45, 1.6), (5.4, .25, 2.6), (8.9, .12, 4)])
for tt_ in (S2, S7): add(bell(mf(86)), tt_, 0.05, 0.4, 0.7); add(bell(mf(81)), tt_ + 0.02, 0.04, -0.4, 0.7)

# reverb (synthetic stereo IR, FFT convolution)
irn = int(2.8 * SR); xi = np.arange(irn) / SR
for ch in range(2):
    ir = rng.normal(0, 1, irn) * np.exp(-xi * 2.4); ir = np.convolve(ir, np.ones(8) / 8, "same"); ir[:int(0.02 * SR)] = 0
    nfft = 1 << int(np.ceil(np.log2(N + irn)))
    wet = np.fft.irfft(np.fft.rfft(VERB[:, ch], nfft) * np.fft.rfft(ir, nfft), nfft)[:N]
    wet *= 0.9 / (np.abs(wet).max() + 1e-9) * np.abs(VERB[:, ch]).max() * 1.2
    (L_ if ch == 0 else R_)[:] += wet
tt = np.arange(N) / SR
fade = np.clip((DUR - 0.3 - tt) / 2.2, 0, 1) * np.clip(tt / 0.5, 0, 1)
mix = np.stack([L_, R_], 1) * fade[:, None]
mix = np.tanh(mix / np.abs(mix).max() * 1.4) ; mix = mix / np.abs(mix).max() * 0.89
with wave.open("audio.wav", "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((mix * 32767).astype(np.int16).tobytes())

if len(sys.argv) > 1 and sys.argv[1] == "preview":
    secs = [float(s) for s in sys.argv[2].split(",")]
    ims = [Image.fromarray(frame(int(s * FPS))).resize((W // 3, H // 3)) for s in secs]
    sh = Image.new("RGB", (W // 3 * len(ims), H // 3))
    for k, im in enumerate(ims): sh.paste(im, (k * W // 3, 0))
    sh.save("preview.png"); sys.exit()
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                      "-i", "-", "-i", "audio.wav", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                      "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", "Galaland_Diwali_Cinematic.mp4"], stdin=subprocess.PIPE)
for i in range(NF): p.stdin.write(frame(i).tobytes())
p.stdin.close(); p.wait(); print("done")
