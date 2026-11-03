"""
Bhai Dooj gift reel (Instagram Reel / YouTube Short, 1080x1920 @ 30fps).

Look: dark, cinematic product showcase. The wall photo (assets/wall.jpg) is used
for the intro and the ending, and each gift uses its own product photo
(assets/products/*), cut out and placed under a coloured spotlight. Every cut
lands on the beat of the dhol soundtrack, which is generated in code (no
copyrighted music).

    python make_reel.py            # -> bhai_dooj_reel.mp4
    python make_reel.py --no-music # silent, to add trending audio inside Instagram

Needs Pillow, numpy and ffmpeg.
"""
import argparse
import math
import os
import subprocess
import wave

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
FONTS = os.path.join(ASSETS, "fonts")

GOLD = (245, 196, 81)
WHITE = (255, 255, 255)
SOFT = (225, 225, 230)

BPM = 104
BEAT = 60 / BPM

# ----------------------------------------------------------------- products
PRODUCTS = [
    dict(file="ferrari.webp", brand="HOT WHEELS  •  RLC", title=["FERRARI F40"],
         line="Red Line Club Exclusive", glow=(230, 30, 40)),
    dict(file="mustang.jpg", brand="HOT WHEELS  •  RLC", title=["MUSTANG", "SHELBY GT500"],
         line="Original RLC  •  Spectraflame Blue", glow=(30, 110, 255), dark_bg=True),
    dict(file="godzilla.jpg", brand="HOT WHEELS  PREMIUM", title=["NISSAN SKYLINE", "GODZILLA"],
         line="GT-R BNR34  •  Pop Culture", glow=(200, 60, 50)),
    dict(file="tfox.jpg", brand="HOT WHEELS  •  SIGNED", title=["T-FOX", "GT-R GUACZILLA"],
         line="Autographed card  •  Nissan GT-R R35", glow=(120, 220, 40)),
    dict(file="brian_set.jpg", brand="FAST & FURIOUS  •  SILVER SERIES", title=["BRIAN O'CONNER", "SET"],
         line="All 5 cars  •  Complete set", glow=(255, 130, 20), wide=True),
]
N = len(PRODUCTS)

INTRO_S = 8 * BEAT
GIFT_S = 6 * BEAT
OUTRO_S = 9 * BEAT
TOTAL_S = INTRO_S + GIFT_S * N + OUTRO_S
CUTS = [INTRO_S + GIFT_S * k for k in range(N + 1)]

# ----------------------------------------------------------------- fonts / text
_fc = {}


def font(size, name="Anton-Regular"):
    size = max(1, int(size))
    k = (size, name)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(os.path.join(FONTS, f"{name}.ttf"), size)
    return _fc[k]


def SEMI(s):
    return font(s, "Poppins-SemiBold")


def MED(s):
    return font(s, "Poppins-Medium")


_dummy = ImageDraw.Draw(Image.new("RGB", (1, 1)))


def text_w(txt, f, track=0):
    if not track:
        return _dummy.textlength(txt, font=f)
    return sum(_dummy.textlength(c, font=f) for c in txt) + track * (len(txt) - 1)


def fit(txt, name, max_w, start):
    s = start
    while s > 20 and text_w(txt, font(s, name)) > max_w:
        s -= 2
    return s


def draw_text(base, cy_top, txt, f, fill, alpha=1.0, track=0, rise=0.0, shadow=True, cx=W / 2):
    """Centered text; `rise` (0..1) slides it up out of a clip box (title reveal)."""
    if alpha <= 0.01:
        return
    w = text_w(txt, f, track)
    asc, desc = f.getmetrics()
    lh = asc + desc
    layer = Image.new("RGBA", (int(w) + 40, lh + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    off = int(lh * rise)
    x = 20
    if track:
        for c in txt:
            d.text((x, 20 + off), c, font=f, fill=fill + (255,))
            x += d.textlength(c, font=f) + track
    else:
        d.text((x, 20 + off), txt, font=f, fill=fill + (255,))
    if alpha < 1:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    px, py = int(cx - w / 2 - 20), int(cy_top - 20)
    if shadow:
        sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        sh.putalpha(layer.getchannel("A").point(lambda v: int(v * 0.6)))
        sh = sh.filter(ImageFilter.GaussianBlur(10))
        base.alpha_composite(sh, (px, py + 6))
    # clip to the line box so the reveal slides in from below
    clip = layer.crop((0, 0, layer.width, lh + 26))
    base.alpha_composite(clip, (px, py))


# ----------------------------------------------------------------- image prep
def cutout(path, thresh=28):
    """Remove a plain white / light-grey studio background."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    work = im.copy()
    key = (255, 0, 255)
    for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1),
              (0, h // 2), (w - 1, h // 2)]:
        if work.getpixel(p) != key and min(work.getpixel(p)) > 200:
            ImageDraw.floodfill(work, p, key, thresh=thresh)
    r, g, b = work.split()
    bg = ImageChops.multiply(ImageChops.multiply(r.point(lambda v: 255 if v == 255 else 0),
                                                 g.point(lambda v: 255 if v == 0 else 0)),
                             b.point(lambda v: 255 if v == 255 else 0))
    alpha = ImageChops.invert(bg).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out.crop(alpha.getbbox())


def dark_photo(path):
    """Product shot already on black: fade its edges into the backdrop."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    y, x = np.ogrid[:h, :w]
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    a = np.clip((1.0 - d) / 0.35, 0, 1) ** 1.5
    lum = np.asarray(im).max(axis=2) / 255.0
    a = a * np.clip(lum * 6 + 0.15, 0, 1)
    out = im.convert("RGBA")
    out.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    return out


def fit_size(im, max_w, max_h):
    s = min(max_w / im.width, max_h / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    if s > 1.2:
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=90, threshold=2))
    return im


def with_reflection(im, strength=0.22, frac=0.28):
    rh = int(im.height * frac)
    ref = im.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, im.width, rh))
    grad = np.linspace(strength, 0, rh)[:, None] * np.ones((1, im.width))
    a = np.asarray(ref.getchannel("A")).astype(np.float32) * grad
    ref.putalpha(Image.fromarray(a.astype(np.uint8)))
    ref = ref.filter(ImageFilter.GaussianBlur(2))
    out = Image.new("RGBA", (im.width, im.height + rh + 6), (0, 0, 0, 0))
    # soft contact shadow
    sh = Image.new("L", out.size, 0)
    ImageDraw.Draw(sh).ellipse((im.width * 0.08, im.height - 18, im.width * 0.92, im.height + 22), fill=160)
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    out.paste((0, 0, 0, 255), (0, 0), sh)
    out.alpha_composite(im, (0, 0))
    out.alpha_composite(ref, (0, im.height + 6))
    return out


for p in PRODUCTS:
    path = os.path.join(ASSETS, "products", p["file"])
    if p.get("dark_bg"):
        im = fit_size(dark_photo(path), 1080, 1080)
        p["img"] = im
    else:
        maxw, maxh = (1000, 900) if p.get("wide") else (860, 960)
        p["img"] = with_reflection(fit_size(cutout(path), maxw, maxh))

# ----------------------------------------------------------------- backdrops
WALL = Image.open(os.path.join(ASSETS, "wall.jpg")).convert("RGB")


def grade(img, amt=0.55):
    """Cinematic grade: darker, warm highlights, teal-ish shadows."""
    a = np.asarray(img).astype(np.float32) / 255.0
    a = a ** 1.25 * amt
    a[..., 0] = a[..., 0] * 1.08 + 0.01
    a[..., 2] = a[..., 2] * 0.92 + 0.025
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


# vertical plate of the wall, cropped from its centre, a bit bigger than the frame
_ph = int(H * 1.18)
_pw = int(WALL.width * _ph / WALL.height)
WALL_PLATE = grade(WALL.resize((_pw, _ph), Image.LANCZOS), 0.62)


def vignette(strength=0.75):
    y, x = np.ogrid[:H, :W]
    d = np.sqrt(((x - W / 2) / (W * 0.7)) ** 2 + ((y - H / 2) / (H * 0.62)) ** 2)
    return np.clip(1.12 - d * strength, 0.18, 1.0)[..., None].astype(np.float32)


VIG = vignette()

_blur_wall = WALL.resize((W // 4, int(W // 4 * WALL.height / WALL.width)), Image.BILINEAR)
_blur_wall = _blur_wall.crop(((_blur_wall.width - W // 8) // 2, 0,
                              (_blur_wall.width + W // 8) // 2, _blur_wall.height))
_blur_wall = _blur_wall.resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(30))
_blur_wall = np.asarray(_blur_wall).astype(np.float32) * 0.16


def product_backdrop(color):
    y, x = np.ogrid[:H, :W]
    base = np.zeros((H, W, 3), np.float32) + np.array([10, 10, 14], np.float32)
    base += _blur_wall
    d = np.sqrt(((x - W / 2) / 620.0) ** 2 + ((y - 1060) / 760.0) ** 2)
    glow = np.exp(-d ** 2 * 1.6)[..., None]
    base += glow * np.array(color, np.float32) * 0.42
    # floor
    floor = np.clip((y - 1450) / 470.0, 0, 1)[..., None]
    base *= 1 - 0.5 * floor
    base *= VIG
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))


BACKDROPS = [product_backdrop(p["glow"]) for p in PRODUCTS]

rng_g = np.random.default_rng(11)
GRAIN = [Image.fromarray(np.clip(rng_g.normal(128, 9, (H // 2, W // 2)), 0, 255).astype(np.uint8))
         .resize((W, H), Image.BILINEAR) for _ in range(6)]


# ----------------------------------------------------------------- easing
def clamp(t):
    return max(0.0, min(1.0, t))


def ease(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_io(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def beat_pulse(t):
    """0..1 spike on every beat, used for subtle zoom punches."""
    ph = (t / BEAT) % 1.0
    return math.exp(-ph * 9)


def zoom_crop(img, z, cx=None, cy=None, dx=0, dy=0):
    cx = img.width / 2 if cx is None else cx
    cy = img.height / 2 if cy is None else cy
    cw = img.width / z if img.width / img.height < W / H else img.height * W / H / z
    ch = cw * H / W
    box = (cx - cw / 2 + dx, cy - ch / 2 + dy, cx + cw / 2 + dx, cy + ch / 2 + dy)
    return img.crop(tuple(int(v) for v in box)).resize((W, H), Image.BILINEAR)


def handheld(t, amt=5.0):
    return (amt * math.sin(t * 1.3) + amt * 0.4 * math.sin(t * 3.1),
            amt * math.cos(t * 1.1) + amt * 0.4 * math.sin(t * 2.7))


# ----------------------------------------------------------------- scenes
def scene_intro(t):
    z = 1.0 + 0.10 * ease_io(t / INTRO_S) + 0.012 * beat_pulse(t)
    dx, dy = handheld(t)
    frame = zoom_crop(WALL_PLATE, z, dx=dx, dy=dy)
    dim = 1.0 if t < 0.35 else 1 - 0.35 * ease((t - 0.35) / 0.6)
    arr = np.asarray(frame).astype(np.float32) * dim * VIG
    frame = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")

    b = t / BEAT
    if b < 4:
        a = ease((b - 0.6) / 0.5)
        draw_text(frame, 560, "BHAI DOOJ", font(230), GOLD, a, rise=1 - ease((b - 0.6) / 0.6))
        a = ease((b - 1.6) / 0.5)
        draw_text(frame, 860, "aa raha hai...", MED(70), WHITE, a)
        out = clamp((b - 3.6) / 0.4)
        if out > 0:
            frame = Image.blend(frame, Image.fromarray((arr * 0.6).astype(np.uint8)).convert("RGBA"), out)
    else:
        a = ease((b - 4.0) / 0.4)
        draw_text(frame, 600, "GIFT NAHI DOGI", font(150), WHITE, a, rise=1 - ease((b - 4.0) / 0.45))
        a = ease((b - 4.5) / 0.4)
        draw_text(frame, 790, "BHAI KO?", font(190), GOLD, a, rise=1 - ease((b - 4.5) / 0.45))
        a = ease((b - 6.0) / 0.5)
        draw_text(frame, 1150, "5 gifts jo bhai ko pakka pasand aayenge", MED(44), SOFT, a)
    return frame


def scene_gift(t, i):
    p = PRODUCTS[i]
    frame = BACKDROPS[i].copy().convert("RGBA")

    # header
    a = ease(t / 0.35)
    draw_text(frame, 150, f"GIFT  {i + 1:02d} / {N:02d}", SEMI(30), GOLD, a, track=8, shadow=False)
    ImageDraw.Draw(frame).line((W / 2 - 40 * a, 212, W / 2 + 40 * a, 212), fill=GOLD + (255,), width=3)
    draw_text(frame, 240, p["brand"], SEMI(32), SOFT, ease((t - 0.1) / 0.4), track=6, shadow=False)
    y = 300
    for k, line in enumerate(p["title"]):
        size = fit(line, "Anton-Regular", W - 120, 150 if k == 0 else 120)
        tt = t - 0.12 - 0.1 * k
        draw_text(frame, y, line, font(size), WHITE if k == 0 else GOLD, ease(tt / 0.3),
                  rise=1 - ease(tt / 0.4))
        y += int(size * 1.25)

    # product: punch in, then slow push
    im = p["img"]
    top = y + 70 if not p.get("dark_bg") else 560
    bottom = 1665
    fitk = 1.0 if p.get("dark_bg") else min(1.0, (bottom - top) / im.height)
    s = fitk * (1.0 + 0.12 * (1 - ease(t / 0.45)) + 0.03 * (t / GIFT_S) + 0.008 * beat_pulse(t))
    im = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)
    alpha = ease(t / 0.3)
    if alpha < 1:
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    if p.get("dark_bg"):
        frame.alpha_composite(im, (int(W / 2 - im.width / 2), int(1120 - im.height / 2)))
    else:
        cy = (top + bottom) / 2
        frame.alpha_composite(im, (int(W / 2 - im.width / 2), int(cy - im.height / 2)))

    # footer
    a = ease((t - 0.7) / 0.5)
    draw_text(frame, 1690, p["line"], MED(40), SOFT, a)
    a = ease((t - 1.2) / 0.5)
    draw_text(frame, 1760, "Perfect Bhai Dooj gift", SEMI(34), GOLD, a, track=3)
    return frame


def scene_outro(t):
    z = 1.22 - 0.2 * ease_io(t / OUTRO_S)
    dx, dy = handheld(t + 9)
    frame = zoom_crop(WALL_PLATE, z, dx=dx, dy=dy)
    arr = np.asarray(frame).astype(np.float32) * 0.55 * VIG
    frame = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")

    b = t / BEAT
    draw_text(frame, 470, "IS BHAI DOOJ", SEMI(40), GOLD, ease(b / 0.6), track=10)
    draw_text(frame, 550, "BHAI KO DO", font(170), WHITE, ease((b - 0.5) / 0.4), rise=1 - ease((b - 0.5) / 0.45))
    draw_text(frame, 760, "HOT WHEELS", font(210), GOLD, ease((b - 1.5) / 0.4), rise=1 - ease((b - 1.5) / 0.45))
    a = ease((b - 3.0) / 0.5)
    d = ImageDraw.Draw(frame)
    d.line((W / 2 - 160 * a, 1080, W / 2 + 160 * a, 1080), fill=GOLD + (255,), width=3)
    draw_text(frame, 1120, "DM TO ORDER", SEMI(64), WHITE, ease((b - 3.5) / 0.5), track=10)
    draw_text(frame, 1225, "Limited pieces  •  RLC  •  Premium", MED(40), SOFT, ease((b - 4.5) / 0.5))
    return frame


def whip(img, amount):
    """Horizontal motion blur + slide used for beat-synced cuts."""
    if amount <= 0.02:
        return img
    arr = np.asarray(img).astype(np.float32)
    shift = int(70 * amount)
    acc = np.zeros_like(arr)
    taps = 7
    for k in range(taps):
        acc += np.roll(arr, (k - taps // 2) * max(1, shift // taps), axis=1)
    return Image.fromarray((acc / taps).astype(np.uint8))


def render(n):
    t = n / FPS
    if t < INTRO_S:
        f = scene_intro(t)
    elif t < CUTS[-1]:
        i = int((t - INTRO_S) // GIFT_S)
        f = scene_gift(t - INTRO_S - i * GIFT_S, i)
    else:
        f = scene_outro(t - CUTS[-1])
    f = f.convert("RGB")
    for c in CUTS:
        dt = t - c
        if -0.1 < dt < 0.12:
            f = whip(f, 1 - abs(dt) / 0.12)
        if 0 <= dt < 0.07:
            f = Image.blend(f, Image.new("RGB", (W, H), (255, 245, 230)), 0.35 * (1 - dt / 0.07))
    # film grain
    g = GRAIN[n % len(GRAIN)]
    f = Image.blend(f, ImageChops.overlay(f, Image.merge("RGB", [g] * 3)), 0.6)
    return f


# ----------------------------------------------------------------- audio
SR = 44100
rng = np.random.default_rng(3)


def env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t * decay)


def dhol_bass(n=int(0.5 * SR)):
    t = np.arange(n) / SR
    f = 62 + 70 * np.exp(-t * 22)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * env(n, 0.002, 7)
    slap = rng.standard_normal(n) * env(n, 0.0005, 70) * 0.35
    return body + slap


def dhol_tilli(n=int(0.18 * SR)):
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 410 * t) * 0.5 + np.sin(2 * np.pi * 690 * t) * 0.3
    noise = np.convolve(rng.standard_normal(n), np.ones(3) / 3, "same")
    return (tone + noise * 0.9) * env(n, 0.0005, 38)


def shaker(n=int(0.07 * SR)):
    x = rng.standard_normal(n)
    x = x - np.convolve(x, np.ones(6) / 6, "same")  # crude high-pass
    return x * env(n, 0.004, 55)


def pluck(freq, dur, bright=0.996):
    """Karplus-Strong string, sounds like a real plucked instrument."""
    n = int(dur * SR)
    p = int(SR / freq)
    buf = rng.uniform(-1, 1, p)
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = bright * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out


def reverb(x, secs=1.4, mix=0.22):
    n = int(secs * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 4.5)
    ir = np.convolve(ir, np.ones(8) / 8, "same")
    ir /= np.sqrt(np.sum(ir ** 2))
    L = len(x) + n
    nfft = 1 << (L - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[:len(x)]
    return x * (1 - mix) + wet * mix * 1.5


def whoosh(n=int(0.45 * SR)):
    x = rng.standard_normal(n)
    out = np.zeros(n)
    t = np.linspace(0, 1, n)
    k = (2 + 30 * t ** 2).astype(int)  # sweeping smoothing = filter sweep
    cs = np.cumsum(np.insert(x, 0, 0))
    for i in range(n):
        a = max(0, i - k[i])
        out[i] = (cs[i + 1] - cs[a]) / (i + 1 - a)
    return out * np.sin(np.pi * t) ** 2 * 1.6


def add(buf, s, at):
    i = max(0, int(at * SR))
    if i >= len(buf):
        return
    e = min(len(buf), i + len(s))
    buf[i:e] += s[:e - i]


def make_music(path, seconds):
    n = int(seconds * SR)
    drums = np.zeros(n)
    music = np.zeros(n)
    fx = np.zeros(n)
    bpm = 104
    st = 60 / bpm / 4  # sixteenth
    # bhangra-style chaal over 16 steps
    bass_steps = {0, 6, 8, 11, 14}
    tilli_steps = {3, 4, 7, 10, 12, 15}
    B, T, S = dhol_bass(), dhol_tilli(), shaker()
    steps = int(seconds / st)
    for k in range(steps):
        s = k % 16
        at = k * st + rng.normal(0, 0.004)  # human timing
        vel = rng.uniform(0.85, 1.0)
        if k * st < 0.9:  # soft start: only shaker
            add(drums, S * 0.35 * vel, at)
            continue
        if s in bass_steps:
            add(drums, B * 0.95 * vel, at)
        if s in tilli_steps:
            add(drums, T * 0.45 * vel, at)
        if s % 2 == 1:
            add(drums, S * 0.18 * vel, at)

    # tanpura-ish drone + melody (Raag Bilawal-ish, D major pentatonic feel)
    sa = 146.83  # D3
    for k in range(int(seconds / (st * 8))):
        at = k * st * 8
        for j, r in enumerate([1.5, 2, 2, 1]):
            add(music, pluck(sa * r, 1.6, 0.9985) * 0.16, at + j * st * 2)
    melody = [12, 14, 16, 19, 16, 14, 12, 9, 12, 14, 16, 21, 19, 16, 14, 12,
              16, 19, 21, 24, 21, 19, 16, 14, 12, 14, 16, 14, 12, 9, 7, 12]
    for k in range(int(seconds / (st * 2))):
        at = k * st * 2 + rng.normal(0, 0.006)
        if at < 1.6 or (k % 8 == 7):
            continue
        f = sa * 2 ** (melody[k % len(melody)] / 12)
        add(music, pluck(f, 0.9, 0.995) * 0.32 * rng.uniform(0.8, 1.0), at)

    # whoosh on every scene change
    for c in [INTRO_S + GIFT_S * k for k in range(N + 1)]:
        add(fx, whoosh() * 0.25, c - 0.3)

    mix = reverb(drums, 0.8, 0.12) + reverb(music, 1.8, 0.3) + fx
    fade_in, fade_out = int(0.3 * SR), int(1.4 * SR)
    mix[:fade_in] *= np.linspace(0, 1, fade_in)
    mix[-fade_out:] *= np.linspace(1, 0, fade_out)
    mix = np.tanh(mix / np.max(np.abs(mix)) * 1.4)  # gentle glue/saturation
    mix = mix / np.max(np.abs(mix)) * 0.89
    stereo = np.stack([mix, np.roll(mix, int(0.012 * SR))], axis=1)  # slight width
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((stereo * 32767).astype(np.int16).tobytes())


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "bhai_dooj_reel.mp4"))
    ap.add_argument("--no-music", action="store_true")
    args = ap.parse_args()

    frames = int(TOTAL_S * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    wav = None
    if not args.no_music:
        wav = args.out + ".wav"
        make_music(wav, TOTAL_S)
        cmd += ["-i", wav, "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", args.out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(frames):
        proc.stdin.write(render(n).tobytes())
    proc.stdin.close()
    proc.wait()
    if wav:
        os.remove(wav)
    print(f"Saved {args.out} ({TOTAL_S:.1f}s)")


if __name__ == "__main__":
    main()
