import math, random, subprocess, wave, struct
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
DUR = 25.0
NF = int(DUR * FPS)
random.seed(7)
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
GOLD, RED, WHITE, BLACK = (255, 200, 40), (230, 30, 40), (255, 255, 255), (0, 0, 0)

@lru_cache(None)
def F(size):
    return ImageFont.truetype(BOLD, max(4, int(size)))

def ease_out(t): t = min(max(t, 0), 1); return 1 - (1 - t) ** 3
def ease_back(t):
    t = min(max(t, 0), 1); c = 1.9
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
def clamp(t): return min(max(t, 0.0), 1.0)

def text(d, s, xy, size, fill=WHITE, stroke=8, sfill=BLACK, anchor="mm"):
    d.text(xy, s, font=F(size), fill=fill, stroke_width=stroke, stroke_fill=sfill, anchor=anchor)

def vgrad(top, bot):
    t = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(top) * (1 - t) + np.array(bot) * t).astype(np.uint8)
    return Image.fromarray(np.repeat(a, W, axis=1), "RGB")

def radial(inner, outer, cx=W/2, cy=H/2):
    y, x = np.mgrid[0:H, 0:W]
    r = np.clip(np.hypot(x - cx, y - cy) / (H * 0.7), 0, 1)[..., None]
    return Image.fromarray((np.array(inner) * (1 - r) + np.array(outer) * r).astype(np.uint8), "RGB")

BG_LOGO = radial((70, 20, 120), (5, 5, 25))
BG_CHASE = vgrad((20, 10, 50), (255, 110, 60))
BG_STH = radial((120, 60, 0), (10, 0, 20))
BG_LINE = vgrad((0, 40, 90), (0, 160, 200))
BG_END = radial((200, 20, 60), (20, 0, 40))

# rotating sunburst rays
def make_rays(c1, n=24, size=2400):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx = cy = size / 2
    for i in range(n):
        a0 = 2 * math.pi * i / n; a1 = a0 + math.pi / n
        d.polygon([(cx, cy), (cx + size * math.cos(a0), cy + size * math.sin(a0)),
                   (cx + size * math.cos(a1), cy + size * math.sin(a1))], fill=c1)
    return im
RAYS_GOLD = make_rays((255, 210, 60, 55))
RAYS_PINK = make_rays((255, 255, 255, 35))

def paste_rays(img, rays, ang, cx, cy):
    r = rays.rotate(ang, resample=Image.BILINEAR)
    s = r.size[0]
    r = r.crop((int(s/2 - cx), int(s/2 - cy), int(s/2 - cx + W), int(s/2 - cy + H)))
    img.paste(r, (0, 0), r)

# city skyline
CITY = Image.new("RGBA", (W * 2, 500), (0, 0, 0, 0))
cd = ImageDraw.Draw(CITY); x = 0
while x < W * 2:
    bw, bh = random.randint(60, 150), random.randint(150, 480)
    cd.rectangle([x, 500 - bh, x + bw, 500], fill=(25, 15, 45, 255))
    for wy in range(500 - bh + 20, 490, 40):
        for wx in range(x + 12, x + bw - 20, 30):
            if random.random() < 0.45:
                cd.rectangle([wx, wy, wx + 12, wy + 18], fill=(255, 220, 120, 255))
    x += bw + random.randint(0, 20)

def car(d, x, y, s, body, accent=WHITE, t=0.0, police=False, flip=False, flame=True):
    """Side-view diecast-style car; (x, y) = ground point at rear, s = scale."""
    def P(px, py):
        if flip: px = 410 - px
        return (x + px * s, y + py * s)
    d.ellipse([P(-10, -12)[0], y - 14 * s, P(420, 0)[0], y + 10 * s] if not flip else
              [P(420, 0)[0], y - 14 * s, P(-10, -12)[0], y + 10 * s], fill=(0, 0, 0))
    pts = [(0, -45), (8, -92), (120, -104), (175, -152), (285, -152), (345, -104),
           (402, -92), (412, -55), (405, -32), (0, -32)]
    d.polygon([P(*p) for p in pts], fill=body, outline=BLACK, width=max(2, int(5 * s)))
    if flame:
        d.polygon([P(*p) for p in [(20, -75), (200, -82), (150, -70), (230, -66), (160, -58), (20, -58)]], fill=accent)
    for win in ([(185, -142), (232, -142), (232, -106), (140, -106)],
                [(240, -142), (280, -142), (330, -106), (240, -106)]):
        d.polygon([P(*p) for p in win], fill=(150, 220, 255), outline=BLACK, width=max(1, int(3 * s)))
    d.polygon([P(*p) for p in [(395, -88), (410, -84), (410, -70), (395, -72)]], fill=(255, 250, 180))
    d.polygon([P(*p) for p in [(0, -85), (12, -88), (12, -70), (0, -70)]], fill=(255, 40, 40))
    if police:
        on = int(t * 8) % 2
        c1, c2 = ((255, 30, 30), (40, 60, 255)) if on else ((90, 0, 0), (0, 0, 90))
        d.rectangle([*P(195, -170), *P(230, -152)] if not flip else [*P(230, -170), *P(195, -152)], fill=c1, outline=BLACK)
        d.rectangle([*P(232, -170), *P(267, -152)] if not flip else [*P(267, -170), *P(232, -152)], fill=c2, outline=BLACK)
    for wx in (90, 322):
        cx, cy = P(wx, -38); r = 40 * s
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(20, 20, 20))
        r2 = r * 0.6
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=(200, 200, 210), outline=(90, 90, 90), width=max(1, int(3 * s)))
        ang = -t * 25 * (1 if not flip else -1)
        for k in range(5):
            a = ang + k * 2 * math.pi / 5
            d.line([cx, cy, cx + r2 * math.cos(a), cy + r2 * math.sin(a)], fill=(90, 90, 90), width=max(2, int(5 * s)))
        d.ellipse([cx - r * 0.15, cy - r * 0.15, cx + r * 0.15, cy + r * 0.15], fill=GOLD)

def star(d, cx, cy, R, rot, fill, outline=BLACK, width=6):
    pts = []
    for i in range(10):
        a = rot + i * math.pi / 5 - math.pi / 2
        rr = R if i % 2 == 0 else R * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill, outline=outline, width=width)

SPARKS = [(random.uniform(0, W), random.uniform(0, H), random.uniform(0, 6.28), random.uniform(8, 26)) for _ in range(60)]
def sparkles(d, t, color=(255, 240, 160), n=60):
    for (sx, sy, ph, sz) in SPARKS[:n]:
        k = max(0, math.sin(t * 4 + ph))
        r = sz * k
        if r > 1:
            d.polygon([(sx, sy - r), (sx + r * .25, sy - r * .25), (sx + r, sy), (sx + r * .25, sy + r * .25),
                       (sx, sy + r), (sx - r * .25, sy + r * .25), (sx - r, sy), (sx - r * .25, sy - r * .25)], fill=color)

CONF_COLORS = [(255, 60, 60), (255, 210, 40), (60, 200, 255), (120, 255, 120), (255, 120, 220), WHITE]
CONF = [dict(x=random.uniform(0, W), y=random.uniform(-H, 0), vy=random.uniform(250, 600), vx=random.uniform(-80, 80),
             a=random.uniform(0, 6.28), va=random.uniform(-8, 8), c=random.choice(CONF_COLORS), s=random.uniform(12, 26)) for _ in range(220)]
def confetti(d, t):
    for p in CONF:
        y = (p["y"] + p["vy"] * t) % (H + 200) - 100
        x = p["x"] + p["vx"] * t + 40 * math.sin(t * 3 + p["a"])
        a = p["a"] + p["va"] * t; s = p["s"]; w = s * abs(math.cos(a * 1.3)) + 3
        ca, sa = math.cos(a), math.sin(a)
        pts = [(x + dx * ca - dy * sa, y + dx * sa + dy * ca) for dx, dy in [(-w/2, -s/3), (w/2, -s/3), (w/2, s/3), (-w/2, s/3)]]
        d.polygon(pts, fill=p["c"])

# ---------------------------------------------------------------- scenes
def scene_logo(t):
    img = BG_LOGO.copy()
    paste_rays(img, RAYS_PINK, t * 12, W / 2, 760)
    d = ImageDraw.Draw(img)
    sparkles(d, t)
    word = "GALALAND"; size = 150; f = F(size)
    widths = [f.getlength(c) for c in word]; total = sum(widths) + 6 * (len(word) - 1)
    x = (W - total) / 2
    for i, c in enumerate(word):
        k = ease_back((t - 0.2 - i * 0.12) / 0.5)
        if t - 0.2 - i * 0.12 > 0:
            y = 760 - (1 - k) * 700 + 10 * math.sin(t * 5 + i * 0.7) * clamp(t - 2)
            col = GOLD if i % 2 == 0 else (255, 120, 40)
            d.text((x + widths[i] / 2, y), c, font=f, fill=col, stroke_width=10, stroke_fill=(120, 0, 30), anchor="mm")
        x += widths[i] + 6
    a = clamp((t - 1.6) / 0.5)
    if a > 0:
        y = 900 + (1 - ease_out(a)) * 80
        d.rounded_rectangle([200, y - 55, 880, y + 55], 30, fill=(230, 30, 40), outline=WHITE, width=6)
        text(d, "DIECAST WORLD", (540, y), 64, WHITE, 4)
    # checkered strip + car zooming across
    for i in range(0, W, 40):
        for j in range(2):
            d.rectangle([i, 1500 + j * 40, i + 40, 1540 + j * 40], fill=WHITE if (i // 40 + j) % 2 else BLACK)
    cx = -500 + (t - 1.0) * 700
    car(d, cx, 1490, 1.1, (240, 40, 40), GOLD, t)
    text(d, "Diecast  •  Chase  •  STH", (540, 1700), 58, (255, 240, 200), 5)
    return img

def scene_chase(t):
    img = BG_CHASE.copy()
    off = int(t * 260) % W
    img.paste(CITY, (-off, 660), CITY); img.paste(CITY, (W * 2 - off, 660), CITY)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1160, W, 1640], fill=(45, 45, 55))
    d.rectangle([0, 1160, W, 1175], fill=(230, 230, 230)); d.rectangle([0, 1625, W, 1640], fill=(230, 230, 230))
    loff = int(t * 1600) % 240
    for i in range(-1, 7):
        d.rectangle([i * 240 - loff, 1395, i * 240 - loff + 140, 1410], fill=(255, 220, 0))
    rnd = random.Random(int(t * 30))
    for _ in range(14):
        ly = rnd.uniform(1180, 1620); lx = rnd.uniform(0, W)
        d.line([lx, ly, lx + rnd.uniform(100, 300), ly], fill=(200, 200, 220), width=3)
    hx = 520 + 60 * math.sin(t * 1.7); px = 40 + 70 * math.sin(t * 1.3 + 1)
    car(d, px, 1560, 1.05, (250, 250, 250), (20, 20, 20), t, police=True, flame=False)
    car(d, hx, 1430, 1.15, (20, 120, 255), GOLD, t)
    # siren tint
    on = int(t * 8) % 2
    tint = Image.new("RGB", (W, H), (255, 0, 0) if on else (0, 60, 255))
    img = Image.blend(img, tint, 0.10)
    d = ImageDraw.Draw(img)
    shake = 8 * math.sin(t * 40) * clamp(1 - (t % 1.5))
    k = ease_back(t / 0.5)
    text(d, "THE CHASE", (540 + shake, 330), 140 * k, GOLD, 10, (120, 0, 30))
    text(d, "IS ON!", (540 - shake, 490), 160 * k, WHITE, 10, RED)
    a = clamp((t - 2.5) / 0.4)
    if a > 0:
        y = 1800 + (1 - ease_out(a)) * 150
        d.rounded_rectangle([140, y - 60, 940, y + 60], 30, fill=BLACK, outline=GOLD, width=6)
        text(d, "Hunt every CHASE car!", (540, y), 56, GOLD, 3)
    return img

def scene_sth(t):
    img = BG_STH.copy()
    paste_rays(img, RAYS_GOLD, -t * 25, W / 2, 1000)
    d = ImageDraw.Draw(img)
    sparkles(d, t * 1.5, (255, 230, 120))
    k = ease_back(t / 0.6)
    cw, ch = 640 * k, 900 * k; cx, cy = 540, 1020 + 15 * math.sin(t * 2.5)
    if k > 0.05:
        d.rounded_rectangle([cx - cw/2, cy - ch/2, cx + cw/2, cy + ch/2], int(40 * k), fill=(200, 20, 40), outline=GOLD, width=10)
        d.rounded_rectangle([cx - cw/2 + 25*k, cy - ch/2 + 25*k, cx + cw/2 - 25*k, cy - ch/2 + 150*k], int(25*k), fill=(255, 140, 0))
        text(d, "GALALAND", (cx, cy - ch/2 + 88*k), 70 * k, WHITE, int(5 * k) + 1)
        d.rounded_rectangle([cx - cw/2 + 50*k, cy - 170*k, cx + cw/2 - 50*k, cy + 300*k], int(60*k), fill=(230, 245, 255), outline=WHITE, width=6)
        car(d, cx - 240 * k, cy + 140 * k, 1.17 * k, (255, 190, 20), (220, 30, 30), t * 0.3)
        star(d, cx + 220 * k, cy - ch/2 + 260*k, 120 * k, t * 1.5, GOLD, (150, 60, 0), 6)
        text(d, "STH", (cx + 220 * k, cy - ch/2 + 262*k), 54 * k, RED, int(3 * k) + 1, WHITE)
        text(d, "RARE • RUBBER TIRES • GOLD", (cx, cy + 370 * k), 30 * k, GOLD, 2)
    a = clamp((t - 0.6) / 0.4)
    if a > 0:
        s = 1 + 0.05 * math.sin(t * 8)
        text(d, "SUPER", (540, 250), 130 * s * ease_back(a), GOLD, 10, (120, 0, 30))
        text(d, "TREASURE HUNT", (540, 390), 105 * s * ease_back(a), WHITE, 9, RED)
    b = clamp((t - 1.8) / 0.4)
    if b > 0:
        text(d, "Found an STH? That's GOLD!", (540, 1690 + (1 - ease_out(b)) * 100), 54, (255, 240, 200), 5)
    return img

LINE_COLORS = [((255, 40, 40), GOLD), ((40, 200, 90), WHITE), ((255, 140, 0), BLACK),
               ((140, 60, 255), (255, 220, 0)), ((20, 20, 20), RED), ((255, 90, 180), WHITE)]
def scene_lineup(t):
    img = BG_LINE.copy(); d = ImageDraw.Draw(img)
    for row in range(3):
        y = 820 + row * 330
        d.rectangle([0, y + 5, W, y + 30], fill=(20, 30, 50))
        speed = 420 + row * 120; dirn = 1 if row % 2 == 0 else -1
        for j in range(2):
            col, acc = LINE_COLORS[(row * 2 + j) % len(LINE_COLORS)]
            span = W + 700
            if dirn > 0: x = (t * speed + j * span / 2) % span - 500
            else: x = W + 50 - ((t * speed + j * span / 2) % span)
            car(d, x, y, 0.95, col, acc, t * dirn, flip=(dirn < 0))
    k = ease_back(t / 0.5)
    text(d, "COLLECT", (540, 250), 140 * k, GOLD, 10, (120, 0, 30))
    text(d, "THEM ALL!", (540, 410), 140 * k, WHITE, 10, (0, 60, 140))
    tags = ["DIECAST", "CHASE", "STH"]
    for i, tg in enumerate(tags):
        a = clamp((t - 0.6 - i * 0.35) / 0.3)
        if a > 0:
            x = 200 + i * 340; sc = ease_back(a)
            d.rounded_rectangle([x - 150 * sc, 1750 - 55 * sc, x + 150 * sc, 1750 + 55 * sc], int(30 * sc) + 1,
                                fill=[RED, BLACK, GOLD][i], outline=WHITE, width=5)
            text(d, tg, (x, 1750), 54 * sc, [WHITE, GOLD, RED][i], 3, BLACK if i < 2 else WHITE)
    return img

def scene_end(t):
    img = BG_END.copy()
    paste_rays(img, RAYS_GOLD, t * 15, W / 2, 900)
    d = ImageDraw.Draw(img)
    confetti(d, t)
    k1 = ease_back(t / 0.5)
    text(d, "WISHING", (540, 380), 120 * k1, WHITE, 9, (120, 0, 30))
    k2 = ease_back((t - 0.3) / 0.6)
    if k2 > 0:
        s = 1 + 0.04 * math.sin(t * 6)
        text(d, "GALALAND", (540, 600), 165 * k2 * s, GOLD, 12, (120, 0, 30))
    k3 = ease_back((t - 0.7) / 0.5)
    if k3 > 0:
        text(d, "HUGE SUCCESS!", (540, 800), 110 * k3, WHITE, 9, RED)
    star(d, 540, 1150, 190 * ease_back((t - 1.0) / 0.6), t * 0.8, GOLD, (150, 60, 0), 8)
    if t > 1.0:
        text(d, "#1", (540, 1160), 110 * ease_back((t - 1.0) / 0.6), RED, 5, WHITE)
    a = clamp((t - 1.8) / 0.5)
    if a > 0:
        y = 1500 + (1 - ease_out(a)) * 120
        text(d, "Keep Collecting.", (540, y), 70, (255, 240, 200), 6)
        text(d, "Keep Chasing. Keep Winning!", (540, y + 100), 56, GOLD, 6)
    cx = -450 + (t - 2.2) * 600
    car(d, cx, 1850, 0.9, (255, 200, 30), RED, t)
    return img

SCENES = [(0, 4, scene_logo), (4, 10, scene_chase), (10, 15, scene_sth), (15, 19.5, scene_lineup), (19.5, 25, scene_end)]
CUTS = [s[0] for s in SCENES[1:]]

def frame(i):
    t = i / FPS
    for a, b, fn in SCENES:
        if a <= t < b:
            img = fn(t - a); break
    # flash at cuts
    for c in CUTS:
        dt = t - c
        if 0 <= dt < 0.25:
            img = Image.blend(img, Image.new("RGB", (W, H), WHITE), 1 - dt / 0.25)
    if t > DUR - 0.5:
        img = Image.blend(img, Image.new("RGB", (W, H), BLACK), (t - (DUR - 0.5)) / 0.5)
    return img

# ---------------------------------------------------------------- audio
SR = 44100; BPM = 128; beat = 60 / BPM
N = int(SR * DUR); audio = np.zeros(N)
tt = np.arange(N) / SR
def add(sig, start):
    s = int(start * SR); e = min(N, s + len(sig))
    if s < N: audio[s:e] += sig[:e - s]
kl = np.arange(int(0.25 * SR)) / SR
kick = np.sin(2 * np.pi * (45 * kl + 90 / 18 * (1 - np.exp(-18 * kl)) * 1)) * np.exp(-kl * 12) * 0.9
kick = np.sin(2 * np.pi * np.cumsum(45 + 110 * np.exp(-kl * 25)) / SR) * np.exp(-kl * 10) * 0.9
hl = np.arange(int(0.06 * SR)); rng = np.random.default_rng(1)
hat = np.diff(rng.standard_normal(len(hl) + 1)) * np.exp(-hl / SR * 70) * 0.12
cl = np.arange(int(0.18 * SR))
clap = np.diff(rng.standard_normal(len(cl) + 1)) * np.exp(-cl / SR * 22) * 0.25
roots = [55.0, 43.65, 65.41, 49.0]  # A F C G
nb = int(DUR / beat)
for b in range(nb):
    st = b * beat
    if st < 0.5: continue
    add(kick, st)
    add(hat, st + beat / 2)
    if b % 2 == 1: add(clap, st)
    root = roots[(b // 4) % 4]
    for half in range(2):
        L = int(beat / 2 * SR); x = np.arange(L) / SR
        f = root * (2 if half else 1)
        bass = np.sign(np.sin(2 * np.pi * f * x)) * 0.10 * np.exp(-x * 5)
        add(bass, st + half * beat / 2)
    # arpeggio lead on scenes after intro
    if st > 10:
        for q in range(4):
            L = int(beat / 4 * SR); x = np.arange(L) / SR
            f = root * 4 * [1, 1.5, 2, 1.5][q] * (1.26 if q == 1 else 1)
            add(np.sin(2 * np.pi * f * x) * np.exp(-x * 14) * 0.08, st + q * beat / 4)
# siren during chase
m = (tt >= 4) & (tt < 10)
sf = 750 + 200 * np.sin(2 * np.pi * 1.6 * tt)
siren = np.sin(2 * np.pi * np.cumsum(sf) / SR) * 0.06
audio[m] += siren[m]
# engine rumble during chase
eng = np.sin(2 * np.pi * np.cumsum(70 + 15 * np.sin(2 * np.pi * 0.7 * tt)) / SR) * 0.08
audio[m] += eng[m]
# whooshes at cuts
for c in [0.0] + CUTS:
    L = int(0.6 * SR); x = np.arange(L) / SR
    nz = np.convolve(rng.standard_normal(L), np.ones(8) / 8, "same")
    add(nz * np.sin(np.pi * x / 0.6) ** 2 * 0.35, max(0, c - 0.4))
# sparkle chimes in STH + finale
for st in [10.2, 10.6, 19.6, 20.0, 20.4]:
    for f in [1318.5, 1760, 2637]:
        L = int(1.0 * SR); x = np.arange(L) / SR
        add(np.sin(2 * np.pi * f * x) * np.exp(-x * 5) * 0.05, st)
# fade
audio *= np.clip((DUR - tt) / 1.0, 0, 1)
audio = audio / np.max(np.abs(audio)) * 0.85
with wave.open("audio.wav", "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((audio * 32767).astype(np.int16).tobytes())

# ---------------------------------------------------------------- render
import sys
if len(sys.argv) > 1 and sys.argv[1] == "preview":
    for sec in [2.5, 7, 13, 17.5, 23]:
        frame(int(sec * FPS)).resize((W // 2, H // 2)).save(f"preview_{sec}.png")
    sys.exit()
p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                      "-r", str(FPS), "-i", "-", "-i", "audio.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                      "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                      "Galaland_Success.mp4"], stdin=subprocess.PIPE)
for i in range(NF):
    p.stdin.write(frame(i).tobytes())
p.stdin.close(); p.wait()
print("done")
