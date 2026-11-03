"""
Bhai Dooj gift reel generator (Instagram Reel / YouTube Short, 1080x1920, 30fps).

Usage:
    python make_reel.py              # writes bhai_dooj_reel.mp4 next to this file
    python make_reel.py --no-music   # silent version (add trending audio in Instagram)

Needs: Pillow, numpy, ffmpeg on PATH.
"""
import argparse
import math
import os
import random
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")
_font_cache = {}


def font(size, bold=True):
    size = max(1, int(size))
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(BOLD if bold else REG, size)
    return _font_cache[key]


# ---------------------------------------------------------------- products
PRODUCTS = [
    dict(line1="Hot Wheels", line2="FERRARI", tag="RLC",
         sub="Red Line Club Exclusive", body=(210, 20, 30), accent=(255, 215, 0)),
    dict(line1="Original Hot Wheels", line2="MUSTANG", tag="RLC",
         sub="Blue  |  Red Line Club", body=(25, 90, 220), accent=(255, 255, 255)),
    dict(line1="Hot Wheels Premium", line2="NISSAN GT-R", tag="PREMIUM",
         sub='"Godzilla"', body=(150, 155, 165), accent=(230, 30, 40)),
    dict(line1="Hot Wheels", line2="TFOX", tag="HOT PICK",
         sub="Collector's Choice", body=(255, 120, 0), accent=(20, 20, 20)),
    dict(line1="Hot Wheels", line2="BRIAN O'CONNER", tag="SET",
         sub="Fast & Furious Tribute Set", body=(255, 110, 0),
         body2=(30, 110, 230), accent=(255, 255, 255), pair=True),
]

INTRO_S, CAR_S, OUTRO_S = 3.5, 3.0, 4.0
TOTAL_S = INTRO_S + CAR_S * len(PRODUCTS) + OUTRO_S

random.seed(7)
SPARKS = [(random.random() * W, random.random() * H, random.uniform(1.5, 4.5),
           random.random() * 6.28) for _ in range(90)]


# ---------------------------------------------------------------- helpers
def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ease_back(t):
    t = max(0.0, min(1.0, t))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def make_background(top, bottom):
    grad = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(top)[None, None, :] * (1 - grad) +
           np.array(bottom)[None, None, :] * grad)
    arr = np.repeat(arr, W, axis=1).astype(np.uint8)
    img = Image.fromarray(arr, "RGB")
    # warm festive glow in the middle
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse((-200, 500, W + 200, 1500), fill=110)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    img = Image.composite(Image.new("RGB", (W, H), (255, 140, 30)), img, glow)
    return img


BG = make_background((25, 4, 40), (60, 8, 20))


def draw_sparkles(d, t):
    for x, y, r, ph in SPARKS:
        a = 0.5 + 0.5 * math.sin(t * 4 + ph)
        yy = (y - t * 40 * r) % H
        c = (255, int(200 + 55 * a), int(80 + 120 * a))
        rr = r * (0.4 + a)
        d.ellipse((x - rr, yy - rr, x + rr, yy + rr), fill=c)


def draw_diya(d, cx, cy, t, s=1.0):
    # clay lamp
    d.chord((cx - 70 * s, cy - 40 * s, cx + 70 * s, cy + 50 * s), 0, 180,
            fill=(190, 80, 20), outline=(255, 190, 60), width=int(4 * s))
    d.rectangle((cx - 70 * s, cy + 3 * s, cx + 70 * s, cy + 10 * s), fill=(255, 190, 60))
    # flickering flame
    f = 1 + 0.12 * math.sin(t * 17 + cx)
    d.ellipse((cx - 30 * s * f, cy - 85 * s * f, cx + 30 * s * f, cy - 5 * s),
              fill=(255, 150, 20))
    d.ellipse((cx - 16 * s * f, cy - 65 * s * f, cx + 16 * s * f, cy - 5 * s),
              fill=(255, 240, 150))


def text_c(d, y, txt, size, fill, bold=True, stroke=0, stroke_fill=(0, 0, 0), x=None):
    f = font(size, bold)
    w = d.textlength(txt, font=f)
    cx = W / 2 if x is None else x
    d.text((cx - w / 2, y), txt, font=f, fill=fill,
           stroke_width=stroke, stroke_fill=stroke_fill)


def fit_size(d, txt, max_w, start):
    s = start
    while s > 30 and d.textlength(txt, font=font(s)) > max_w:
        s -= 4
    return s


def draw_wheel(d, cx, cy, r, ang):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(15, 15, 15))
    ri = r * 0.62
    d.ellipse((cx - ri, cy - ri, cx + ri, cy + ri), fill=(200, 200, 210))
    for k in range(5):
        a = ang + k * 2 * math.pi / 5
        d.line((cx, cy, cx + ri * math.cos(a), cy + ri * math.sin(a)),
               fill=(90, 90, 100), width=max(3, int(r * 0.14)))
    rc = r * 0.16
    d.ellipse((cx - rc, cy - rc, cx + rc, cy + rc), fill=(230, 30, 30))


def draw_car(d, x, y, scale, body, accent, wheel_ang, facing=1):
    """Generic stylised sports-car silhouette. (x, y) = rear-bottom-left anchor."""
    def P(px, py):
        return (x + (px if facing == 1 else 600 - px) * scale, y + py * scale)

    shadow = [P(20, 175), P(580, 175), P(560, 195), P(40, 195)]
    d.polygon(shadow, fill=(0, 0, 0))
    body_pts = [(10, 150), (15, 105), (60, 92), (170, 85), (240, 40), (330, 32),
                (400, 70), (540, 92), (590, 115), (595, 150), (520, 160), (90, 160)]
    d.polygon([P(*p) for p in body_pts], fill=body, outline=(20, 20, 20))
    dark = tuple(int(c * 0.6) for c in body)
    d.polygon([P(*p) for p in [(15, 128), (590, 132), (595, 150), (520, 160),
                                (90, 160), (10, 150)]], fill=dark)
    # windows
    d.polygon([P(*p) for p in [(195, 85), (250, 50), (320, 45), (320, 85)]],
              fill=(40, 60, 90))
    d.polygon([P(*p) for p in [(335, 45), (390, 74), (395, 85), (335, 85)]],
              fill=(40, 60, 90))
    # racing stripe
    d.line([P(60, 112), P(560, 112)], fill=accent, width=max(4, int(10 * scale)))
    # lights
    d.polygon([P(*p) for p in [(560, 100), (592, 115), (580, 122), (555, 112)]],
              fill=(255, 250, 200))
    d.polygon([P(*p) for p in [(12, 108), (40, 100), (40, 115), (14, 120)]],
              fill=(255, 30, 30))
    r = 52 * scale
    for wx in (130, 470):
        cx, cy = P(wx, 160)
        draw_wheel(d, cx, cy, r, wheel_ang * facing)


def speed_lines(d, t, y0, y1, color=(255, 255, 255)):
    rnd = random.Random(int(t * 12))
    for _ in range(14):
        yy = rnd.uniform(y0, y1)
        xx = rnd.uniform(-200, W)
        ln = rnd.uniform(120, 380)
        d.line((xx, yy, xx + ln, yy), fill=color, width=rnd.choice([2, 3, 4]))


def badge(d, cx, cy, txt, t_local):
    s = ease_back(t_local / 0.4)
    if s <= 0:
        return
    f = font(int(64 * s))
    w = d.textlength(txt, font=f)
    pad = 36 * s
    d.rounded_rectangle((cx - w / 2 - pad, cy - 50 * s, cx + w / 2 + pad, cy + 50 * s),
                        radius=int(30 * s), fill=(255, 215, 0), outline=(255, 255, 255),
                        width=4)
    d.text((cx - w / 2, cy - 38 * s), txt, font=f, fill=(120, 0, 20))


# ---------------------------------------------------------------- scenes
def scene_intro(img, d, t):
    for i, cx in enumerate((180, 540, 900)):
        draw_diya(d, cx, 1650, t + i, 1.3)
    a1 = ease_back(t / 0.6)
    if a1 > 0:
        text_c(d, 380 - 60 * (1 - a1), "BHAI DOOJ", int(150 * min(a1, 1.15)),
               (255, 215, 0), stroke=6, stroke_fill=(120, 0, 30))
    if t > 0.5:
        a2 = ease_out((t - 0.5) / 0.5)
        text_c(d, 580 + 40 * (1 - a2), "aa raha hai!", 96, (255, 255, 255),
               stroke=4, stroke_fill=(80, 0, 40))
    if t > 1.4:
        a3 = ease_back((t - 1.4) / 0.5)
        y = 860
        box_h = 300 * a3
        d.rounded_rectangle((90, y, W - 90, y + box_h), radius=40,
                            fill=(255, 255, 255), outline=(255, 215, 0), width=8)
        if a3 > 0.8:
            text_c(d, y + 45, "Gift nahi dogi", 92, (190, 10, 40))
            text_c(d, y + 160, "bhai ko?", 104, (190, 10, 40))
    if t > 2.4:
        a4 = ease_out((t - 2.4) / 0.4)
        wob = 6 * math.sin(t * 12)
        text_c(d, 1260 + wob, "Uska favourite gift yahan hai", 56,
               (255, int(230 * a4), int(120 * a4)))
        text_c(d, 1340 + wob, "v  v  v", 56, (255, 215, 0))


def scene_car(img, d, t, idx, p):
    # header
    text_c(d, 120, f"GIFT IDEA #{idx + 1}", 60, (255, 215, 0), stroke=3,
           stroke_fill=(90, 0, 30))
    # road
    d.rectangle((0, 1180, W, 1230), fill=(30, 30, 35))
    for k in range(8):
        xx = (k * 180 - t * 900) % (W + 180) - 180
        d.rectangle((xx, 1202, xx + 100, 1210), fill=(255, 215, 0))

    arrive = ease_out(t / 0.9)
    wheel_ang = t * 18 * (1.0 - 0.7 * arrive)
    if t < 1.0:
        speed_lines(d, t, 820, 1170)
    scale = 1.55 if not p.get("pair") else 0.85
    if p.get("pair"):
        x1 = -1000 + (20 + 1000) * arrive
        x2 = W + 400 - (W + 400 - 550) * arrive
        draw_car(d, x1, 1180 - 195 * scale, scale, p["body"], (30, 30, 30), wheel_ang)
        draw_car(d, x2, 1180 - 195 * scale, scale, p["body2"], p["accent"], wheel_ang, facing=-1)
    else:
        car_w = 600 * scale
        x = -car_w - 100 + (W / 2 - car_w / 2 + car_w + 100) * arrive
        y = 1180 - 195 * scale + 4 * math.sin(t * 30) * (1 - arrive)
        draw_car(d, x, y, scale, p["body"], p["accent"], wheel_ang)

    # name card
    if t > 0.6:
        a = ease_back((t - 0.6) / 0.5)
        text_c(d, 300 - 40 * (1 - a), p["line1"], 70, (255, 255, 255),
               stroke=3, stroke_fill=(60, 0, 30))
        size = fit_size(d, p["line2"], W - 120, 140)
        text_c(d, 400, p["line2"], int(size * min(a, 1.1)), (255, 215, 0),
               stroke=6, stroke_fill=(130, 0, 30))
    if t > 1.1:
        badge(d, W / 2, 680, p["tag"], t - 1.1)
    if t > 1.5:
        a = ease_out((t - 1.5) / 0.4)
        text_c(d, 1300 + 30 * (1 - a), p["sub"], 58,
               (255, int(255 * a), int(255 * a)), bold=False)
    if t > 1.9:
        pulse = 1 + 0.04 * math.sin(t * 10)
        txt = "Perfect gift for Bhai"
        f = font(int(62 * pulse))
        w = d.textlength(txt, font=f)
        d.rounded_rectangle((W / 2 - w / 2 - 40, 1440, W / 2 + w / 2 + 40, 1540),
                            radius=50, fill=(200, 10, 50))
        d.text((W / 2 - w / 2, 1455), txt, font=f, fill=(255, 255, 255))


def scene_outro(img, d, t):
    for i, cx in enumerate((150, 400, 680, 930)):
        draw_diya(d, cx, 1720, t + i * 0.7, 1.0)
    a = ease_back(t / 0.6)
    text_c(d, 250, "Is Bhai Dooj", int(110 * min(a, 1.1)), (255, 255, 255),
           stroke=5, stroke_fill=(90, 0, 40))
    if t > 0.4:
        text_c(d, 400, "bhai ko do", 100, (255, 215, 0), stroke=5,
               stroke_fill=(120, 0, 30))
        text_c(d, 530, "HOT WHEELS!", 130, (255, 90, 30), stroke=6,
               stroke_fill=(255, 255, 255))
    # gift box
    if t > 0.9:
        g = ease_back((t - 0.9) / 0.5)
        cx, cy, s = W / 2, 1030, 220 * g
        d.rectangle((cx - s, cy - s * 0.6, cx + s, cy + s), fill=(200, 10, 50))
        d.rectangle((cx - s * 1.1, cy - s, cx + s * 1.1, cy - s * 0.55), fill=(230, 30, 70))
        d.rectangle((cx - s * 0.15, cy - s, cx + s * 0.15, cy + s), fill=(255, 215, 0))
        d.ellipse((cx - s * 0.7, cy - s * 1.45, cx - s * 0.05, cy - s * 0.95),
                  outline=(255, 215, 0), width=max(1, int(20 * g)))
        d.ellipse((cx + s * 0.05, cy - s * 1.45, cx + s * 0.7, cy - s * 0.95),
                  outline=(255, 215, 0), width=max(1, int(20 * g)))
    if t > 1.6:
        pulse = 1 + 0.05 * math.sin(t * 9)
        txt = "DM to Order Now"
        f = font(int(80 * pulse))
        w = d.textlength(txt, font=f)
        d.rounded_rectangle((W / 2 - w / 2 - 50, 1330, W / 2 + w / 2 + 50, 1460),
                            radius=65, fill=(255, 215, 0), outline=(255, 255, 255), width=6)
        d.text((W / 2 - w / 2, 1350), txt, font=f, fill=(120, 0, 20))
    if t > 2.2:
        text_c(d, 1500, "Limited stock  |  RLC  |  Premium", 46, (255, 230, 200),
               bold=False)


def render_frame(n):
    tg = n / FPS
    img = BG.copy()
    d = ImageDraw.Draw(img)
    draw_sparkles(d, tg)
    if tg < INTRO_S:
        scene_intro(img, d, tg)
    elif tg < INTRO_S + CAR_S * len(PRODUCTS):
        k = int((tg - INTRO_S) // CAR_S)
        scene_car(img, d, tg - INTRO_S - k * CAR_S, k, PRODUCTS[k])
    else:
        scene_outro(img, d, tg - INTRO_S - CAR_S * len(PRODUCTS))
    # quick white flash on scene cuts
    cuts = [INTRO_S + CAR_S * k for k in range(len(PRODUCTS) + 1)]
    for c in cuts:
        dt = tg - c
        if 0 <= dt < 0.15:
            img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)),
                              0.7 * (1 - dt / 0.15))
    return img


# ---------------------------------------------------------------- music
def make_music(path, seconds, sr=44100, bpm=120):
    t = np.arange(int(seconds * sr)) / sr
    out = np.zeros_like(t)
    beat = 60 / bpm
    # kick on every beat, clap on 2 & 4, hi-hat on off-beats
    for i in range(int(seconds / beat) + 1):
        s = int(i * beat * sr)
        n = int(0.25 * sr)
        seg = t[:n]
        kick = np.sin(2 * np.pi * (50 + 120 * np.exp(-seg * 30)) * seg) * np.exp(-seg * 9)
        e = min(len(out), s + n)
        out[s:e] += 0.9 * kick[:e - s]
        if i % 2 == 1:
            nn = int(0.12 * sr)
            clap = np.random.randn(nn) * np.exp(-np.arange(nn) / sr * 35)
            e = min(len(out), s + nn)
            out[s:e] += 0.35 * clap[:e - s]
        hs = s + int(beat / 2 * sr)
        nn = int(0.05 * sr)
        if hs + nn < len(out):
            hat = np.random.randn(nn) * np.exp(-np.arange(nn) / sr * 90)
            out[hs:hs + nn] += 0.15 * hat
    # simple festive melody (raag-ish pentatonic)
    notes = [0, 2, 4, 7, 9, 7, 4, 2, 0, 4, 7, 12, 9, 7, 4, 2]
    base = 293.66  # D4
    step = beat / 2
    for i in range(int(seconds / step)):
        f = base * 2 ** (notes[i % len(notes)] / 12)
        s = int(i * step * sr)
        n = int(step * sr)
        seg = t[:n]
        tone = (np.sin(2 * np.pi * f * seg) + 0.4 * np.sin(4 * np.pi * f * seg)) * \
            np.exp(-seg * 6)
        e = min(len(out), s + n)
        out[s:e] += 0.22 * tone[:e - s]
    fade = int(1.0 * sr)
    out[-fade:] *= np.linspace(1, 0, fade)
    out = out / np.max(np.abs(out)) * 0.85
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((out * 32767).astype(np.int16).tobytes())


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "bhai_dooj_reel.mp4"))
    ap.add_argument("--no-music", action="store_true")
    args = ap.parse_args()

    n_frames = int(TOTAL_S * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    wav = None
    if not args.no_music:
        wav = args.out + ".wav"
        make_music(wav, TOTAL_S)
        cmd += ["-i", wav, "-c:a", "aac", "-b:a", "160k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", args.out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(n_frames):
        proc.stdin.write(render_frame(n).tobytes())
    proc.stdin.close()
    proc.wait()
    if wav and os.path.exists(wav):
        os.remove(wav)
    print(f"Saved {args.out}  ({TOTAL_S:.1f}s, {n_frames} frames)")


if __name__ == "__main__":
    main()
