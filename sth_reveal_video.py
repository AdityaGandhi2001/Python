"""
"2027 STH revealed" - fast, beat-synced Gen Z style Instagram reel.

Inputs : a folder of STH cutouts sth0.png .. sth8.png (see sth_prep_cars.py)
Output : 1080x1920 30fps MP4 with an original synthesized trap beat.

    python sth_reveal_video.py sth_assets out.mp4
"""

import math
import random
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
BPM = 150
BEAT = 60 / BPM  # 0.4 s

INTER = "/usr/share/fonts/opentype/inter/"
F_BLACK = INTER + "Inter-Black.otf"
F_BLACK_I = INTER + "Inter-BlackItalic.otf"
F_XB = INTER + "Inter-ExtraBold.otf"
F_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

CARS = [
    ("MIX A", "'64 LINCOLN CONTINENTAL", "purple drip unlocked", "💜"),
    ("MIX B", "BMW M4 GT3", "that livery goes crazy", "🏁"),
    ("MIX C", "DODGE D100", "off-road menace", "😤"),
    ("MIX D", "'88 MITSUBISHI STARION", "80s rizz fr", "💙"),
    ("MIX E", "ASTON MARTIN DB5 SAFARI", "lowkey the GOAT", "🐐"),
    ("MIX F", "FERRARI 12CILINDRI", "gold ferrari?? instant cop", "🤑"),
    ("MIX ?", "PORSCHE 911 CARRERA T", "no notes", "🫡"),
    ("MIX ?", "1967 SHELBY GT-500", "golden era", "🏆"),
    ("MIX J", "???", "still under wraps", "👀"),
]

HOOK_BEATS, CAR_BEATS, RECAP_BEATS, OUTRO_BEATS = 8, 4, 8, 8
T_HOOK = HOOK_BEATS * BEAT
T_CAR = CAR_BEATS * BEAT
T_CARS = T_CAR * len(CARS)
T_RECAP = RECAP_BEATS * BEAT
T_OUTRO = OUTRO_BEATS * BEAT
TOTAL = T_HOOK + T_CARS + T_RECAP + T_OUTRO

_fonts = {}


def font(path, size):
    k = (path, int(size))
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, int(size))
    return _fonts[k]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def p_(t, s, d):
    return clamp((t - s) / d)


def expo_out(t):
    t = clamp(t)
    return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)


def back_out(t, k=2.2):
    t = clamp(t)
    return 1 + (k + 1) * (t - 1) ** 3 + k * (t - 1) ** 2


# ------------------------------------------------------------------ assets
_emoji_cache = {}


def emoji(ch, size):
    k = (ch, size)
    if k not in _emoji_cache:
        f = ImageFont.truetype(F_EMOJI, 109)
        im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
        im = im.crop(im.getbbox())
        s = size / im.height
        _emoji_cache[k] = im.resize((max(1, int(im.width * s)), size), Image.LANCZOS)
    return _emoji_cache[k]


def accent_of(img):
    a = np.asarray(img.convert("RGBA")).reshape(-1, 4).astype(float)
    a = a[a[:, 3] > 200][:, :3]
    mx, mn = a.max(1), a.min(1)
    sat = (mx - mn) / (mx + 1)
    sel = a[(sat > 0.35) & (mx > 60)]
    if len(sel) < 50:
        return (90, 120, 255)
    c = np.median(sel, axis=0)
    # push to a vivid neon version
    c = c / max(1, c.max()) * 255
    return tuple(int(v) for v in c)


class Car:
    def __init__(self, path, width=1000):
        im = Image.open(path).convert("RGBA")
        s = width / im.width
        self.img = im.resize((width, int(im.height * s)), Image.LANCZOS)
        self.accent = accent_of(self.img)
        a = self.img.getchannel("A")
        glow = Image.new("RGBA", self.img.size, self.accent + (0,))
        glow.putalpha(a.point(lambda v: int(v * 0.9)))
        pad = 120
        g = Image.new("RGBA", (self.img.width + pad * 2, self.img.height + pad * 2), (0, 0, 0, 0))
        g.paste(glow, (pad, pad), glow)
        self.glow = g.filter(ImageFilter.GaussianBlur(45))
        self.glow_pad = pad
        self.ghosts = []
        for k in (0.35, 0.2, 0.1):
            gi = self.img.copy()
            gi.putalpha(a.point(lambda v, k=k: int(v * k)))
            self.ghosts.append(gi)
        # floor reflection
        ref = self.img.transpose(Image.FLIP_TOP_BOTTOM)
        grad = Image.linear_gradient("L").resize(ref.size)
        grad = grad.point(lambda v: int(max(0, 90 - v * 0.9)))
        ra = Image.composite(ref.getchannel("A"), Image.new("L", ref.size, 0), grad)
        ra = Image.fromarray((np.asarray(ra).astype(float) * np.asarray(grad) / 255).astype(np.uint8))
        ref.putalpha(ra)
        self.reflection = ref


def make_vignette():
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)
    return np.clip(1.15 - d ** 2 * 0.9, 0.35, 1.0)[..., None].astype(np.float32)


def make_grain(n=6, seed=3):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        g = rng.normal(0, 9, (H // 2, W // 2)).astype(np.float32)
        g = np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]
        out.append(g)
    return out


def make_grid():
    g = Image.new("RGBA", (W, H + 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    for x in range(0, W + 1, 120):
        d.line((x, 0, x, H + 120), fill=(255, 255, 255, 14), width=2)
    for y in range(0, H + 121, 120):
        d.line((0, y, W, y), fill=(255, 255, 255, 14), width=2)
    return g


# ------------------------------------------------------------------ text helpers
def text_w(txt, f):
    return f.getlength(txt)


def draw_text_c(img, cx, cy, txt, f, fill, stroke=0, sfill=(0, 0, 0), anchor="mm"):
    ImageDraw.Draw(img).text((cx, cy), txt, font=f, fill=fill, stroke_width=stroke,
                             stroke_fill=sfill, anchor=anchor)


def slam_text(base, cx, cy, txt, path, size, fill, p, stroke=0, sfill=(0, 0, 0), start=1.6):
    """Text that slams in from big to normal size."""
    if p <= 0:
        return
    e = expo_out(p)
    scale = start + (1 - start) * e
    f = font(path, max(10, size * scale))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_text_c(lay, cx, cy, txt, f, fill, stroke, sfill)
    if p < 0.25:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * p / 0.25)))
    base.alpha_composite(lay)


def fit(txt, path, size, maxw):
    while size > 20 and text_w(txt, font(path, size)) > maxw:
        size -= 2
    return font(path, size)


def caption_box(base, cx, cy, txt, f, fg, bg, p, emo=None, rot=0):
    """TikTok-style caption: text on a solid rounded box, pops in, optional emoji."""
    if p <= 0:
        return
    tw = text_w(txt, f)
    es = int(f.size * 1.15) if emo else 0
    gap = 16 if emo else 0
    bw, bh = int(tw + es + gap + 64), int(f.size * 1.6)
    lay = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((20, 20, 20 + bw, 20 + bh), radius=22, fill=bg)
    d.text((20 + 32, 20 + bh / 2), txt, font=f, fill=fg, anchor="lm")
    if emo:
        e = emoji(emo, es)
        lay.alpha_composite(e, (int(20 + 32 + tw + gap), int(20 + (bh - e.height) / 2)))
    s = back_out(p)
    lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    lay = lay.resize((max(1, int(lay.width * s)), max(1, int(lay.height * s))), Image.BICUBIC)
    base.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))


def marquee(base, y, txt, f, color, offset, outline=True, alpha=90):
    """Giant repeated text scrolling horizontally behind the car."""
    unit = txt + "  •  "
    uw = text_w(unit, f)
    lay = Image.new("RGBA", (W, int(f.size * 1.4)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x = -(offset % uw) - uw
    while x < W:
        if outline:
            d.text((x, 0), unit, font=f, fill=(0, 0, 0, 0), stroke_width=3,
                   stroke_fill=color + (alpha,))
        else:
            d.text((x, 0), unit, font=f, fill=color + (alpha,))
        x += uw
    base.alpha_composite(lay, (0, int(y)))


# ------------------------------------------------------------------ scenes
def bg_frame(t, accent, grid, glow_strength=1.0):
    base = Image.new("RGBA", (W, H), (8, 8, 12, 255))
    off = int((t * 60) % 120)
    base.alpha_composite(grid, (0, -off))
    # two drifting neon blobs in the accent colour
    blobs = Image.new("RGBA", (W // 4, H // 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(blobs)
    for i, (r, sp, ph) in enumerate([(110, 0.6, 0.0), (80, 0.9, 2.0)]):
        cx = W / 8 + math.sin(t * sp + ph) * 70
        cy = H / 8 + (-60 if i == 0 else 90) + math.cos(t * sp * 0.8 + ph) * 50
        c = accent if i == 0 else tuple(int(v * 0.6) for v in accent[::-1])
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c + (int(110 * glow_strength),))
    blobs = blobs.filter(ImageFilter.GaussianBlur(40)).resize((W, H), Image.BILINEAR)
    base.alpha_composite(blobs)
    return base


def speed_lines(base, t, accent, strength):
    if strength <= 0:
        return
    rnd = random.Random(int(t * 30))
    d = ImageDraw.Draw(base)
    for _ in range(int(26 * strength)):
        y = rnd.uniform(500, 1500)
        x = rnd.uniform(-200, W)
        ln = rnd.uniform(150, 600)
        c = accent if rnd.random() < 0.5 else (255, 255, 255)
        d.line((x, y, x + ln, y), fill=c + (int(rnd.uniform(40, 140) * strength),),
               width=rnd.choice([2, 3, 4]))


def scene_hook(base, t, cars):
    beat = t / BEAT
    # flashing car silhouettes behind the title (quick teaser cuts every half beat)
    k = int(beat * 2) % len(cars)
    if beat < 6:
        car = cars[k]
        sil = car.img.copy()
        sil = sil.resize((int(sil.width * 1.1), int(sil.height * 1.1)))
        a = sil.getchannel("A").point(lambda v: int(v * 0.28))
        sil.putalpha(a)
        base.alpha_composite(sil, (int(W / 2 - sil.width / 2), 1400 - sil.height // 2))

    slam_text(base, W / 2, 560, "2027", F_BLACK_I, 330, (255, 255, 255), p_(t, 0, 0.3),
              start=2.2)
    slam_text(base, W / 2, 790, "SUPER TREASURE", F_BLACK_I, 104, (255, 214, 0),
              p_(t, BEAT * 2, 0.25))
    slam_text(base, W / 2, 900, "HUNTS", F_BLACK_I, 150, (255, 214, 0), p_(t, BEAT * 3, 0.25))
    caption_box(base, W / 2, 1090, "JUST GOT REVEALED", font(F_BLACK, 62), (0, 0, 0),
                (255, 255, 255), p_(t, BEAT * 4, 0.3), emo="👀", rot=-3)
    if t > BEAT * 6:
        f = font(F_XB, 52)
        bounce = 12 * abs(math.sin((t - BEAT * 6) * math.pi / BEAT))
        draw_text_c(base, W / 2, 1640 + bounce, "every one so far ↓", f, (255, 255, 255))


def scene_car(base, t, i, car, side):
    label, name, vibe, emo = CARS[i]
    acc = car.accent
    mystery = label == "MIX J"

    # giant scrolling outline marquee
    marquee(base, 1010, label, font(F_BLACK_I, 230), acc, t * 260 + i * 300, outline=True, alpha=110)
    marquee(base, 380, name, font(F_BLACK_I, 120), (255, 255, 255), -t * 180 - i * 200,
            outline=True, alpha=35)

    # counter chip
    f = font(F_XB, 38)
    caption_box(base, W / 2, 250, f"STH 2027  ·  {i + 1:02d}/{len(CARS):02d}", f, (255, 255, 255),
                (255, 255, 255, 28), 1.0)

    # mix label slam
    slam_text(base, W / 2, 560, label, F_BLACK_I, 210, acc, p_(t, 0, 0.22), stroke=0, start=1.9)

    # car slide-in with motion trail, then float
    pin = expo_out(p_(t, 0.02, 0.32))
    pout = clamp((t - (T_CAR - 0.12)) / 0.12)
    dx = side * (1 - pin) * W * 1.1 - side * pout * W * 1.2
    float_y = 10 * math.sin(t * 3.2)
    cx, cy = W / 2 + dx, 1180 + float_y
    x0, y0 = int(cx - car.img.width / 2), int(cy - car.img.height / 2)

    gp = car.glow_pad
    glow_a = 0.6 + 0.4 * math.sin(t * 6) ** 2
    gl = car.glow
    if glow_a < 1:
        gl = gl.copy()
        gl.putalpha(gl.getchannel("A").point(lambda v: int(v * glow_a)))
    base.alpha_composite(gl, (x0 - gp, y0 - gp))
    base.alpha_composite(car.reflection, (x0, y0 + car.img.height - 6))
    moving = pin < 0.97 or pout > 0
    if moving:
        for k, gh in enumerate(car.ghosts):
            base.alpha_composite(gh, (int(x0 + side * (k + 1) * 70), y0))
    base.alpha_composite(car.img, (x0, y0))

    # name + vibe captions
    nf = fit(name, F_BLACK, 74, W - 120)
    if p_(t, BEAT, 0.01) > 0:
        pn = p_(t, BEAT, 0.18)
        lay = Image.new("RGBA", (W, 160), (0, 0, 0, 0))
        draw_text_c(lay, W / 2, 80, name, nf, (255, 255, 255), stroke=6, sfill=(0, 0, 0))
        yoff = int(30 * (1 - expo_out(pn)))
        if pn < 1:
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * pn)))
        base.alpha_composite(lay, (0, 1430 - 80 + yoff))
    caption_box(base, W / 2, 1580, vibe, font(F_BLACK, 56), (0, 0, 0), acc + (255,),
                p_(t, BEAT * 2, 0.28), emo=emo, rot=(-3 if i % 2 else 3))
    if label == "MIX ?":
        draw_text_c(base, W / 2, 1690, "(mix not confirmed yet)", font(F_XB, 36),
                    (255, 255, 255, 170))
    if mystery and t > BEAT * 2.5:
        draw_text_c(base, W / 2, 1690, "stay tuned...", font(F_XB, 40), (255, 255, 255, 200))
    return pin < 0.6 or pout > 0  # speed-lines hint


def scene_recap(base, t, cars):
    slam_text(base, W / 2, 330, "THE LINE-UP", F_BLACK_I, 140, (255, 255, 255), p_(t, 0, 0.25),
              start=2)
    caption_box(base, W / 2, 470, "(so far)", font(F_BLACK, 50), (0, 0, 0), (255, 214, 0),
                p_(t, BEAT, 0.25), rot=-2)
    tw = 330
    for i, car in enumerate(cars):
        pi_ = p_(t, BEAT * 1.5 + i * BEAT * 0.5, 0.25)
        if pi_ <= 0:
            continue
        r, c = divmod(i, 3)
        cx = 190 + c * 350
        cy = 720 + r * 330
        s = back_out(pi_)
        d = ImageDraw.Draw(base)
        tile_w, tile_h = 330 * s, 300 * s
        d.rounded_rectangle((cx - tile_w / 2, cy - tile_h / 2, cx + tile_w / 2, cy + tile_h / 2),
                            radius=int(26 * s), fill=car.accent + (60,),
                            outline=car.accent + (220,), width=3)
        im = car.img.resize((max(1, int(tw * 0.9 * s)), max(1, int(car.img.height * tw * 0.9 * s / car.img.width))),
                            Image.LANCZOS)
        base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2 - 20 * s)))
        lab = CARS[i][0]
        draw_text_c(base, cx, cy + tile_h / 2 - 40 * s, lab, font(F_BLACK_I, max(10, 40 * s)),
                    (255, 255, 255))


def scene_outro(base, t, cars):
    slam_text(base, W / 2, 620, "which one", F_BLACK_I, 130, (255, 255, 255), p_(t, 0, 0.25))
    slam_text(base, W / 2, 770, "u hunting?", F_BLACK_I, 130, (255, 214, 0), p_(t, BEAT, 0.25))
    caption_box(base, W / 2, 960, "comment ur pick", font(F_BLACK, 60), (0, 0, 0),
                (255, 255, 255), p_(t, BEAT * 2, 0.3), emo="👇", rot=-3)
    caption_box(base, W / 2, 1110, "follow for more drops", font(F_BLACK, 52), (255, 255, 255),
                (255, 40, 90), p_(t, BEAT * 3.5, 0.3), emo="🔥", rot=2)
    # cars parade along the bottom
    small = [c.img.resize((300, int(c.img.height * 300 / c.img.width)), Image.LANCZOS) for c in cars[:8]]
    x = W - (t * 700) % (len(small) * 340) - 340
    for k in range(len(small) * 2):
        im = small[k % len(small)]
        xx = x + k * 340
        if -340 < xx < W:
            base.alpha_composite(im, (int(xx), 1430 - im.height // 2))
    draw_text_c(base, W / 2, 1720, "pics: @your.choice_hotwheels", font(F_XB, 30),
                (255, 255, 255, 140))


# ------------------------------------------------------------------ post FX
def rgb_split(arr, amt):
    if amt < 1:
        return arr
    out = arr.copy()
    out[:, amt:, 0] = arr[:, :-amt, 0]
    out[:, :-amt, 2] = arr[:, amt:, 2]
    return out


def glitch_slices(arr, t, strength):
    if strength <= 0:
        return arr
    rnd = random.Random(int(t * 1000))
    out = arr.copy()
    for _ in range(int(8 * strength)):
        y = rnd.randint(0, H - 60)
        h = rnd.randint(10, 60)
        s = rnd.randint(-80, 80)
        out[y:y + h] = np.roll(arr[y:y + h], s, axis=1)
    return out


def zoom(img, s, shake=(0, 0)):
    if s <= 1.0005 and shake == (0, 0):
        return img
    w2, h2 = int(W * s), int(H * s)
    big = img.resize((w2, h2), Image.BILINEAR)
    x0 = (w2 - W) // 2 + int(shake[0])
    y0 = (h2 - H) // 2 + int(shake[1])
    x0 = max(0, min(w2 - W, x0))
    y0 = max(0, min(h2 - H, y0))
    return big.crop((x0, y0, x0 + W, y0 + H))


# ------------------------------------------------------------------ audio
def synth_audio(path):
    sr = 44100
    n = int(TOTAL * sr) + sr
    mix = np.zeros(n)
    rng = np.random.default_rng(5)

    def add(sig, at, g=1.0):
        i = int(at * sr)
        if i >= n:
            return
        j = min(n, i + len(sig))
        mix[i:j] += sig[: j - i] * g

    def env_exp(m, k):
        return np.exp(-np.arange(m) / sr * k)

    def kick():
        m = int(0.35 * sr)
        tt = np.arange(m) / sr
        f = 50 + 120 * np.exp(-tt * 35)
        ph = 2 * np.pi * np.cumsum(f) / sr
        return np.sin(ph) * env_exp(m, 9) * 1.0

    def clap():
        m = int(0.25 * sr)
        nz = rng.standard_normal(m)
        nz = nz - np.convolve(nz, np.ones(8) / 8, "same")
        e = env_exp(m, 22)
        for d in (0.0, 0.012, 0.024):
            k = int(d * sr)
            e[k:] += env_exp(m - k, 60) * 0.6
        return nz * e * 0.45

    def hat(open_=False):
        m = int((0.18 if open_ else 0.05) * sr)
        nz = rng.standard_normal(m)
        nz = nz - np.convolve(nz, np.ones(3) / 3, "same")
        return nz * env_exp(m, 18 if open_ else 80) * 0.18

    def bass(freq, dur, glide_to=None):
        m = int(dur * sr)
        tt = np.arange(m) / sr
        f = np.full(m, freq) if glide_to is None else freq + (glide_to - freq) * np.clip(tt / 0.08, 0, 1)
        ph = 2 * np.pi * np.cumsum(f) / sr
        s = np.sin(ph) + 0.25 * np.sin(2 * ph)
        s = np.tanh(s * 1.8)
        e = np.minimum(1, tt / 0.005) * np.exp(-tt * 1.2)
        return s * e * 0.55

    def impact():
        m = int(1.2 * sr)
        tt = np.arange(m) / sr
        f = 40 + 80 * np.exp(-tt * 6)
        boom = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 3)
        nz = rng.standard_normal(m) * np.exp(-tt * 14) * 0.4
        return (boom + nz) * 0.8

    def riser(dur):
        m = int(dur * sr)
        tt = np.arange(m) / sr
        nz = rng.standard_normal(m)
        nz = nz - np.convolve(nz, np.ones(4) / 4, "same")
        sweep = np.sin(2 * np.pi * np.cumsum(300 + 2500 * (tt / dur) ** 2) / sr) * 0.3
        return (nz * 0.25 + sweep) * (tt / dur) ** 2 * 0.5

    def stab(freqs, dur=0.3):
        m = int(dur * sr)
        tt = np.arange(m) / sr
        s = sum(np.sign(np.sin(2 * np.pi * f * tt)) * 0.3 + np.sin(2 * np.pi * f * tt) for f in freqs)
        return s * np.exp(-tt * 9) * 0.08

    # minor-key 808 line (A minor-ish), one note per bar
    roots = [55.0, 55.0, 43.65, 49.0]  # A1 A1 F1 G1
    nbeats = int(TOTAL / BEAT) + 1
    drop = HOOK_BEATS  # full beat starts after the hook
    for b in range(nbeats):
        at = b * BEAT
        bar, pos = divmod(b, 4)
        root = roots[bar % 4]
        if b < drop:
            # sparse hook: kicks on slams, hats building
            if b in (0, 2, 3, 4):
                add(kick(), at)
            add(hat(), at + BEAT / 2)
            if b >= 4:
                add(hat(), at)
                add(hat(), at + BEAT / 4)
                add(hat(), at + 3 * BEAT / 4)
            continue
        if b >= nbeats - 2:
            continue
        # drums
        if pos == 0:
            add(kick(), at)
        if pos == 2:
            add(kick(), at + BEAT / 2)
        if pos in (1, 3):
            add(clap(), at)
        for s in range(2):
            add(hat(), at + s * BEAT / 2)
        if pos == 3 and bar % 2:
            for s in range(4):  # hat roll
                add(hat(), at + BEAT / 2 + s * BEAT / 8, 0.8)
        if pos == 2 and bar % 2 == 0:
            add(hat(True), at + BEAT / 2)
        # 808
        if pos == 0:
            add(bass(root, BEAT * 1.9), at)
        if pos == 2:
            add(bass(root * 1.5, BEAT * 0.9, glide_to=root), at + BEAT / 2)
        # chord stab
        if pos == 0:
            add(stab([root * 8, root * 8 * 1.189, root * 8 * 1.498]), at)

    add(riser(T_HOOK - 0.1), 0.05)
    for i in range(len(CARS)):
        add(impact(), T_HOOK + i * T_CAR, 0.7 if i else 1.0)
    add(impact(), T_HOOK + T_CARS, 0.8)
    add(impact(), T_HOOK + T_CARS + T_RECAP, 0.8)

    mix = mix[: int(TOTAL * sr)]
    mix = np.tanh(mix * 1.1)
    mix = mix / np.abs(mix).max() * 0.9
    fade = int(0.6 * sr)
    mix[-fade:] *= np.linspace(1, 0, fade)
    pcm = (mix * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


# ------------------------------------------------------------------ main
def render_frame(t, cars, grid, vignette, grain, fi):
    hook_acc = (255, 40, 90)
    in_cars = T_HOOK <= t < T_HOOK + T_CARS
    if t < T_HOOK:
        acc, lt = hook_acc, t
    elif in_cars:
        k = int((t - T_HOOK) // T_CAR)
        acc, lt = cars[k].accent, t - T_HOOK - k * T_CAR
    elif t < T_HOOK + T_CARS + T_RECAP:
        acc, lt = (255, 214, 0), t - T_HOOK - T_CARS
    else:
        acc, lt = hook_acc, t - T_HOOK - T_CARS - T_RECAP

    frame = bg_frame(t, acc, grid)
    sl = 0.0
    if t < T_HOOK:
        scene_hook(frame, lt, cars)
    elif in_cars:
        side = 1 if k % 2 == 0 else -1
        fast = scene_car(frame, lt, k, cars[k], side)
        sl = 1.0 if fast else 0.25
    elif t < T_HOOK + T_CARS + T_RECAP:
        scene_recap(frame, lt, cars)
    else:
        scene_outro(frame, lt, cars)
    speed_lines(frame, t, acc, sl)

    # beat-synced camera: zoom punch on every beat, shake on section hits
    bp = (t % BEAT) / BEAT
    punch = 1 + 0.045 * math.exp(-bp * 7)
    hit_times = [0, BEAT * 2, BEAT * 3, BEAT * 4] + [T_HOOK + i * T_CAR for i in range(len(CARS))] \
        + [T_HOOK + T_CARS, T_HOOK + T_CARS + T_RECAP]
    since = min((t - h for h in hit_times if t >= h), default=9)
    shake_amt = 26 * math.exp(-since * 14) if since < 0.4 else 0
    rnd = random.Random(fi)
    shake = (rnd.uniform(-1, 1) * shake_amt, rnd.uniform(-1, 1) * shake_amt)
    frame = zoom(frame.convert("RGB"), punch + (0.06 * math.exp(-since * 10) if since < 0.4 else 0), shake)

    arr = np.asarray(frame).astype(np.float32)
    # flash on hits
    if since < 0.12:
        a = (1 - since / 0.12) * 0.75
        arr = arr * (1 - a) + 255 * a
    arr = arr * vignette + grain[fi % len(grain)]
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    if since < 0.15:
        arr = rgb_split(arr, int(18 * (1 - since / 0.15)))
        arr = glitch_slices(arr, t, 1 - since / 0.15)
    return arr


def main(cars_dir, out):
    cars = [Car(f"{cars_dir}/sth{i}.png") for i in range(len(CARS))]
    grid, vignette, grain = make_grid(), make_vignette(), make_grain()
    wav = out.rsplit(".", 1)[0] + "_beat.wav"
    synth_audio(wav)
    nframes = int(TOTAL * FPS)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
         "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE)
    for fi in range(nframes):
        ff.stdin.write(render_frame(fi / FPS, cars, grid, vignette, grain, fi).tobytes())
    ff.stdin.close()
    ff.wait()
    print(f"wrote {out}: {TOTAL:.1f}s, {nframes} frames")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
