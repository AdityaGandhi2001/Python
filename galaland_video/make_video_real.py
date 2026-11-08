"""Galaland promo video built from real Hot Wheels photos (Wikimedia Commons, see CREDITS.md)."""
import math, random, subprocess, wave, sys, json
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

W, H, FPS = 1080, 1920, 30
DUR = 30.0
NF = int(DUR * FPS)
random.seed(7)
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
GOLD, RED, WHITE, BLACK, ORANGE = (255, 200, 40), (230, 30, 40), (255, 255, 255), (0, 0, 0), (255, 120, 20)

@lru_cache(None)
def F(size): return ImageFont.truetype(BOLD, max(4, int(size)))
def clamp(t): return min(max(t, 0.0), 1.0)
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_back(t):
    t = clamp(t); c = 1.9
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
def text(d, s, xy, size, fill=WHITE, stroke=8, sfill=BLACK, anchor="mm"):
    if size < 5: return
    d.text(xy, s, font=F(size), fill=fill, stroke_width=stroke, stroke_fill=sfill, anchor=anchor)

# ---------------------------------------------------------------- photos
PH = {}
def load(i):
    if i in PH: return PH[i]
    im = ImageOps.exif_transpose(Image.open(f"photos/{i:02d}.jpg")).convert("RGB")
    bg = ImageOps.fit(im, (int(W * 1.15), int(H * 1.15)))
    bg = bg.filter(ImageFilter.GaussianBlur(28))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    fg = im.copy(); fg.thumbnail((980, 1050), Image.LANCZOS)
    fg = ImageOps.expand(fg, 14, WHITE)
    sh = Image.new("RGBA", (fg.width + 60, fg.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([30, 40, fg.width + 30, fg.height + 40], fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    sh.paste(fg, (30, 30))
    PH[i] = (bg, sh)
    return PH[i]

def photo_frame(i, lt, dur, cy=1000, rays=None, rot=0.0, shake=0.0, show_fg=True):
    bg, fg = load(i)
    z = 1 + 0.06 * lt / dur
    bw, bh = bg.size
    cw, ch = int(W * 1.15 / z), int(H * 1.15 / z)
    x0, y0 = (bw - cw) // 2, (bh - ch) // 2
    img = bg.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
    if rays is not None: paste_rays(img, rays, rot, W / 2, cy)
    if show_fg:
        s = ease_back(lt / 0.3) * (1 + 0.07 * lt / dur)
        if s > 0.02:
            f2 = fg.resize((max(1, int(fg.width * s)), max(1, int(fg.height * s))), Image.BILINEAR)
            dx = shake * math.sin(lt * 47); dy = shake * math.cos(lt * 39)
            img.paste(f2, (int(W / 2 - f2.width / 2 + dx), int(cy - f2.height / 2 + dy)), f2)
    return img

def make_rays(c1, n=24, size=2600):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = size / 2
    for k in range(n):
        a0 = 2 * math.pi * k / n; a1 = a0 + math.pi / n
        d.polygon([(c, c), (c + size * math.cos(a0), c + size * math.sin(a0)), (c + size * math.cos(a1), c + size * math.sin(a1))], fill=c1)
    return im
RAYS_GOLD = make_rays((255, 200, 50, 70))
RAYS_WHITE = make_rays((255, 255, 255, 30))
def paste_rays(img, rays, ang, cx, cy):
    r = rays.rotate(ang, resample=Image.BILINEAR); s = r.size[0]
    r = r.crop((int(s / 2 - cx), int(s / 2 - cy), int(s / 2 - cx + W), int(s / 2 - cy + H)))
    img.paste(r, (0, 0), r)

def star(d, cx, cy, R, rot, fill, outline=BLACK, width=6):
    pts = []
    for k in range(10):
        a = rot + k * math.pi / 5 - math.pi / 2; rr = R if k % 2 == 0 else R * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill, outline=outline, width=width)

SPARKS = [(random.uniform(0, W), random.uniform(0, H), random.uniform(0, 6.28), random.uniform(10, 30)) for _ in range(60)]
def sparkles(d, t, color=(255, 240, 160)):
    for (sx, sy, ph, sz) in SPARKS:
        r = sz * max(0, math.sin(t * 4 + ph))
        if r > 1:
            d.polygon([(sx, sy - r), (sx + r * .25, sy - r * .25), (sx + r, sy), (sx + r * .25, sy + r * .25), (sx, sy + r),
                       (sx - r * .25, sy + r * .25), (sx - r, sy), (sx - r * .25, sy - r * .25)], fill=color)

CONF_COLORS = [(255, 60, 60), GOLD, (60, 200, 255), (120, 255, 120), (255, 120, 220), WHITE]
CONF = [dict(x=random.uniform(0, W), y=random.uniform(-H, 0), vy=random.uniform(250, 600), vx=random.uniform(-80, 80),
             a=random.uniform(0, 6.28), va=random.uniform(-8, 8), c=random.choice(CONF_COLORS), s=random.uniform(12, 26)) for _ in range(220)]
def confetti(d, t):
    for p in CONF:
        y = (p["y"] + p["vy"] * t) % (H + 200) - 100
        x = p["x"] + p["vx"] * t + 40 * math.sin(t * 3 + p["a"])
        a = p["a"] + p["va"] * t; s = p["s"]; w = s * abs(math.cos(a * 1.3)) + 3; ca, sa = math.cos(a), math.sin(a)
        d.polygon([(x + dx * ca - dy * sa, y + dx * sa + dy * ca) for dx, dy in [(-w/2, -s/3), (w/2, -s/3), (w/2, s/3), (-w/2, s/3)]], fill=p["c"])

def speed_lines(d, t, n=18):
    rnd = random.Random(int(t * 30))
    for _ in range(n):
        y = rnd.uniform(0, H); x = rnd.uniform(-200, W); L = rnd.uniform(150, 450)
        d.line([x, y, x + L, y], fill=(255, 255, 255), width=rnd.choice([2, 3, 4]))

def tag(d, s, y, a, fill=RED, tc=WHITE, size=60):
    if a <= 0: return
    k = ease_back(a); wdt = F(size).getlength(s) + 90
    d.rounded_rectangle([540 - wdt / 2 * k, y - 60 * k, 540 + wdt / 2 * k, y + 60 * k], int(30 * k) + 1, fill=fill, outline=WHITE, width=6)
    text(d, s, (540, y), size * k, tc, 3)

# ---------------------------------------------------------------- scenes
def scene_intro(t):
    img = photo_frame(6, t, 3.5, show_fg=False)
    paste_rays(img, RAYS_WHITE, t * 12, W / 2, 820)
    d = ImageDraw.Draw(img); sparkles(d, t)
    word = "GALALAND"; f = F(150); ws = [f.getlength(c) for c in word]; x = (W - sum(ws) - 42) / 2
    for k, c in enumerate(word):
        lt = t - 0.15 - k * 0.11
        if lt > 0:
            y = 820 - (1 - ease_back(lt / 0.5)) * 750
            d.text((x + ws[k] / 2, y), c, font=f, fill=GOLD if k % 2 == 0 else ORANGE, stroke_width=10, stroke_fill=(120, 0, 30), anchor="mm")
        x += ws[k] + 6
    tag(d, "DIECAST WORLD", 980, (t - 1.4) / 0.4, RED, WHITE, 64)
    a = clamp((t - 2.0) / 0.4)
    if a > 0: text(d, "Hot Wheels  •  Chase  •  STH", (540, 1150 + (1 - ease_out(a)) * 60), 58, (255, 240, 200), 6)
    return img

CHASE_SHOTS = [(0.0, 1.4, 5), (1.4, 2.6, 0), (2.6, 3.6, 5), (3.6, 4.9, 1), (4.9, 6.5, 4)]
def scene_chase(t):
    for a, b, i in CHASE_SHOTS:
        if a <= t < b: lt, dur, ph = t - a, b - a, i
    img = photo_frame(ph, lt, dur, cy=1060, shake=6)
    d = ImageDraw.Draw(img); speed_lines(d, t)
    on = int(t * 8) % 2
    img = Image.blend(img, Image.new("RGB", (W, H), (255, 0, 0) if on else (0, 70, 255)), 0.13)
    d = ImageDraw.Draw(img)
    sh = 8 * math.sin(t * 40) * clamp(1 - (t % 1.3) * 2)
    k = ease_back(t / 0.5)
    text(d, "THE CHASE", (540 + sh, 260), 140 * k, GOLD, 10, (120, 0, 30))
    text(d, "IS ON!", (540 - sh, 420), 160 * k, WHITE, 10, RED)
    if ph == 5: tag(d, "🚨 POLICE PURSUIT" if False else "POLICE PURSUIT", 1760, (lt) / 0.3, (20, 40, 160), WHITE, 56)
    else: tag(d, "Hunt every CHASE car!", 1760, (lt) / 0.3, BLACK, GOLD, 54)
    return img

def scene_sth(t):
    if t < 3.0:
        img = photo_frame(15, t, 3.0, cy=1030, rays=RAYS_GOLD, rot=-t * 25)
        d = ImageDraw.Draw(img); sparkles(d, t * 1.5)
        a = ease_back((t - 0.2) / 0.5); s = 1 + 0.05 * math.sin(t * 8)
        text(d, "SUPER", (540, 230), 130 * a * s, GOLD, 10, (120, 0, 30))
        text(d, "TREASURE HUNT", (540, 370), 105 * a * s, WHITE, 9, RED)
        r = 120 * ease_back((t - 0.6) / 0.5)
        if r > 2:
            star(d, 860, 600, r, t * 1.5, GOLD, (150, 60, 0), 6)
            text(d, "STH", (860, 604), 54 * r / 120, RED, 3, WHITE)
        tag(d, "Spot the TH logo = JACKPOT!", 1750, (t - 1.0) / 0.4, GOLD, BLACK, 50)
    else:
        lt = t - 3.0
        img = photo_frame(12, lt, 2.5, cy=1030, rays=RAYS_GOLD, rot=lt * 25)
        d = ImageDraw.Draw(img); sparkles(d, t * 1.5)
        k = ease_back(lt / 0.4)
        text(d, "HUNT THE", (540, 250), 120 * k, WHITE, 9, RED)
        text(d, "RARE ONES!", (540, 400), 130 * k, GOLD, 10, (120, 0, 30))
        tag(d, "CHASE  •  STH  •  RARE", 1750, (lt - 0.4) / 0.4, RED, WHITE, 54)
    return img

MONTAGE = [(9, "SUPERCARS"), (14, "MUSCLE CARS"), (17, "CLASSICS"), (13, "MAINLINES"), (10, "LOOSE HAULS"), (11, "CARDED"), (7, "FULL WALLS")]
def scene_montage(t):
    step = 7.0 / len(MONTAGE); n = min(int(t / step), len(MONTAGE) - 1); lt = t - n * step
    ph, cap = MONTAGE[n]
    img = photo_frame(ph, lt, step, cy=1020)
    d = ImageDraw.Draw(img)
    k = ease_back(t / 0.5)
    text(d, "COLLECT", (540, 230), 130 * k, GOLD, 10, (120, 0, 30))
    text(d, "THEM ALL!", (540, 380), 130 * k, WHITE, 10, (0, 60, 140))
    tag(d, cap, 1760, lt / 0.25, [RED, BLACK, ORANGE, (0, 90, 200)][n % 4], WHITE, 62)
    if lt < 0.12: img = Image.blend(img, Image.new("RGB", (W, H), WHITE), 0.6 * (1 - lt / 0.12))
    return img

def scene_end(t):
    img = photo_frame(7, t, 6.0, show_fg=False)
    paste_rays(img, RAYS_GOLD, t * 15, W / 2, 1150)
    d = ImageDraw.Draw(img); confetti(d, t)
    text(d, "WISHING", (540, 360), 120 * ease_back(t / 0.5), WHITE, 9, (120, 0, 30))
    k2 = ease_back((t - 0.3) / 0.6)
    if k2 > 0: text(d, "GALALAND", (540, 580), 165 * k2 * (1 + 0.04 * math.sin(t * 6)), GOLD, 12, (120, 0, 30))
    k3 = ease_back((t - 0.7) / 0.5)
    if k3 > 0: text(d, "HUGE SUCCESS!", (540, 780), 110 * k3, WHITE, 9, RED)
    r = 190 * ease_back((t - 1.0) / 0.6)
    if r > 2:
        star(d, 540, 1130, r, t * 0.8, GOLD, (150, 60, 0), 8)
        text(d, "#1", (540, 1140), 110 * r / 190, RED, 5, WHITE)
    a = clamp((t - 1.8) / 0.5)
    if a > 0:
        y = 1480 + (1 - ease_out(a)) * 120
        text(d, "Keep Collecting.", (540, y), 70, (255, 240, 200), 6)
        text(d, "Keep Chasing. Keep Winning!", (540, y + 100), 56, GOLD, 6)
        text(d, "Chase  •  STH  •  Diecast", (540, y + 200), 50, WHITE, 5)
    return img

CREDITS = json.load(open("credits.json"))
def scene_credits(t):
    img = Image.new("RGB", (W, H), (10, 10, 20)); d = ImageDraw.Draw(img)
    text(d, "GALALAND", (540, 300), 120, GOLD, 8, (120, 0, 30))
    text(d, "Photo credits (Wikimedia Commons)", (540, 470), 40, WHITE, 0)
    y = 560
    for k, v in sorted(CREDITS.items(), key=lambda kv: int(kv[0])):
        text(d, f"{v['artist'][:28]} — {v['license']}", (540, y), 34, (200, 200, 210), 0); y += 58
    text(d, "Hot Wheels is a trademark of Mattel. Fan video, not affiliated.", (540, y + 50), 28, (150, 150, 160), 0)
    return img

SCENES = [(0, 3.5, scene_intro), (3.5, 10, scene_chase), (10, 15.5, scene_sth), (15.5, 22.5, scene_montage),
          (22.5, 28.3, scene_end), (28.3, 30, scene_credits)]
CUTS = [s[0] for s in SCENES[1:]]

def frame(i):
    t = i / FPS
    for a, b, fn in SCENES:
        if a <= t < b: img = fn(t - a); break
    for c in CUTS:
        dt = t - c
        if 0 <= dt < 0.25: img = Image.blend(img, Image.new("RGB", (W, H), WHITE), 1 - dt / 0.25)
    if t > DUR - 0.4: img = Image.blend(img, Image.new("RGB", (W, H), BLACK), (t - (DUR - 0.4)) / 0.4)
    return img

# ---------------------------------------------------------------- audio
SR = 44100; beat = 60 / 128
N = int(SR * DUR); audio = np.zeros(N); tt = np.arange(N) / SR; rng = np.random.default_rng(1)
def add(sig, start):
    s = int(start * SR); e = min(N, s + len(sig))
    if 0 <= s < N: audio[s:e] += sig[:e - s]
kl = np.arange(int(0.25 * SR)) / SR
kick = np.sin(2 * np.pi * np.cumsum(45 + 110 * np.exp(-kl * 25)) / SR) * np.exp(-kl * 10) * 0.9
hl = np.arange(int(0.06 * SR)); hat = np.diff(rng.standard_normal(len(hl) + 1)) * np.exp(-hl / SR * 70) * 0.12
cl = np.arange(int(0.18 * SR)); clap = np.diff(rng.standard_normal(len(cl) + 1)) * np.exp(-cl / SR * 22) * 0.25
roots = [55.0, 43.65, 65.41, 49.0]
MUSIC_END = 28.3
for b in range(int(MUSIC_END / beat)):
    st = b * beat
    if st < 0.4: continue
    add(kick, st); add(hat, st + beat / 2)
    if b % 2 == 1: add(clap, st)
    root = roots[(b // 4) % 4]
    for half in range(2):
        L = int(beat / 2 * SR); x = np.arange(L) / SR
        add(np.sign(np.sin(2 * np.pi * root * (2 if half else 1) * x)) * 0.10 * np.exp(-x * 5), st + half * beat / 2)
    if st > 10:
        for q in range(4):
            L = int(beat / 4 * SR); x = np.arange(L) / SR
            f = root * 4 * [1, 1.5, 2, 1.5][q] * (1.26 if q == 1 else 1)
            add(np.sin(2 * np.pi * f * x) * np.exp(-x * 14) * 0.08, st + q * beat / 4)
m = (tt >= 3.5) & (tt < 10)
audio[m] += (np.sin(2 * np.pi * np.cumsum(750 + 200 * np.sin(2 * np.pi * 1.6 * tt)) / SR) * 0.06)[m]
audio[m] += (np.sin(2 * np.pi * np.cumsum(70 + 15 * np.sin(2 * np.pi * 0.7 * tt)) / SR) * 0.08)[m]
for c in [0.4] + CUTS[:-1]:
    L = int(0.6 * SR); x = np.arange(L) / SR
    add(np.convolve(rng.standard_normal(L), np.ones(8) / 8, "same") * np.sin(np.pi * x / 0.6) ** 2 * 0.35, c - 0.4)
for st in [10.2, 10.6, 13.0, 22.6, 23.0, 23.4]:
    for f in [1318.5, 1760, 2637]:
        L = int(SR); x = np.arange(L) / SR
        add(np.sin(2 * np.pi * f * x) * np.exp(-x * 5) * 0.05, st)
audio *= np.clip((MUSIC_END + 1.2 - tt) / 1.2, 0, 1)
audio = audio / np.max(np.abs(audio)) * 0.85
with wave.open("audio_real.wav", "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((audio * 32767).astype(np.int16).tobytes())

if len(sys.argv) > 1 and sys.argv[1] == "preview":
    ims = [frame(int(s * FPS)).resize((W // 4, H // 4)) for s in [2.8, 5.5, 8.5, 12, 14.5, 17, 20, 26, 29]]
    sheet = Image.new("RGB", (W // 4 * len(ims), H // 4))
    for k, im in enumerate(ims): sheet.paste(im, (k * W // 4, 0))
    sheet.save("preview_real.png"); sys.exit()

p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                      "-i", "-", "-i", "audio_real.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                      "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", "Galaland_HotWheels.mp4"], stdin=subprocess.PIPE)
for i in range(NF): p.stdin.write(frame(i).tobytes())
p.stdin.close(); p.wait(); print("done")
