"""Galaland - Happy Diwali (bright & festive edit).

Swap in your own photos: replace the files in photos/ (car*.jpg = cars, d*.jpg = Diwali shots)
keeping the same names, then run:  python3 festive.py
"""
import math, random, subprocess, wave, sys, json
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

W, H, FPS = 1080, 1920, 30
BPM = 112; B = 60 / BPM; BAR = 4 * B
DUR = 23.4
NF = int(DUR * FPS)
rnd = random.Random(21)
PINK, SAFFRON, YELLOW, PURPLE, TEAL, WHITE, INK = (255, 46, 136), (255, 138, 0), (255, 212, 0), (123, 44, 255), (0, 194, 168), (255, 255, 255), (25, 10, 40)

def clamp(t): return min(max(t, 0.0), 1.0)
def eo(t): t = clamp(t); return 1 - (1 - t) ** 3
def eback(t):
    t = clamp(t); c = 2.2
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
@lru_cache(None)
def F(name, size): return ImageFont.truetype("fonts/" + name, int(size))

# ------------------------------------------------------------------ plates
PL = {}
def plate(name, blur=0, sat=1.35, bright=1.06):
    k = (name, blur)
    if k in PL: return PL[k]
    im = ImageOps.exif_transpose(Image.open("photos/" + name)).convert("RGB")
    im = ImageOps.fit(im, (int(W * 1.2), int(H * 1.2)), Image.LANCZOS, centering=(0.5, 0.5))
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    im = ImageEnhance.Color(im).enhance(sat); im = ImageEnhance.Brightness(im).enhance(bright); im = ImageEnhance.Contrast(im).enhance(1.08)
    PL[k] = im
    return im
def kb(name, lt, dur, z0=1.0, z1=1.1, punch=0.0, blur=0, rot=0.0, shift=0.0):
    im = plate(name, blur)
    z = z0 + (z1 - z0) * clamp(lt / dur) + punch
    pw, ph = im.size; cw, ch = pw / 1.2 / z, ph / 1.2 / z
    cx, cy = pw / 2 + shift, ph / 2
    out = im.resize((W, H), Image.BICUBIC, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))
    if rot: out = out.rotate(rot, resample=Image.BICUBIC, expand=False, fillcolor=PINK)
    return out
def punch(lt): return 0.14 * math.exp(-lt * 9)

# ------------------------------------------------------------------ sticker typography
STK = {}
def sticker(text, font, size, fill=WHITE, outline=INK, ow=10, shadow=PINK, sh=(10, 12), box=None, pad=(36, 16), track=0):
    key = (text, font, size, fill, outline, ow, shadow, sh, box, pad, track)
    if key in STK: return STK[key]
    f = F(font, size)
    if track:
        widths = [f.getlength(c) + track for c in text]; tw = sum(widths) - track
    else: tw = f.getlength(text)
    asc, desc = f.getmetrics(); th = asc + desc
    m = 30
    w, h = int(tw + 2 * pad[0] + 2 * m + ow * 2 + abs(sh[0])), int(th + 2 * pad[1] + 2 * m + ow * 2 + abs(sh[1]))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0, y0 = m + ow, m + ow
    def draw_txt(dx, dy, col, stroke=0, scol=None):
        if track:
            x = x0 + pad[0] + dx
            for c, cw in zip(text, widths):
                d.text((x, y0 + pad[1] + dy), c, font=f, fill=col, stroke_width=stroke, stroke_fill=scol); x += cw
        else:
            d.text((x0 + pad[0] + dx, y0 + pad[1] + dy), text, font=f, fill=col, stroke_width=stroke, stroke_fill=scol)
    if box:
        bx = [x0, y0, x0 + tw + 2 * pad[0], y0 + th + 2 * pad[1]]
        if shadow: d.rounded_rectangle([bx[0] + sh[0], bx[1] + sh[1], bx[2] + sh[0], bx[3] + sh[1]], 18, fill=shadow)
        d.rounded_rectangle(bx, 18, fill=box)
        draw_txt(0, 0, fill)
    else:
        if shadow: draw_txt(sh[0], sh[1], shadow, ow, shadow)
        draw_txt(0, 0, fill, ow, outline)
    STK[key] = im
    return im
def slam(img, st, cx, cy, lt, rot=0.0, t_out=99.0, delay=0.0):
    lt = lt - delay
    if lt < 0 or lt > t_out: return
    s = 1.0 + 0.9 * (1 - eback(lt / 0.32))
    s *= 1 + 0.025 * math.sin(lt * 2 * math.pi / B)            # pulse on the beat
    out = clamp((t_out - lt) / 0.15)
    s *= 1 - 0.3 * (1 - out)
    a = clamp(lt / 0.08) * out
    im = st.resize((max(1, int(st.width * s)), max(1, int(st.height * s))), Image.BICUBIC)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if a < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    img.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)

# ------------------------------------------------------------------ particles: sparkles, confetti, fireworks
SPK = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0, 6.28), rnd.uniform(10, 28), rnd.choice([WHITE, YELLOW, (255, 220, 240)])) for _ in range(55)]
def sparkles(d, t, n=55):
    for (x, y, ph, sz, c) in SPK[:n]:
        r = sz * max(0, math.sin(t * 5 + ph)) ** 2
        if r > 1.5:
            d.polygon([(x, y - r), (x + r * .18, y - r * .18), (x + r, y), (x + r * .18, y + r * .18), (x, y + r), (x - r * .18, y + r * .18), (x - r, y), (x - r * .18, y - r * .18)], fill=c)
CONF = [dict(x=rnd.uniform(0, W), y=rnd.uniform(-H, 0), vy=rnd.uniform(300, 650), vx=rnd.uniform(-60, 60), a=rnd.uniform(0, 6.3), va=rnd.uniform(-9, 9),
             c=rnd.choice([PINK, SAFFRON, YELLOW, PURPLE, TEAL, WHITE]), s=rnd.uniform(14, 28)) for _ in range(200)]
def confetti(d, t):
    for p in CONF:
        y = p["y"] + p["vy"] * t
        if y > H + 40 or y < -40: continue
        x = p["x"] + p["vx"] * t + 30 * math.sin(t * 3 + p["a"]); a = p["a"] + p["va"] * t; s = p["s"]; w = s * abs(math.cos(a * 1.3)) + 3
        ca, sa = math.cos(a), math.sin(a)
        d.polygon([(x + dx * ca - dy * sa, y + dx * sa + dy * ca) for dx, dy in [(-w / 2, -s / 3), (w / 2, -s / 3), (w / 2, s / 3), (-w / 2, s / 3)]], fill=p["c"])
FW_COL = [[(255, 80, 170), (255, 200, 230)], [(255, 210, 40), (255, 250, 200)], [(80, 230, 255), (220, 250, 255)], [(170, 90, 255), (230, 200, 255)], [(255, 140, 30), (255, 230, 160)]]
BURSTS = []
for t0 in list(np.arange(0.2, 6.4, 0.55)) + list(np.arange(15.0, 21.4, 0.32)):
    BURSTS.append(dict(t0=t0 + rnd.uniform(-.1, .1), x=rnd.uniform(120, W - 120), y=rnd.uniform(200, 1000), pal=rnd.choice(FW_COL), n=rnd.randint(60, 90),
                       sp=rnd.uniform(380, 600), seed=rnd.randint(0, 9999)))
def fireworks(t):
    g = Image.new("RGB", (W // 2, H // 2)); d = ImageDraw.Draw(g)
    for b in BURSTS:
        a = t - b["t0"]
        if not 0 <= a < 1.6: continue
        rr = random.Random(b["seed"]); fade = (1 - a / 1.6) ** 1.3
        for k in range(b["n"]):
            ang = 2 * math.pi * k / b["n"] + rr.uniform(-.06, .06); v = b["sp"] * rr.uniform(.7, 1.1); ph = rr.random()
            def pos(aa):
                dist = v * (1 - math.exp(-2.4 * aa)) / 2.4
                return (b["x"] + dist * math.cos(ang)) / 2, (b["y"] + dist * math.sin(ang) + 70 * aa * aa) / 2
            (x1, y1), (x2, y2) = pos(max(0, a - .09)), pos(a)
            col = b["pal"][0 if ph < .6 else 1]; tw = 1 if a < .8 else (0.3 + 0.7 * (math.sin(t * 50 + ph * 30) > 0))
            d.line([x1, y1, x2, y2], fill=tuple(int(c * fade * tw) for c in col), width=3)
        if a < .1:
            r = 40 * (1 - a / .1); d.ellipse([b["x"] / 2 - r, b["y"] / 2 - r, b["x"] / 2 + r, b["y"] / 2 + r], fill=(255, 255, 235))
    halo = g.filter(ImageFilter.GaussianBlur(5))
    arr = np.asarray(g, np.float32) + np.asarray(halo, np.float32) * 1.6
    return np.asarray(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)
def screen_add(img, layer):
    a = np.asarray(img, np.float32); out = 255 - (255 - a) * (255 - layer) / 255
    return Image.fromarray(out.astype(np.uint8))

# colourful light leak
yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
def leak(t, t0, dur, col):
    u = (t - t0) / dur
    if not 0 <= u <= 1: return None
    cx, cy = (W / 4) * (1.3 * u - 0.15), (H / 4) * (0.2 + 0.5 * u)
    m = np.exp(-(((xx - cx) / (W / 4 * .5)) ** 2 + ((yy - cy) / (H / 4 * .4)) ** 2)) * math.sin(math.pi * u)
    lay = (m[..., None] * np.array(col, np.float32))
    return np.asarray(Image.fromarray(lay.astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)

# ------------------------------------------------------------------ car card
CARD = {}
def car_card(name, border):
    k = (name, border)
    if k in CARD: return CARD[k]
    im = ImageOps.exif_transpose(Image.open("photos/" + name)).convert("RGB")
    im = ImageOps.fit(im, (900, 900) if "15" in name else (900, 680), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(1.25); im = ImageEnhance.Contrast(im).enhance(1.06)
    bw = 16; sh = 22
    out = Image.new("RGBA", (im.width + 2 * bw + sh + 40, im.height + 2 * bw + sh + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(out)
    d.rounded_rectangle([20 + sh, 20 + sh, 20 + sh + im.width + 2 * bw, 20 + sh + im.height + 2 * bw], 34, fill=border)
    d.rounded_rectangle([20, 20, 20 + im.width + 2 * bw, 20 + im.height + 2 * bw], 34, fill=WHITE)
    mask = Image.new("L", im.size); ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], 22, fill=255)
    out.paste(im, (20 + bw, 20 + bw), mask)
    CARD[k] = out
    return out

# ------------------------------------------------------------------ timeline
S_INTRO, S_BRAND, S_CARS, S_FIN, S_CRED = 0, 8 * B, 12 * B, 28 * B, 40 * B
INTRO_SHOTS = ["d31.jpg", "d15.jpg", "d14.jpg", "d09.jpg"]
CARS = [("car00.jpg", "THIS DIWALI", YELLOW, INK, PINK), ("car09.jpg", "SHINE BRIGHT", PINK, WHITE, YELLOW),
        ("car05.jpg", "CHASE CARS", YELLOW, INK, PURPLE), ("car01.jpg", "RARE FINDS", TEAL, WHITE, YELLOW),
        ("car15.jpg", "SUPER TREASURE HUNTS", PINK, WHITE, YELLOW), ("car04.jpg", "NEW ARRIVALS", YELLOW, INK, PINK),
        ("car17.jpg", "CLASSICS", PURPLE, WHITE, YELLOW), ("car07.jpg", "AT GALALAND", SAFFRON, WHITE, PURPLE)]

def gradient_bg(t):
    k = (t * 0.25) % 1
    a = np.array(PINK, np.float32) * (1 - k) + np.array(PURPLE, np.float32) * k
    b = np.array(SAFFRON, np.float32)
    g = np.linspace(0, 1, H)[:, None, None]
    return Image.fromarray(np.repeat((a * (1 - g) + b * g).astype(np.uint8), W, axis=1))

def frame(i):
    t = i / FPS
    fw = None
    if t < S_BRAND:                                   # ---------- intro
        n = min(int(t / (2 * B)), 3); lt = t - n * 2 * B
        img = kb(INTRO_SHOTS[n], lt, 2 * B, 1.02, 1.1, punch(lt))
        fw = fireworks(t)
        img = screen_add(img, fw)
        d = ImageDraw.Draw(img); sparkles(d, t)
        slam(img, sticker("HAPPY", "YatraOne.ttf", 230, YELLOW, INK, 12, PINK, (12, 14)), 540, 800, t - 2 * B, -4)
        slam(img, sticker("DIWALI", "YatraOne.ttf", 225, WHITE, INK, 12, PINK, (12, 14)), 540, 1060, t - 3 * B, 3)
        slam(img, sticker("FESTIVAL OF LIGHTS", "Montserrat-Black.ttf", 44, INK, None, 0, PINK, (8, 8), box=YELLOW, track=4), 540, 1290, t - 5 * B, -2)
    elif t < S_CARS:                                  # ---------- brand
        lt = t - S_BRAND
        img = kb("d13.jpg", lt, 4 * B, 1.0, 1.15, punch(lt), rot=lt * 3)
        img = screen_add(img, fireworks(t) * 0.8)
        d = ImageDraw.Draw(img); sparkles(d, t)
        slam(img, sticker("WISHES FROM", "Montserrat-Black.ttf", 56, WHITE, None, 0, INK, (8, 8), box=PINK, track=6), 540, 760, lt, -3)
        slam(img, sticker("GALALAND", "Montserrat-Black.ttf", 150, YELLOW, INK, 12, PINK, (12, 14)), 540, 960, lt - B, 0)
        slam(img, sticker("DIECAST • CHASE • STH", "Montserrat-ExtraBold.ttf", 44, INK, None, 0, PINK, (8, 8), box=WHITE, track=3), 540, 1150, lt - 2 * B, 2)
    elif t < S_FIN:                                   # ---------- cars, one per 2 beats
        lt0 = t - S_CARS; n = min(int(lt0 / (2 * B)), 7); lt = lt0 - n * 2 * B
        nm, cap, boxc, txtc, border = CARS[n]
        img = kb(nm, lt, 2 * B, 1.0, 1.08, 0, blur=30)
        tint = Image.new("RGB", (W, H), [PINK, PURPLE, SAFFRON, TEAL][n % 4])
        img = Image.blend(img, tint, 0.35)
        d = ImageDraw.Draw(img)
        # rays
        cx, cy = 540, 980
        for k in range(16):
            a0 = lt * 0.6 + k * math.pi / 8; a1 = a0 + math.pi / 16
            d.polygon([(cx, cy), (cx + 2000 * math.cos(a0), cy + 2000 * math.sin(a0)), (cx + 2000 * math.cos(a1), cy + 2000 * math.sin(a1))], fill=tuple(min(255, int(c * 1.0 + 30)) for c in tint.getpixel((0, 0))))
        img = Image.blend(kb(nm, lt, 2 * B, 1.0, 1.08, 0, blur=30), img, 0.75)
        d = ImageDraw.Draw(img); sparkles(d, t, 35)
        cd = car_card(nm, border)
        s = (0.7 + 0.3 * eback(lt / 0.3)) * (1 + 0.04 * lt)
        rot = (-3 if n % 2 else 3) * (1 - 0.4 * eo(lt))
        c2 = cd.resize((int(cd.width * s), int(cd.height * s)), Image.BICUBIC).rotate(rot, resample=Image.BICUBIC, expand=True)
        img.paste(c2, (int(540 - c2.width / 2), int(980 - c2.height / 2)), c2)
        slam(img, sticker("HAPPY DIWALI", "YatraOne.ttf", 92, WHITE, INK, 8, PINK, (8, 10)), 540, 330, lt0, 0)
        size = 62 if len(cap) < 14 else 50
        slam(img, sticker(cap, "Montserrat-Black.ttf", size, txtc, None, 0, INK, (10, 10), box=boxc, track=3), 540, 1530, lt - 0.1, -3 if n % 2 == 0 else 3)
        if lt < 0.07: img = Image.blend(img, Image.new("RGB", (W, H), WHITE), 0.7 * (1 - lt / 0.07))
    elif t < S_CRED:                                  # ---------- finale
        lt = t - S_FIN
        nm = "d02.jpg" if lt < 4 * B else ("d26.jpg" if lt < 8 * B else "d22.jpg")
        l2 = lt % (4 * B)
        img = kb(nm, l2, 4 * B, 1.02, 1.12, punch(l2))
        img = screen_add(img, fireworks(t))
        d = ImageDraw.Draw(img); confetti(d, lt); sparkles(d, t)
        slam(img, sticker("HAPPY", "YatraOne.ttf", 220, YELLOW, INK, 13, PINK, (13, 15)), 540, 560, lt, -4)
        slam(img, sticker("DIWALI", "YatraOne.ttf", 235, WHITE, INK, 13, PINK, (13, 15)), 540, 830, lt - 0.5 * B, 3)
        lines = [("Wishing you light, joy", WHITE, PINK), ("& lots of lucky STH!", INK, YELLOW)]
        for k, (s_, tc, bc) in enumerate(lines):
            slam(img, sticker(s_, "Montserrat-ExtraBold.ttf", 52, tc, None, 0, INK, (8, 8), box=bc), 540, 1110 + k * 120, lt - (2 + k) * B, -2 + 4 * k)
        slam(img, sticker("— TEAM GALALAND —", "Montserrat-Black.ttf", 64, YELLOW, INK, 8, PINK, (8, 10), track=4), 540, 1440, lt - 5 * B, 0)
    else:                                             # ---------- credits
        lt = t - S_CRED
        img = gradient_bg(t); d = ImageDraw.Draw(img)
        CR = json.load(open("credits.json"))
        d.text((540, 380), "HAPPY DIWALI!", font=F("YatraOne.ttf", 110), fill=YELLOW, anchor="mm", stroke_width=8, stroke_fill=INK)
        d.text((540, 520), "Photos: Wikimedia Commons", font=F("Montserrat-Bold.ttf", 34), fill=WHITE, anchor="mm")
        y = 590
        for v in CR.values():
            d.text((540, y), f"{v['artist'][:26]} · {v['license']}", font=F("Montserrat-Bold.ttf", 27), fill=(255, 235, 245), anchor="mm"); y += 46
        d.text((540, y + 40), "Hot Wheels is a trademark of Mattel. Not affiliated.", font=F("Montserrat-Bold.ttf", 25), fill=(255, 220, 235), anchor="mm")
    # colour leaks on section changes
    for t0, col in [(S_BRAND - .25, (255, 60, 160)), (S_CARS - .3, (255, 200, 40)), (S_FIN - .3, (255, 90, 200)), (S_CRED - .3, (255, 170, 40))]:
        lk = leak(t, t0, 0.7, col)
        if lk is not None: img = screen_add(img, lk)
    if t < 0.25: img = Image.blend(Image.new("RGB", (W, H), WHITE), img, t / 0.25)
    if t > DUR - 0.3: img = Image.blend(img, Image.new("RGB", (W, H), INK), (t - (DUR - 0.3)) / 0.3)
    return img

# ------------------------------------------------------------------ music: bhangra-style dhol + tumbi + brass
SR = 44100; N = int(SR * DUR); rng = np.random.default_rng(4)
L_ = np.zeros(N); R_ = np.zeros(N); SEND = np.zeros(N)
def mf(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, t0, g=1.0, pan=0.0, send=0.1):
    s = int(t0 * SR); e = min(N, s + len(sig))
    if s >= N or e <= s or s < 0: return
    x = sig[:e - s] * g
    L_[s:e] += x * math.cos((pan + 1) * math.pi / 4); R_[s:e] += x * math.sin((pan + 1) * math.pi / 4); SEND[s:e] += x * send
def dagga(v=1.0):
    x = np.arange(int(.42 * SR)) / SR
    body = np.sin(2 * np.pi * np.cumsum(62 + 95 * np.exp(-x * 22)) / SR) * np.exp(-x * 7.5)
    slap = rng.normal(0, 1, len(x)) * np.exp(-x * 140) * 0.35
    return (body + slap) * v
def tilli(v=1.0):
    x = np.arange(int(.14 * SR)) / SR
    nz = np.diff(np.diff(rng.normal(0, 1, len(x) + 2))) * np.exp(-x * 60) * 0.25
    ring = (np.sin(2 * np.pi * 410 * x) + .5 * np.sin(2 * np.pi * 980 * x)) * np.exp(-x * 30) * 0.5
    return (nz + ring) * v
def kick():
    x = np.arange(int(.4 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(45 + 140 * np.exp(-x * 35)) / SR) * np.exp(-x * 6)
def clap():
    x = np.arange(int(.35 * SR)) / SR; nz = rng.normal(0, 1, len(x)); nz -= np.convolve(nz, np.ones(5) / 5, "same")
    return nz * (sum((x >= o) * np.exp(-np.maximum(0, x - o) * 90) for o in (0, .01, .021)) * .5 + np.exp(-x * 18) * .45)
def pluck(f, d, bright=0.993):
    n = int(d * SR); P = max(2, int(SR / f)); out = np.zeros(n + P + 1); out[:P] = rng.uniform(-1, 1, P)
    i = P
    while i < n + P:
        j = min(i + P, n + P); out[i:j] = bright * 0.5 * (out[i - P:j - P] + out[i - P + 1:j - P + 1]); i = j
    s = out[P:P + n]; return np.tanh(s * 1.8) * np.exp(-np.arange(n) / SR * 4)
def brass(fs, d):
    n = int(d * SR); x = np.arange(n) / SR; s = np.zeros(n)
    for f in fs:
        for det in (-0.004, 0, 0.004):
            for h in range(1, 10): s += np.sin(2 * np.pi * f * (1 + det) * h * x) / h * (0.9 ** h)
    e = np.minimum(1, x / 0.02) * np.exp(-x * 3.5)
    return s * e
CH = [(50, [62, 66, 69]), (50, [62, 66, 69]), (43, [59, 62, 67]), (45, [61, 64, 69])]   # D D G A
STEP = B / 4
DAGGA = {0: 1, 3: .6, 6: .9, 8: 1, 11: .6, 14: .9}
TILLI = {2: .8, 4: 1, 7: .6, 10: .8, 12: 1, 15: .7, 13: .4}
RIFF = [74, 74, 69, 74, 72, 74, 69, 67, 69, 69, 66, 69, 67, 64, 62, None]
nb = int((S_CRED + 0.2) / BAR) + 1
for bar in range(nb):
    t0 = bar * BAR; root, chord = CH[bar % 4]
    full = t0 >= S_BRAND - 0.01
    for st in range(16):
        ts = t0 + st * STEP + (0.018 if st % 2 else 0)          # light swing
        if ts >= S_CRED: break
        if st in DAGGA and (full or st in (0, 8)): add(dagga(DAGGA[st]), ts, .55, -.1, .05)
        if st in TILLI and full: add(tilli(TILLI[st]), ts, .35, .25, .12)
        if t0 >= S_CARS and st in (0, 8): add(kick(), ts, .6, 0, 0)
        if full and st in (4, 12): add(clap(), ts, .28, 0, .3)
        if t0 >= S_CARS and RIFF[st]: add(pluck(mf(RIFF[st]), .35), ts, .22, .35, .2)
        if t0 >= S_BRAND and st % 2 == 0:                           # bass bounce on 8ths
            f = mf(root - 12 + (12 if st % 4 == 2 else 0)); x = np.arange(int(STEP * 2 * SR)) / SR
            add((np.sin(2 * np.pi * f * x) + .4 * np.sign(np.sin(2 * np.pi * f * x)) * .3) * np.exp(-x * 5), ts, .13, 0, 0)
    if t0 < S_CRED: add(brass([mf(m) for m in chord], BAR * .9), t0, .02, -.2, .25)
    if S_FIN <= t0 < S_CRED:
        for k, m in enumerate([78, 76, 74, 76, 78, 81, 78, 76]): add(pluck(mf(m), .4, .996), t0 + k * B / 2, .16, -.35, .3)
# risers, impacts, firework booms
def riser(d):
    n = int(d * SR); x = np.arange(n) / SR; nz = rng.normal(0, 1, n); nz -= np.convolve(nz, np.ones(10) / 10, "same")
    return (nz * .5 + np.sin(2 * np.pi * np.cumsum(400 + 1800 * (x / d) ** 2) / SR) * .2) * (x / d) ** 2
def impact():
    x = np.arange(int(1.8 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(40 + 80 * np.exp(-x * 7)) / SR) * np.exp(-x * 3) + rng.normal(0, 1, len(x)) * np.exp(-x * 10) * .3
for t_, d in [(S_BRAND, 2 * B), (S_CARS, 4 * B), (S_FIN, 4 * B)]:
    add(riser(d), t_ - d, .25, 0, .2); add(impact(), t_, .5, 0, .4)
for b in BURSTS:
    x = np.arange(int(1.2 * SR)) / SR
    boom = np.convolve(rng.normal(0, 1, len(x)), np.ones(30) / 30, "same") * np.exp(-x * 7)
    cr = np.zeros(len(x))
    for _ in range(25):
        p = int(rng.uniform(.3, 1.1) * SR); cr[p:p + 250] += rng.normal(0, 1, 250) * np.exp(-np.arange(250) / 35)
    add(boom * 1.2 + cr * .25, b["t0"], .22, rnd.uniform(-.6, .6), .3)
# reverb + master
irn = int(1.6 * SR); xi = np.arange(irn) / SR; ir = rng.normal(0, 1, irn) * np.exp(-xi * 4); ir[:600] = 0
nfft = 1 << int(np.ceil(np.log2(N + irn))); wet = np.fft.irfft(np.fft.rfft(SEND, nfft) * np.fft.rfft(ir, nfft), nfft)[:N]
wet *= np.abs(SEND).max() / (np.abs(wet).max() + 1e-9) * .8
L_ += wet; R_ += np.roll(wet, 300)
tt = np.arange(N) / SR
mix = np.stack([L_, R_], 1) * (np.clip((DUR - .2 - tt) / 1.6, 0, 1))[:, None]
mix = np.tanh(mix / np.abs(mix).max() * 1.6); mix = mix / np.abs(mix).max() * .89
with wave.open("audio.wav", "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((mix * 32767).astype(np.int16).tobytes())

if len(sys.argv) > 1 and sys.argv[1] == "preview":
    secs = [float(s) for s in sys.argv[2].split(",")]
    ims = [frame(int(s * FPS)).resize((W // 3, H // 3)) for s in secs]
    sh = Image.new("RGB", (W // 3 * len(ims), H // 3))
    for k, im in enumerate(ims): sh.paste(im, (k * W // 3, 0))
    sh.save("preview.png"); sys.exit()
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "audio.wav",
                      "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart",
                      "Galaland_Happy_Diwali_Festive.mp4"], stdin=subprocess.PIPE)
for i in range(NF): p.stdin.write(frame(i).tobytes())
p.stdin.close(); p.wait(); print("done")
