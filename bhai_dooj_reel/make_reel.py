"""
Bhai Dooj gift reel (Instagram Reel / YouTube Short, 1080x1920 @ 30fps).

Uses the real photo of the Hot Wheels wall (assets/wall.jpg) as background and
crops the actual cards from it for every gift frame. Soundtrack is a dhol +
plucked-string groove rendered in code (no copyrighted music).

    python make_reel.py            # -> bhai_dooj_reel.mp4
    python make_reel.py --no-music # silent, if you want to add trending audio in Instagram

Needs Pillow, numpy and ffmpeg.
"""
import argparse
import math
import os
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
FONTS = os.path.join(ASSETS, "fonts")
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

GOLD = (255, 204, 51)
WHITE = (255, 255, 255)
RED = (214, 20, 50)
INK = (25, 10, 15)

# ----------------------------------------------------------------- fonts
_fc = {}


def font(size, weight="ExtraBold"):
    size = max(1, int(size))
    k = (size, weight)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(os.path.join(FONTS, f"Poppins-{weight}.ttf"), size)
    return _fc[k]


_ec = {}


def emoji(ch, size):
    """Colour emoji as an RGBA image (Noto only renders at 109px, so scale)."""
    k = (ch, size)
    if k not in _ec:
        f = ImageFont.truetype(EMOJI_FONT, 109)
        im = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
        im = im.crop(im.getbbox())
        _ec[k] = im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)
    return _ec[k]


# ----------------------------------------------------------------- photo + cards
WALL = Image.open(os.path.join(ASSETS, "wall.jpg")).convert("RGB")
K = WALL.width / 1999  # crop boxes below were measured on a 1999px-wide preview


def card(box, pad=6):
    x0, y0, x1, y1 = box
    c = WALL.crop((int((x0 - pad) * K), int((y0 - pad) * K),
                   int((x1 + pad) * K), int((y1 + pad) * K)))
    return c


PRODUCTS = [
    dict(title="Ferrari", pre="Hot Wheels", tag="RLC", note="Red Line Club",
         cards=[(400, 680, 515, 850)]),
    dict(title="Mustang", pre="Original Hot Wheels", tag="RLC", note="Blue  •  Red Line Club",
         cards=[(145, 475, 262, 648)]),
    dict(title='Nissan "Godzilla"', pre="Hot Wheels", tag="PREMIUM", note="Nissan Skyline GT-R",
         cards=[(1612, 490, 1730, 662)]),
    dict(title="TFOX", pre="Hot Wheels", tag="COLLECTOR PICK", note="Fast & Furious Premium",
         cards=[(882, 90, 995, 250)]),
    dict(title="Brian O'Conner Set", pre="Hot Wheels", tag="FULL SET", note="Fast & Furious  •  Premium",
         cards=[(882, 270, 995, 450), (882, 470, 995, 650),
                (882, 665, 995, 845), (882, 860, 995, 1040)]),
]

INTRO_S, GIFT_S, OUTRO_S = 4.0, 3.4, 4.2
N = len(PRODUCTS)
TOTAL_S = INTRO_S + GIFT_S * N + OUTRO_S


def polish(img, target_h):
    """Upscale a card crop cleanly, round corners, add soft shadow."""
    w = int(img.width * target_h / img.height)
    big = img.resize((w, target_h), Image.LANCZOS)
    big = big.filter(ImageFilter.UnsharpMask(radius=2.2, percent=120, threshold=2))
    mask = Image.new("L", big.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, target_h - 1), radius=26, fill=255)
    pad = 60
    out = Image.new("RGBA", (w + pad * 2, target_h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("L", out.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((pad + 10, pad + 24, pad + w + 10, pad + target_h + 24),
                                         radius=26, fill=170)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    out.paste((0, 0, 0, 255), (0, 0), sh)
    big = big.convert("RGBA")
    big.putalpha(mask)
    # thin white border like a real protector case highlight
    ImageDraw.Draw(big).rounded_rectangle((1, 1, w - 2, target_h - 2), radius=26,
                                          outline=(255, 255, 255, 200), width=4)
    out.alpha_composite(big, (pad, pad))
    return out


for p in PRODUCTS:
    crops = [card(b) for b in p["cards"]]
    h = 1000 if len(crops) == 1 else 480
    p["imgs"] = [polish(c, h) for c in crops]

# ----------------------------------------------------------------- backgrounds
# Vertical pan plate: wall scaled to slightly taller than the frame.
PAN_H = int(H * 1.04)
PAN = WALL.resize((int(WALL.width * PAN_H / WALL.height), PAN_H), Image.LANCZOS)


def darken(img, amt, warm=True):
    arr = np.asarray(img).astype(np.float32) * amt
    if warm:
        arr[..., 0] *= 1.06
        arr[..., 2] *= 0.9
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def vignette():
    y, x = np.ogrid[:H, :W]
    d = np.sqrt(((x - W / 2) / (W * 0.75)) ** 2 + ((y - H / 2) / (H * 0.65)) ** 2)
    v = np.clip(1.15 - d * 0.75, 0.25, 1.0)
    return v[..., None].astype(np.float32)


VIG = vignette()

# blurred plates for the gift scenes (one per product, centred near its card)
BLUR_PLATES = []
for p in PRODUCTS:
    x0, y0, x1, y1 = p["cards"][0]
    cx = (x0 + x1) / 2 * K
    cw = WALL.height * W / H * 0.8
    left = int(np.clip(cx - cw / 2, 0, WALL.width - cw))
    plate = WALL.crop((left, 0, int(left + cw), WALL.height)).resize((int(W * 1.1), int(H * 1.1)),
                                                                     Image.BILINEAR)
    plate = plate.filter(ImageFilter.GaussianBlur(26))
    BLUR_PLATES.append(darken(plate, 0.55))


def apply_vig(img):
    arr = np.asarray(img).astype(np.float32) * VIG
    return Image.fromarray(arr.astype(np.uint8))


# ----------------------------------------------------------------- easing / text
def clamp(t):
    return max(0.0, min(1.0, t))


def ease(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_back(t):
    t = clamp(t)
    return 1 + 2.4 * (t - 1) ** 3 + 1.4 * (t - 1) ** 2


def shadow_text(base, xy, txt, f, fill, alpha=1.0, anchor="mt", shadow=True):
    if alpha <= 0:
        return
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if shadow:
        d.text((xy[0] + 3, xy[1] + 5), txt, font=f, fill=(0, 0, 0, 170), anchor=anchor)
        layer = layer.filter(ImageFilter.GaussianBlur(5))
        d = ImageDraw.Draw(layer)
    d.text(xy, txt, font=f, fill=fill + (255,), anchor=anchor)
    if alpha < 1:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer.putalpha(a)
    base.alpha_composite(layer)


def pill(base, cx, y, txt, f, bg, fg, alpha=1.0, padx=34, pady=16):
    if alpha <= 0:
        return
    d0 = ImageDraw.Draw(base)
    l, t, r, b = d0.textbbox((0, 0), txt, font=f)
    w, h = r - l, b - t
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    box = (cx - w / 2 - padx, y, cx + w / 2 + padx, y + h + pady * 2)
    d.rounded_rectangle(box, radius=int((h + pady * 2) / 2), fill=bg + (int(255 * alpha),))
    d.text((cx - w / 2 - l, y + pady - t), txt, font=f, fill=fg + (int(255 * alpha),))
    base.alpha_composite(layer)
    return box


def fit(txt, weight, max_w, start):
    s = start
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    while s > 30 and d.textlength(txt, font=font(s, weight)) > max_w:
        s -= 3
    return s


def paste_emoji(base, ch, cx, cy, size, alpha=1.0, rot=0):
    if alpha <= 0:
        return
    e = emoji(ch, size)
    if rot:
        e = e.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        e = e.copy()
        e.putalpha(e.getchannel("A").point(lambda v: int(v * alpha)))
    base.alpha_composite(e, (int(cx - e.width / 2), int(cy - e.height / 2)))


def shake(t, amt=3.0):
    """Tiny handheld-camera drift."""
    return (amt * math.sin(t * 1.7) + amt * 0.5 * math.sin(t * 4.3),
            amt * math.cos(t * 1.3) + amt * 0.5 * math.sin(t * 3.7))


# ----------------------------------------------------------------- scenes
def scene_intro(t):
    # slow pan across the real wall, like a phone walk-by
    span = PAN.width - W
    x = span * (0.05 + 0.55 * ease(t / INTRO_S * 0.9))
    sx, sy = shake(t, 4)
    frame = PAN.crop((int(x + sx), int(20 + sy), int(x + sx) + W, int(20 + sy) + H))
    frame = darken(frame, 0.62 if t > 0.6 else 1 - 0.38 * ease(t / 0.6))
    frame = apply_vig(frame).convert("RGBA")

    a = ease(t / 0.5)
    shadow_text(frame, (W / 2, 470 + 40 * (1 - a)), "Bhai Dooj", font(150), GOLD, a)
    a = ease((t - 0.35) / 0.5)
    shadow_text(frame, (W / 2, 660 + 40 * (1 - a)), "aa raha hai...", font(84, "SemiBold"), WHITE, a)
    if t > 1.3:
        s = ease_back((t - 1.3) / 0.45)
        pill(frame, W / 2, 920, "Gift nahi dogi", font(int(92 * s)), WHITE, RED, clamp(s))
        pill(frame, W / 2, 1070, "bhai ko?", font(int(92 * s)), WHITE, RED, clamp(s))
        paste_emoji(frame, "\U0001F440", W / 2 + 330, 1150, int(110 * s), clamp(s))
    a = ease((t - 2.5) / 0.5)
    shadow_text(frame, (W / 2, 1440 + 30 * (1 - a)), "Uska favourite gift yahan hai",
                font(56, "SemiBold"), WHITE, a)
    if t > 2.8:
        bob = 12 * math.sin(t * 6)
        paste_emoji(frame, "\U0001F447", W / 2, 1600 + bob, 90, ease((t - 2.8) / 0.3))
    return frame


def scene_gift(t, i):
    p = PRODUCTS[i]
    plate = BLUR_PLATES[i]
    z = 1.0 + 0.04 * (t / GIFT_S)
    pw, ph = int(W * z), int(H * z)
    sx, sy = shake(t + i * 3, 3)
    ox = (plate.width - pw) / 2 + sx
    oy = (plate.height - ph) / 2 + sy
    frame = plate.crop((int(ox), int(oy), int(ox) + pw, int(oy) + ph)).resize((W, H), Image.BILINEAR)
    frame = apply_vig(frame).convert("RGBA")

    # header
    a = ease(t / 0.35)
    pill(frame, W / 2, 120, f"GIFT #{i + 1}", font(40, "SemiBold"), RED, WHITE, a, padx=28, pady=10)
    a = ease((t - 0.1) / 0.4)
    shadow_text(frame, (W / 2, 215 + 25 * (1 - a)), p["pre"], font(56, "SemiBold"), WHITE, a)
    size = fit(p["title"], "ExtraBold", W - 100, 120)
    a = ease((t - 0.2) / 0.4)
    shadow_text(frame, (W / 2, 290 + 25 * (1 - a)), p["title"], font(size), GOLD, a)

    # real cards
    imgs = p["imgs"]
    if len(imgs) == 1:
        s = 0.86 + 0.14 * ease_back(t / 0.55) + 0.03 * (t / GIFT_S)
        im = imgs[0]
        im = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)
        rot = 4 * (1 - ease(t / 0.6))
        if rot > 0.05:
            im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
        alpha = clamp(t / 0.25)
        if alpha < 1:
            im = im.copy()
            im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
        frame.alpha_composite(im, (int(W / 2 - im.width / 2), int(1010 - im.height / 2)))
    else:
        pos = [(W * 0.28, 720), (W * 0.72, 720), (W * 0.28, 1240), (W * 0.72, 1240)]
        for k, (im, (cx, cy)) in enumerate(zip(imgs, pos)):
            tk = t - 0.15 * k
            if tk <= 0:
                continue
            s = 0.8 + 0.2 * ease_back(tk / 0.5)
            im2 = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)
            frame.alpha_composite(im2, (int(cx - im2.width / 2), int(cy - im2.height / 2)))

    # tag + note
    if t > 0.7:
        s = ease_back((t - 0.7) / 0.4)
        pill(frame, W / 2, 1560, p["tag"], font(int(54 * s)), GOLD, INK, clamp(s))
    a = ease((t - 1.0) / 0.4)
    shadow_text(frame, (W / 2, 1680), p["note"], font(44, "Medium"), WHITE, a)
    if t > 1.4:
        a = ease((t - 1.4) / 0.4)
        pill(frame, W / 2 - 30, 1770, "Perfect gift for Bhai", font(46, "SemiBold"), RED, WHITE, a,
             padx=30, pady=12)
        paste_emoji(frame, "\U0001F381", W / 2 + 270, 1808, 64, a)
    return frame


def scene_outro(t):
    # pull back to the full wall
    z = 1.25 - 0.2 * ease(t / OUTRO_S)
    span = PAN.width - W
    x = span * 0.5
    cw, ch = W / z, H / z
    cx, cy = x + W / 2, PAN.height / 2
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    frame = PAN.crop(tuple(int(v) for v in box)).resize((W, H), Image.BILINEAR)
    frame = apply_vig(darken(frame, 0.5)).convert("RGBA")

    a = ease(t / 0.45)
    shadow_text(frame, (W / 2, 330 + 30 * (1 - a)), "Is Bhai Dooj", font(110), WHITE, a)
    a = ease((t - 0.3) / 0.45)
    shadow_text(frame, (W / 2, 500 + 30 * (1 - a)), "bhai ko do", font(80, "SemiBold"), WHITE, a)
    if t > 0.6:
        s = ease_back((t - 0.6) / 0.45)
        shadow_text(frame, (W / 2, 610), "Hot Wheels", font(int(150 * s)), GOLD, clamp(s))
    if t > 1.2:
        s = ease_back((t - 1.2) / 0.4)
        paste_emoji(frame, "\U0001F381", W / 2, 1000, int(230 * s), clamp(s), rot=6 * math.sin(t * 5))
    if t > 1.8:
        pulse = 1 + 0.035 * math.sin(t * 8)
        pill(frame, W / 2, 1300, "DM to Order", font(int(84 * pulse)), GOLD, INK,
             ease((t - 1.8) / 0.3), padx=60, pady=22)
    a = ease((t - 2.3) / 0.4)
    shadow_text(frame, (W / 2, 1490), "Limited stock  •  RLC  •  Premium", font(46, "Medium"), WHITE, a)
    return frame


def render(n):
    t = n / FPS
    if t < INTRO_S:
        f = scene_intro(t)
    elif t < INTRO_S + GIFT_S * N:
        i = int((t - INTRO_S) // GIFT_S)
        f = scene_gift(t - INTRO_S - i * GIFT_S, i)
    else:
        f = scene_outro(t - INTRO_S - GIFT_S * N)
    f = f.convert("RGB")
    # short crossfade-to-black dip around cuts
    for c in [INTRO_S + GIFT_S * k for k in range(N + 1)]:
        dt = abs(t - c)
        if dt < 0.1:
            f = Image.blend(f, Image.new("RGB", (W, H)), 0.55 * (1 - dt / 0.1))
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
