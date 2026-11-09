"""
Bhai Dooj special reel: "2027 Super Treasure Hunts - revealed so far".

Builds a 1080x1920 (Instagram Reel) MP4 from the line-up image:
  festive intro -> one reveal per car -> recap grid -> outro.
Frames are drawn with Pillow and piped straight into ffmpeg, with a small
synthesized whoosh/chime sound track.

Usage:
    python sth_reveal_video.py <lineup_image.jpg> <output.mp4>
"""

import math
import random
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
FONT_DIR = "/usr/share/fonts/opentype/inter/"
F_BLACK = FONT_DIR + "Inter-Black.otf"
F_XBOLD = FONT_DIR + "Inter-ExtraBold.otf"
F_BOLD = FONT_DIR + "Inter-Bold.otf"

GOLD = (255, 200, 60)
SAFFRON = (255, 140, 20)
CREAM = (255, 244, 220)
WHITE = (255, 255, 255)

# (label, car name, column, row) - positions in the 3x3 grid of the source image
CARS = [
    ("MIX A", "'64 Lincoln Continental", 0, 0),
    ("MIX B", "BMW M4 GT3", 1, 0),
    ("MIX C", "Dodge D100", 2, 0),
    ("MIX D", "'88 Mitsubishi Starion", 0, 1),
    ("MIX E", "Aston Martin DB5 Safari Edition", 1, 1),
    ("MIX F", "Ferrari 12Cilindri", 2, 1),
    ("MIX ?", "Porsche 911 Carrera T", 0, 2),
    ("MIX ?", "1967 Shelby GT-500", 1, 2),
    ("MIX J", "Still under wraps...", 2, 2),
]
CELL_X = [(28, 403), (418, 793), (808, 1182)]
CELL_Y = [(205, 400), (412, 602), (620, 806)]

INTRO, PER_CAR, RECAP, OUTRO = 3.6, 2.1, 3.6, 3.4

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_back(t):
    t = clamp(t)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def prog(t, start, dur):
    return clamp((t - start) / dur)


# ---------------------------------------------------------------- assets
def load_cars(path):
    src = Image.open(path).convert("RGB")
    cars = []
    for label, name, c, r in CARS:
        x0, x1 = CELL_X[c]
        y0, y1 = CELL_Y[r]
        # trim the printed "Mix" label (top) and name (bottom); we draw our own
        cars.append(src.crop((x0 + 4, y0 + 38, x1 - 4, y1 - 34)))
    cells = [src.crop((CELL_X[c][0], CELL_Y[r][0], CELL_X[c][1], CELL_Y[r][1]))
             for _, _, c, r in CARS]
    return cars, cells


def make_background():
    """Deep maroon -> saffron vertical gradient with a soft centre glow."""
    y = np.linspace(0, 1, H)[:, None]
    top = np.array([60, 6, 22])
    mid = np.array([140, 22, 30])
    bot = np.array([215, 85, 10])
    col = np.where(y < 0.55, top + (mid - top) * (y / 0.55),
                   mid + (bot - mid) * ((y - 0.55) / 0.45))
    img = np.repeat(col[:, None, :], W, axis=1).reshape(H, W, 3)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.45) / H) ** 2)
    glow = np.clip(1 - d * 2.2, 0, 1)[..., None] * np.array([90, 50, 10])
    img = np.clip(img + glow, 0, 255).astype(np.uint8)
    bg = Image.fromarray(img, "RGB")

    # faint rangoli-style mandala in the middle
    m = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(m)
    cx, cy = W // 2, int(H * 0.47)
    for ring, (rad, petals) in enumerate([(430, 24), (340, 16), (250, 12)]):
        for k in range(petals):
            a = 2 * math.pi * k / petals
            px, py = cx + rad * math.cos(a), cy + rad * math.sin(a)
            s = 46 - ring * 8
            md.ellipse((px - s, py - s, px + s, py + s), outline=(255, 210, 120, 28), width=4)
        md.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), outline=(255, 210, 120, 22), width=3)
    bg.paste(m, (0, 0), m)
    return bg


def draw_garland(d, t):
    """Marigold toran across the top with hanging strands."""
    for i in range(-1, 24):
        x = i * 48 + 24
        sag = 70 + 30 * math.sin(i / 23 * math.pi)
        y = sag * 0.35
        c = SAFFRON if i % 2 else GOLD
        d.ellipse((x - 26, y - 26 + 10, x + 26, y + 26 + 10), fill=c)
    for i in range(1, 11):
        x = i * W / 11
        sway = 6 * math.sin(t * 2 + i)
        n = 4 + (i % 3)
        for k in range(n):
            y = 60 + k * 40
            c = GOLD if (k + i) % 2 else SAFFRON
            d.ellipse((x + sway * k / n - 17, y - 17, x + sway * k / n + 17, y + 17), fill=c)
        d.polygon([(x + sway - 10, 60 + n * 40), (x + sway + 10, 60 + n * 40),
                   (x + sway, 60 + n * 40 + 24)], fill=(40, 150, 60))


def draw_diyas(base, t):
    """Row of glowing clay lamps along the bottom."""
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    xs = [140, 400, 680, 940]
    y = H - 120
    for i, x in enumerate(xs):
        flick = 1 + 0.12 * math.sin(t * 13 + i * 2.1) + 0.06 * math.sin(t * 29 + i)
        r = 90 * flick
        gd.ellipse((x - r, y - 60 - r, x + r, y - 60 + r), fill=(255, 170, 40, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    base.paste(glow, (0, 0), glow)
    d = ImageDraw.Draw(base)
    for i, x in enumerate(xs):
        flick = 1 + 0.15 * math.sin(t * 13 + i * 2.1)
        d.chord((x - 75, y - 50, x + 75, y + 60), 0, 180, fill=(170, 70, 25))
        d.ellipse((x - 75, y - 8, x + 75, y + 12), fill=(120, 45, 15))
        fh = 52 * flick
        d.polygon([(x - 14, y - 4), (x + 14, y - 4), (x + 3 * math.sin(t * 9 + i), y - 4 - fh)],
                  fill=(255, 190, 40))
        d.polygon([(x - 7, y - 4), (x + 7, y - 4), (x + 2 * math.sin(t * 9 + i), y - 4 - fh * 0.55)],
                  fill=(255, 250, 200))


class Sparkles:
    def __init__(self, n=70, seed=7):
        rnd = random.Random(seed)
        self.p = [(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(20, 70),
                   rnd.uniform(2, 6), rnd.uniform(0, 6.28)) for _ in range(n)]

    def draw(self, d, t):
        for x, y, speed, size, ph in self.p:
            yy = (y - speed * t) % H
            tw = 0.5 + 0.5 * math.sin(t * 4 + ph)
            s = size * (0.6 + 0.6 * tw)
            a = int(120 + 135 * tw)
            d.ellipse((x - s, yy - s, x + s, yy + s), fill=(255, 225, 140, a))


# ---------------------------------------------------------------- text helpers
def text_center(d, cx, y, txt, f, fill, stroke=0, stroke_fill=(0, 0, 0)):
    w = d.textlength(txt, font=f)
    d.text((cx - w / 2, y), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)


def fit_font(d, txt, path, size, max_w):
    while size > 20 and d.textlength(txt, font=font(path, size)) > max_w:
        size -= 2
    return font(path, size)


def pop_text(base, cx, cy, txt, path, size, fill, p, stroke=0, stroke_fill=(0, 0, 0), alpha=1.0):
    """Draw text centred at (cx, cy) scaled by an overshoot pop factor p (0..1)."""
    if p <= 0 or alpha <= 0:
        return
    scale = ease_back(p)
    f = font(path, max(8, int(size * scale)))
    tmp = Image.new("RGBA", (W, int(size * 2.2)), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    text_center(td, W / 2, size * 0.3, txt, f, fill, stroke, stroke_fill)
    if alpha < 1:
        tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * alpha)))
    base.paste(tmp, (int(cx - W / 2), int(cy - size * 0.3 - f.size * 0.55)), tmp)


def pill(d, cx, y, txt, f, bg, fg, pad=(34, 16)):
    w = d.textlength(txt, font=f)
    box = (cx - w / 2 - pad[0], y, cx + w / 2 + pad[0], y + f.size + pad[1] * 2)
    d.rounded_rectangle(box, radius=(box[3] - box[1]) // 2, fill=bg)
    d.text((cx - w / 2, y + pad[1] - f.size * 0.08), txt, font=f, fill=fg)


def card(car_img, width, label_color=GOLD):
    """White rounded card holding the car photo, with a gold border."""
    ratio = car_img.height / car_img.width
    inner_w = width - 40
    inner_h = int(inner_w * ratio)
    c = Image.new("RGBA", (width, inner_h + 40), (0, 0, 0, 0))
    cd = ImageDraw.Draw(c)
    cd.rounded_rectangle((0, 0, width - 1, inner_h + 39), radius=36, fill=label_color)
    cd.rounded_rectangle((8, 8, width - 9, inner_h + 31), radius=30, fill=(250, 250, 252))
    photo = car_img.resize((inner_w, inner_h), Image.LANCZOS)
    mask = Image.new("L", photo.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, inner_w - 1, inner_h - 1), radius=24, fill=255)
    c.paste(photo, (20, 20), mask)
    return c


def shine(card_img, p):
    """Diagonal light sweep across a card, p in 0..1."""
    if p <= 0 or p >= 1:
        return card_img
    w, h = card_img.size
    band = Image.new("L", (w, h), 0)
    bd = ImageDraw.Draw(band)
    x = -w * 0.4 + p * w * 1.8
    bd.polygon([(x, 0), (x + 90, 0), (x - 160, h), (x - 250, h)], fill=150)
    band = band.filter(ImageFilter.GaussianBlur(18))
    band = Image.composite(band, Image.new("L", (w, h), 0), card_img.getchannel("A"))
    out = card_img.copy()
    out.paste(Image.new("RGBA", (w, h), (255, 255, 255, 255)), (0, 0), band)
    return out


# ---------------------------------------------------------------- scenes
def scene_intro(base, t):
    d = ImageDraw.Draw(base)
    pop_text(base, W / 2, 470, "HAPPY BHAI DOOJ", F_XBOLD, 74, GOLD, prog(t, 0.1, 0.45),
             stroke=3, stroke_fill=(90, 20, 10))
    p = prog(t, 0.4, 0.5)
    if p > 0:
        a = ease_out(p)
        f = font(F_BOLD, 46)
        txt = "Gift ideas for your bhai..."
        tmp = Image.new("RGBA", (W, 80), (0, 0, 0, 0))
        text_center(ImageDraw.Draw(tmp), W / 2, 10, txt, f, CREAM)
        tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * a)))
        base.paste(tmp, (0, int(580 + 30 * (1 - a))), tmp)
    pop_text(base, W / 2, 820, "2027", F_BLACK, 300, WHITE, prog(t, 0.9, 0.5),
             stroke=8, stroke_fill=(150, 20, 20))
    pop_text(base, W / 2, 1040, "SUPER", F_BLACK, 130, GOLD, prog(t, 1.3, 0.45),
             stroke=5, stroke_fill=(90, 20, 10))
    pop_text(base, W / 2, 1180, "TREASURE HUNTS", F_BLACK, 104, GOLD, prog(t, 1.55, 0.45),
             stroke=5, stroke_fill=(90, 20, 10))
    p = prog(t, 2.1, 0.4)
    if p > 0:
        d = ImageDraw.Draw(base)
        f = font(F_BLACK, 54)
        y = 1320 + 40 * (1 - ease_back(p))
        pill(d, W / 2, y, "REVEALED SO FAR", f, (255, 255, 255), (170, 25, 30))


def scene_car(base, t, idx, car_img):
    label, name, _, _ = CARS[idx]
    mystery = label == "MIX J"
    d = ImageDraw.Draw(base)

    # counter
    f = font(F_XBOLD, 40)
    pill(d, W / 2, 330, f"{idx + 1} / {len(CARS)}", f, (0, 0, 0, 110), CREAM, pad=(28, 12))

    # big mix label pops in
    pop_text(base, W / 2, 560, label, F_BLACK, 190, GOLD, prog(t, 0.0, 0.35),
             stroke=7, stroke_fill=(110, 15, 15))

    # card slides in from the right, sways gently, shine sweeps across
    cw = 980
    c = card(car_img, cw, GOLD if not mystery else (120, 160, 255))
    c = shine(c, prog(t, 0.55, 0.6))
    p = ease_out(prog(t, 0.15, 0.45))
    out = ease_out(prog(t, PER_CAR - 0.25, 0.25))
    x = (W - cw) / 2 + (1 - p) * W - out * W
    y = 800 - c.height / 2 + 140 + 8 * math.sin(t * 3)
    # drop shadow
    sh = Image.new("RGBA", (c.width + 80, c.height + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 50, c.width + 40, c.height + 50), radius=40,
                                         fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    base.paste(sh, (int(x - 40), int(y - 40)), sh)
    base.paste(c, (int(x), int(y)), c)

    # car name slides up
    p = ease_out(prog(t, 0.6, 0.4))
    if p > 0:
        d = ImageDraw.Draw(base)
        txt = name if not mystery else "Coming soon..."
        f = fit_font(d, txt, F_BLACK, 78, W - 100)
        tmp = Image.new("RGBA", (W, 130), (0, 0, 0, 0))
        text_center(ImageDraw.Draw(tmp), W / 2, 15, txt, f, WHITE, 4, (90, 15, 10))
        tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * p)))
        base.paste(tmp, (0, int(y + c.height + 60 + 40 * (1 - p))), tmp)
        if mystery:
            f2 = font(F_BOLD, 44)
            tmp = Image.new("RGBA", (W, 80), (0, 0, 0, 0))
            text_center(ImageDraw.Draw(tmp), W / 2, 10, "Still under wraps", f2, CREAM)
            tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * p)))
            base.paste(tmp, (0, int(y + c.height + 170)), tmp)
        elif label == "MIX ?":
            f2 = font(F_BOLD, 40)
            tmp = Image.new("RGBA", (W, 80), (0, 0, 0, 0))
            text_center(ImageDraw.Draw(tmp), W / 2, 10, "Mix not confirmed yet", f2, CREAM)
            tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * p)))
            base.paste(tmp, (0, int(y + c.height + 170)), tmp)


def scene_recap(base, t, cells):
    pop_text(base, W / 2, 360, "THE LINE-UP", F_BLACK, 120, GOLD, prog(t, 0.0, 0.4),
             stroke=5, stroke_fill=(90, 20, 10))
    pop_text(base, W / 2, 480, "(so far)", F_XBOLD, 60, CREAM, prog(t, 0.2, 0.4))
    tw, gap = 330, 18
    th = int(tw * cells[0].height / cells[0].width)
    x0 = (W - (tw * 3 + gap * 2)) / 2
    y0 = 620
    for i, cell in enumerate(cells):
        p = prog(t, 0.35 + i * 0.12, 0.35)
        if p <= 0:
            continue
        s = ease_back(p)
        w_, h_ = max(1, int(tw * s)), max(1, int(th * s))
        tile = cell.resize((w_, h_), Image.LANCZOS)
        r, c = divmod(i, 3)
        cx = x0 + c * (tw + gap) + tw / 2
        cy = y0 + r * (th + gap) + th / 2
        d = ImageDraw.Draw(base)
        d.rounded_rectangle((cx - w_ / 2 - 6, cy - h_ / 2 - 6, cx + w_ / 2 + 6, cy + h_ / 2 + 6),
                            radius=14, fill=GOLD)
        base.paste(tile, (int(cx - w_ / 2), int(cy - h_ / 2)))


def scene_outro(base, t):
    pop_text(base, W / 2, 620, "Which one is", F_BLACK, 104, WHITE, prog(t, 0.0, 0.4),
             stroke=4, stroke_fill=(90, 15, 10))
    pop_text(base, W / 2, 750, "your bhai getting?", F_BLACK, 92, WHITE, prog(t, 0.15, 0.4),
             stroke=4, stroke_fill=(90, 15, 10))
    p = prog(t, 0.6, 0.4)
    if p > 0:
        d = ImageDraw.Draw(base)
        pill(d, W / 2, 900 + 40 * (1 - ease_back(p)), "COMMENT YOUR FAVOURITE",
             font(F_BLACK, 50), GOLD, (110, 15, 15))
    pop_text(base, W / 2, 1160, "Happy Bhai Dooj", F_BLACK, 116, GOLD, prog(t, 1.0, 0.5),
             stroke=5, stroke_fill=(90, 20, 10))
    p = prog(t, 1.5, 0.5)
    if p > 0:
        f = font(F_BOLD, 34)
        tmp = Image.new("RGBA", (W, 70), (0, 0, 0, 0))
        text_center(ImageDraw.Draw(tmp), W / 2, 10, "Line-up image: @your.choice_hotwheels", f, CREAM)
        tmp.putalpha(tmp.getchannel("A").point(lambda v: int(v * p * 0.85)))
        base.paste(tmp, (0, 1420), tmp)


# ---------------------------------------------------------------- audio
def write_audio(path, total):
    sr = 44100
    n = int(total * sr)
    audio = np.zeros(n)
    rng = np.random.default_rng(1)

    def add(sig, at):
        i = int(at * sr)
        j = min(n, i + len(sig))
        audio[i:j] += sig[: j - i]

    def whoosh(dur=0.45):
        m = int(dur * sr)
        noise = rng.standard_normal(m)
        env = np.sin(np.linspace(0, np.pi, m)) ** 2
        # crude band-pass sweep: moving-average smoothing of varying width
        out = np.convolve(noise, np.ones(12) / 12, mode="same") - np.convolve(noise, np.ones(60) / 60, mode="same")
        return out * env * 0.35

    def chime(freq=1318.5, dur=0.9):
        m = int(dur * sr)
        tt = np.arange(m) / sr
        env = np.exp(-tt * 5)
        return (np.sin(2 * np.pi * freq * tt) + 0.5 * np.sin(2 * np.pi * freq * 2.01 * tt)
                + 0.25 * np.sin(2 * np.pi * freq * 3.03 * tt)) * env * 0.18

    def bell(freq=880, dur=1.6):
        m = int(dur * sr)
        tt = np.arange(m) / sr
        env = np.exp(-tt * 2.5)
        return (np.sin(2 * np.pi * freq * tt) + 0.6 * np.sin(2 * np.pi * freq * 2.76 * tt)) * env * 0.22

    add(bell(660), 0.1)
    add(bell(990), 0.9)
    notes = [1046.5, 1174.7, 1318.5, 1396.9, 1568.0, 1760.0, 1975.5, 2093.0, 2349.3]
    for i in range(len(CARS)):
        st = INTRO + i * PER_CAR
        add(whoosh(), st + 0.1)
        add(chime(notes[i]), st + 0.6)
    st = INTRO + len(CARS) * PER_CAR
    for i in range(9):
        add(chime(notes[i], 0.4) * 0.6, st + 0.35 + i * 0.12)
    add(bell(660), st + RECAP + 1.0)
    add(bell(880), st + RECAP + 1.05)

    audio = audio / max(1e-9, np.abs(audio).max()) * 0.8
    pcm = (audio * 32767).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


# ---------------------------------------------------------------- main
def main(src, out):
    cars, cells = load_cars(src)
    bg = make_background()
    sparkles = Sparkles()
    total = INTRO + PER_CAR * len(CARS) + RECAP + OUTRO
    nframes = int(total * FPS)

    wav = out.rsplit(".", 1)[0] + "_sfx.wav"
    write_audio(wav, total)

    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", wav,
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE)

    for fi in range(nframes):
        t = fi / FPS
        frame = bg.copy().convert("RGBA")
        over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sparkles.draw(ImageDraw.Draw(over), t)
        frame.alpha_composite(over)
        draw_diyas(frame, t)
        draw_garland(ImageDraw.Draw(frame), t)

        if t < INTRO:
            scene_intro(frame, t)
        elif t < INTRO + PER_CAR * len(CARS):
            k = int((t - INTRO) // PER_CAR)
            scene_car(frame, t - INTRO - k * PER_CAR, k, cars[k])
        elif t < INTRO + PER_CAR * len(CARS) + RECAP:
            scene_recap(frame, t - INTRO - PER_CAR * len(CARS), cells)
        else:
            scene_outro(frame, t - INTRO - PER_CAR * len(CARS) - RECAP)

        ff.stdin.write(frame.convert("RGB").tobytes())
    ff.stdin.close()
    ff.wait()
    print(f"wrote {out} ({total:.1f}s, {nframes} frames)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
