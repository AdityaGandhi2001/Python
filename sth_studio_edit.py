"""
Professional studio edit of the Supra unboxing clip.

Inputs : the source clip + the matte cache from sth_matte.py (alpha PNGs + hands.json)
Output : 1080x1920 30fps reel with a studio backdrop, light wrap, contact shadow,
         speed ramps (flow-interpolated slow motion), punch-in moves, whip
         transitions, titles/callouts, end card and an original beat + SFX.

    python sth_studio_edit.py source.mp4 matte_dir out.mp4 [--watch black|gold|silver|none]
"""

import json
import math
import os
import subprocess
import sys
import wave

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import sth_bg_swap as B

OW, OH, FPS = 1080, 1920, 30
INTER = "/usr/share/fonts/opentype/inter/"
F_BLACK, F_BLACK_I, F_XB, F_BOLD = (INTER + n for n in
                                    ("Inter-Black.otf", "Inter-BlackItalic.otf", "Inter-ExtraBold.otf", "Inter-Bold.otf"))
F_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
ORANGE = (255, 122, 26)

# ---------------------------------------------------------------- edit decision list
# (name, src_start, src_end, speed, zoom_from, zoom_to)
EDL = [
    ("hook",   14.00, 14.50, 0.55, 1.30, 1.18),
    ("intro",   0.05,  2.40, 1.00, 1.00, 1.08),
    ("hero",    4.00,  4.90, 0.75, 1.02, 1.14),
    ("open",    2.50,  3.90, 1.50, 1.04, 1.04),
    ("tear",    5.00,  6.90, 1.60, 1.04, 1.10),
    ("tray",    8.00,  9.90, 1.45, 1.00, 1.06),
    ("car",    12.50, 16.30, 1.00, 1.14, 1.00),
    ("end",    15.60, 15.60, 0.00, 1.00, 1.00),  # freeze for the end card
]
END_LEN = 1.6


def build_timeline():
    """List of (segment index, local t, src time) for every output frame + segment start times."""
    tl, starts, t_out = [], [], 0.0
    for i, (name, s0, s1, sp, z0, z1) in enumerate(EDL):
        dur = END_LEN if sp == 0 else (s1 - s0) / sp
        starts.append(t_out)
        n = int(round(dur * FPS))
        for j in range(n):
            lt = j / FPS
            src = s0 if sp == 0 else s0 + lt * sp
            if sp >= 1.0:  # real-time / sped-up: use whole source frames (no blending, no ghosting)
                src = round(src * 30) / 30
            tl.append((i, lt, dur, src))
        t_out += n / FPS
    return tl, starts, t_out


# ---------------------------------------------------------------- source access
class Source:
    def __init__(self, src, matte, cache_dir):
        s = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                     "stream=width,height,r_frame_rate", "-of", "csv=p=0", src]).decode().strip()
        w, h, fr = s.split(",")
        self.w, self.h = int(w), int(h)
        n, d = fr.split("/")
        self.fps = float(n) / float(d)
        self.matte = matte
        self.n = len([f for f in os.listdir(matte) if f.startswith("alpha_")])
        self.hands = json.load(open(f"{matte}/hands.json"))
        raw = f"{cache_dir}/frames_{self.w}x{self.h}.u8"
        need = self.n * self.w * self.h * 3
        if not os.path.exists(raw) or os.path.getsize(raw) < need:
            with open(raw, "wb") as f:
                subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-frames:v", str(self.n),
                                "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=f)
        self.frames = np.memmap(raw, np.uint8, "r", shape=(self.n, self.h, self.w, 3))
        self.dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        self._cache = {}

    def alpha(self, k):
        a = cv2.imread(f"{self.matte}/alpha_{k:05d}.png", cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
        # keep the main subject: drop pieces much smaller than the biggest one (stray roadside etc.)
        n, lab, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8))
        if n > 2:
            areas = st[1:, cv2.CC_STAT_AREA]
            drop = np.isin(lab, np.where(areas < areas.max() * 0.15)[0] + 1).astype(np.uint8)
            a[cv2.dilate(drop, np.ones((9, 9), np.uint8)) > 0] = 0
        # solid subject: fill holes / see-through patches inside the outline, keep soft outer edges
        hard = (a > 0.35).astype(np.uint8)
        cnts, _ = cv2.findContours(hard, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        solid = np.zeros_like(hard)
        cv2.drawContours(solid, cnts, -1, 1, -1)
        inner = cv2.GaussianBlur(cv2.erode(solid, np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 2)
        return np.maximum(a, inner)

    def at(self, t):
        """RGB, alpha and hands at source time t (flow-interpolated between frames)."""
        x = min(max(t * self.fps, 0), self.n - 1)
        k0 = int(math.floor(x))
        k1 = min(k0 + 1, self.n - 1)
        f = x - k0
        a0, i0 = self.alpha(k0), np.asarray(self.frames[k0])
        hands = self.hands[k0 if f < 0.5 else k1]
        if f < 0.04 or f > 0.96 or k1 == k0:
            return i0, a0, hands
        a1, i1 = self.alpha(k1), np.asarray(self.frames[k1])
        g0 = cv2.cvtColor(i0, cv2.COLOR_RGB2GRAY)
        g1 = cv2.cvtColor(i1, cv2.COLOR_RGB2GRAY)
        fl = self.dis.calc(g0, g1, None)  # 0 -> 1
        gx, gy = np.meshgrid(np.arange(self.w, dtype=np.float32), np.arange(self.h, dtype=np.float32))
        m0x, m0y = gx - fl[..., 0] * f, gy - fl[..., 1] * f
        m1x, m1y = gx + fl[..., 0] * (1 - f), gy + fl[..., 1] * (1 - f)
        w0 = cv2.remap(i0, m0x, m0y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
        w1 = cv2.remap(i1, m1x, m1y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
        b0 = cv2.remap(a0, m0x, m0y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        b1 = cv2.remap(a1, m1x, m1y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        rgb = (w0 * (1 - f) + w1 * f).astype(np.uint8)
        return rgb, b0 * (1 - f) + b1 * f, hands


# ---------------------------------------------------------------- compositing
def decontaminate(rgb, a):
    """Replace edge colours (which carry the old asphalt) with nearby interior foreground colour."""
    inner = (a > 0.96).astype(np.float32)
    num = cv2.GaussianBlur(rgb.astype(np.float32) * inner[..., None], (0, 0), 5)
    den = cv2.GaussianBlur(inner, (0, 0), 5)[..., None] + 1e-4
    fill = num / den
    wgt = np.clip((a - 0.45) / 0.5, 0, 1)[..., None]
    return rgb.astype(np.float32) * wgt + fill * (1 - wgt)


class Studio:
    """Seamless studio cyc: graded wall, soft floor, warm key light that follows the subject."""

    def __init__(self):
        yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
        self.yy, self.xx = yy, xx
        g = yy / OH
        wall_top, wall_bot = np.array([34, 36, 42]), np.array([22, 23, 27])
        floor_near, floor_far = np.array([52, 47, 42]), np.array([30, 29, 30])
        horizon = 0.70
        t = np.clip((g - horizon) / 0.06 + 0.5, 0, 1)[..., None]  # soft cyc curve
        wall = wall_top * (1 - g[..., None] / horizon) + wall_bot * (g[..., None] / horizon)
        fg_ = np.clip((g - horizon) / (1 - horizon), 0, 1)[..., None]
        floor = floor_far * (1 - fg_) + floor_near * fg_
        base = wall * (1 - t) + floor * t
        # teal fill from the left, orange kicker from the right (low intensity)
        base += (np.clip(1 - xx / (OW * 0.6), 0, 1) ** 2)[..., None] * np.array([0, 18, 22])
        base += (np.clip((xx - OW * 0.5) / (OW * 0.5), 0, 1) ** 2)[..., None] * np.array([26, 12, 0])
        rng = np.random.default_rng(2)
        base += cv2.GaussianBlur(rng.normal(0, 2.2, (OH, OW)).astype(np.float32), (0, 0), 1.2)[..., None]
        self.base = base.astype(np.float32)
        self.key = np.array([OW * 0.5, OH * 0.4], np.float32)

    def frame(self, centroid):
        self.key = self.key * 0.92 + np.asarray(centroid, np.float32) * 0.08  # light gently follows
        cx, cy = self.key[0], self.key[1] - OH * 0.08
        d = np.sqrt(((self.xx - cx) / (OW * 0.62)) ** 2 + ((self.yy - cy) / (OH * 0.42)) ** 2)
        pool = (np.clip(1 - d, 0, 1) ** 1.8)[..., None] * np.array([92, 66, 44])
        return self.base + pool


def composite(rgb, a, hands, studio, zoom, watch):
    rgb = B.restyle_watch(rgb, [np.asarray(p, np.float32) for p in hands], a, watch)
    fg = decontaminate(rgb, a)
    fg = cv2.resize(fg, (OW, OH), interpolation=cv2.INTER_LANCZOS4)
    al = np.clip(cv2.resize(a, (OW, OH), interpolation=cv2.INTER_CUBIC), 0, 1)
    fg = cv2.addWeighted(fg, 1.35, cv2.GaussianBlur(fg, (0, 0), 1.6), -0.35, 0)  # crisp after upscale
    # subject grade: tame harsh sun, slightly richer colour
    lum = cv2.cvtColor(np.clip(fg, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)[..., None]
    fg = lum + (fg - lum) * 1.08
    fg = fg * 0.96 + 4
    # camera move: punch-in on the subject (background moves less -> depth)
    if zoom != 1.0:
        def zoomed(img, z, interp):
            hh, ww = img.shape[:2]
            M = cv2.getRotationMatrix2D((ww / 2, hh * 0.45), 0, z)
            return cv2.warpAffine(img, M, (ww, hh), flags=interp, borderMode=cv2.BORDER_REFLECT)
        fg = zoomed(fg, zoom, cv2.INTER_LINEAR)
        al = zoomed(al, zoom, cv2.INTER_LINEAR)
    ys, xs = np.nonzero(al[::8, ::8] > 0.5)
    centroid = (xs.mean() * 8, ys.mean() * 8) if len(xs) else (OW / 2, OH / 2)
    bg = studio.frame(centroid)
    if zoom != 1.0:
        z2 = 1 + (zoom - 1) * 0.35
        M = cv2.getRotationMatrix2D((OW / 2, OH * 0.45), 0, z2)
        bg = cv2.warpAffine(bg, M, (OW, OH), borderMode=cv2.BORDER_REFLECT)
    # contact shadow + ambient occlusion
    sh = cv2.GaussianBlur(al, (0, 0), 26)
    M = np.float32([[1, 0, 18], [0, 1, 34]])
    sh = cv2.warpAffine(sh, M, (OW, OH))
    ao = cv2.GaussianBlur(al, (0, 0), 8)
    bg = bg * (1 - (sh * 0.55 + ao * 0.25)[..., None] * (1 - al[..., None]))
    # light wrap: background light bleeding onto the subject's edges
    wrap = np.clip((1 - cv2.GaussianBlur(al, (0, 0), 10)) * al * 2.2, 0, 1)[..., None]
    fg = fg * (1 - wrap * 0.4) + cv2.GaussianBlur(bg, (0, 0), 14) * wrap * 0.4
    out = fg * al[..., None] + bg * (1 - al[..., None])
    return out


def finish(out, fi):
    """Final look: gentle S-curve, warm highlights / cool shadows, vignette, fine grain."""
    x = np.clip(out, 0, 255) / 255
    x = x + 0.06 * np.sin((x - 0.5) * math.pi) * (1 - np.abs(2 * x - 1))  # soft contrast
    lum = x.mean(2, keepdims=True)
    x = x + (lum - 0.5) * np.array([0.03, 0.0, -0.035]) * 2
    v = getattr(finish, "vig", None)
    if v is None:
        yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
        d = np.sqrt(((xx - OW / 2) / (OW * 0.72)) ** 2 + ((yy - OH * 0.47) / (OH * 0.68)) ** 2)
        finish.vig = v = np.clip(1.08 - d ** 2 * 0.55, 0.55, 1)[..., None].astype(np.float32)
    x = x * v
    rng = np.random.default_rng(fi)
    g = rng.normal(0, 0.012, (OH // 2, OW // 2)).astype(np.float32)
    x = x + cv2.resize(g, (OW, OH), interpolation=cv2.INTER_LINEAR)[..., None]
    return np.clip(x * 255, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- titles
_fc = {}


def font(p, s):
    k = (p, int(s))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]


def ease(t):
    t = min(max(t, 0), 1)
    return 1 - (1 - t) ** 3


def text_layer(lines, t, t_in=0.0, t_out=None):
    """lines: list of (text, font_path, size, colour, y, tracking, extra) drawn centred, animated in/out."""
    lay = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i, (txt, fp, size, col, y, track) in enumerate(lines):
        p = ease((t - t_in - i * 0.08) / 0.35)
        if t_out is not None:
            p *= 1 - ease((t - t_out) / 0.25)
        if p <= 0:
            continue
        f = font(fp, size)
        chars = list(txt)
        widths = [f.getlength(c) for c in chars]
        total = sum(widths) + track * (len(chars) - 1)
        x = OW / 2 - total / 2
        yy = y + (1 - p) * 40
        a = int(255 * p)
        for c, cw in zip(chars, widths):
            d.text((x, yy), c, font=f, fill=col + (a,), anchor="lm")
            x += cw + track
    return lay


def chip(lay, cx, y, txt, p, col=(255, 255, 255), fg=(0, 0, 0), emo=None):
    if p <= 0:
        return
    d = ImageDraw.Draw(lay)
    f = font(F_XB, 40)
    tw = f.getlength(txt)
    ew = 0
    e_img = None
    if emo:
        ef = ImageFont.truetype(F_EMOJI, 109)
        e_img = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(e_img).text((10, 10), emo, font=ef, embedded_color=True)
        e_img = e_img.crop(e_img.getbbox())
        e_img = e_img.resize((int(e_img.width * 44 / e_img.height), 44), Image.LANCZOS)
        ew = e_img.width + 14
    w_ = tw + ew + 56
    x0 = cx - w_ / 2 + (1 - ease(p)) * 60
    a = int(255 * min(1, p * 2))
    d.rounded_rectangle((x0, y, x0 + w_, y + 74), radius=37, fill=col + (int(a * 0.94),))
    d.text((x0 + 28, y + 37), txt, font=f, fill=fg + (a,), anchor="lm")
    if e_img is not None:
        e = e_img.copy()
        e.putalpha(e.getchannel("A").point(lambda v: int(v * p)))
        lay.alpha_composite(e, (int(x0 + 28 + tw + 14), int(y + 15)))


def overlays(seg, lt, dur, t_global):
    name = EDL[seg][0]
    lay = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    W_, O_ = (255, 255, 255), ORANGE
    if name == "hook":
        lay.alpha_composite(text_layer([("THE SUPRA", F_BLACK_I, 150, W_, 300, 4),
                                        ("IS HERE", F_BLACK_I, 150, O_, 450, 4)], lt, 0.0))
    elif name == "intro":
        lay.alpha_composite(text_layer([("HOT WHEELS PREMIUM", F_BOLD, 40, (220, 220, 220), 230, 10),
                                        ("FAST & FURIOUS", F_BLACK_I, 118, W_, 330, 2)], lt, 0.15, dur - 0.3))
    elif name == "hero":
        lay.alpha_composite(text_layer([("25 YEARS", F_BLACK_I, 130, O_, 1560, 4),
                                        ("OF FAST & FURIOUS", F_XB, 52, W_, 1680, 8)], lt, 0.1, dur - 0.25))
    elif name in ("open", "tear"):
        if name == "open":
            lay.alpha_composite(text_layer([("UNBOXING", F_BLACK_I, 96, W_, 260, 14)], lt, 0.05))
        else:
            lay.alpha_composite(text_layer([("UNBOXING", F_BLACK_I, 96, W_, 260, 14)], lt, -1, dur - 0.25))
    elif name == "car":
        lay.alpha_composite(text_layer([("TOYOTA", F_XB, 58, (230, 230, 230), 250, 26),
                                        ("SUPRA", F_BLACK_I, 210, O_, 400, 6)], lt, 0.1, dur - 0.3))
        chip(lay, OW / 2, 1540, "METAL / METAL", ease((lt - 0.9) / 0.3) * (1 - ease((lt - dur + 0.3) / 0.25)))
        chip(lay, OW / 2, 1640, "REAL RIDERS TIRES", ease((lt - 1.2) / 0.3) * (1 - ease((lt - dur + 0.3) / 0.25)))
        chip(lay, OW / 2, 1740, "BRIAN'S ICONIC SUPRA", ease((lt - 1.5) / 0.3) * (1 - ease((lt - dur + 0.3) / 0.25)),
             col=ORANGE, fg=(0, 0, 0), emo="🧡")
    elif name == "end":
        lay.alpha_composite(text_layer([("WOULD YOU", F_BLACK_I, 120, W_, 330, 3),
                                        ("COP THIS?", F_BLACK_I, 120, O_, 470, 3)], lt, 0.05))
        chip(lay, OW / 2, 1600, "comment below", ease((lt - 0.4) / 0.3), emo="👇")
        chip(lay, OW / 2, 1700, "follow for more drops", ease((lt - 0.6) / 0.3), col=ORANGE, emo="🔥")
    return lay


# ---------------------------------------------------------------- audio
def soundtrack(path, total, starts):
    sr = 44100
    n = int(total * sr) + sr
    mix = np.zeros(n)
    rng = np.random.default_rng(11)
    bpm = 120
    beat = 60 / bpm

    def add(sig, at, g=1.0):
        i = int(at * sr)
        if 0 <= i < n:
            j = min(n, i + len(sig))
            mix[i:j] += sig[: j - i] * g

    def env(m, k):
        return np.exp(-np.arange(m) / sr * k)

    def kick():
        m = int(0.4 * sr)
        tt = np.arange(m) / sr
        ph = 2 * np.pi * np.cumsum(45 + 110 * np.exp(-tt * 30)) / sr
        return np.sin(ph) * env(m, 8)

    def snare():
        m = int(0.3 * sr)
        nz = rng.standard_normal(m)
        nz -= np.convolve(nz, np.ones(10) / 10, "same")
        tone = np.sin(2 * np.pi * 190 * np.arange(m) / sr) * env(m, 30)
        return (nz * env(m, 18) * 0.5 + tone * 0.4)

    def hat(o=False):
        m = int((0.2 if o else 0.05) * sr)
        nz = rng.standard_normal(m)
        nz -= np.convolve(nz, np.ones(3) / 3, "same")
        return nz * env(m, 14 if o else 70) * 0.16

    def bass(f, d):
        m = int(d * sr)
        tt = np.arange(m) / sr
        s = np.tanh(2 * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)))
        return s * np.minimum(1, tt / 0.01) * np.exp(-tt * 1.5) * 0.5

    def pad(freqs, d):
        m = int(d * sr)
        tt = np.arange(m) / sr
        s = sum(np.sin(2 * np.pi * f * tt + np.sin(2 * np.pi * 0.3 * tt)) for f in freqs)
        return s * np.minimum(1, tt / 0.4) * np.minimum(1, (d - tt) / 0.4) * 0.05

    def whoosh(d=0.35, up=True):
        m = int(d * sr)
        nz = rng.standard_normal(m)
        out = np.zeros(m)
        for i in range(0, m, 256):  # crude moving band-pass
            k = 2 + int((i / m if up else 1 - i / m) * 30)
            seg = nz[i:i + 256]
            out[i:i + 256] = seg - np.convolve(seg, np.ones(k) / k, "same")
        return out * np.sin(np.linspace(0, np.pi, m)) ** 2 * 0.35

    def riser(d):
        m = int(d * sr)
        tt = np.arange(m) / sr
        sw = np.sin(2 * np.pi * np.cumsum(200 + 1800 * (tt / d) ** 2) / sr)
        nz = rng.standard_normal(m)
        nz -= np.convolve(nz, np.ones(5) / 5, "same")
        return (sw * 0.25 + nz * 0.18) * (tt / d) ** 2

    def impact():
        m = int(1.4 * sr)
        tt = np.arange(m) / sr
        boom = np.sin(2 * np.pi * np.cumsum(38 + 90 * np.exp(-tt * 7)) / sr) * np.exp(-tt * 2.6)
        return boom + rng.standard_normal(m) * np.exp(-tt * 16) * 0.35

    def tear(d):
        m = int(d * sr)
        nz = rng.standard_normal(m)
        crackle = (rng.random(m) < 0.02) * rng.standard_normal(m) * 3
        s = np.convolve(nz + crackle, np.ones(4) / 4, "same")
        return s * np.sin(np.linspace(0, np.pi, m)) * 0.12

    names = [e[0] for e in EDL]
    t_flick = starts[names.index("car")] - 1.5
    t_car = starts[names.index("car")]
    t_end = starts[names.index("end")]
    t_tear = starts[names.index("tear")]
    # groove: light before the reveal, full after
    roots = [55.0, 55.0, 65.4, 49.0]
    nb = int(total / beat) + 2
    for b in range(nb):
        at = b * beat
        if at > total:
            break
        bar, pos = divmod(b, 4)
        root = roots[bar % 4]
        full = at >= t_car
        building = t_flick - 2.5 <= at < t_car
        if at < t_flick:
            if pos in (0, 2):
                add(kick(), at, 0.8)
            add(hat(), at + beat / 2)
            if pos == 0:
                add(pad([root * 4, root * 5, root * 6], beat * 4), at)
                add(bass(root, beat * 1.8), at, 0.6)
        if building:
            add(hat(), at + beat / 4)
            add(hat(), at + 3 * beat / 4)
        if full and at < t_end + END_LEN - 0.3:
            if pos in (0, 2):
                add(kick(), at)
            if pos in (1, 3):
                add(snare(), at, 0.8)
            for s in range(2):
                add(hat(), at + s * beat / 2)
            if pos == 3:
                add(hat(True), at + beat / 2)
            if pos == 0:
                add(bass(root, beat * 1.9), at)
                add(pad([root * 4, root * 5, root * 6], beat * 4), at, 1.2)
    # sound design
    for i, s in enumerate(starts[1:], 1):
        if names[i] not in ("car", "end"):
            add(whoosh(0.3, up=i % 2 == 0), s - 0.15, 0.8)
    add(impact(), 0.0, 0.7)
    _, ts0, ts1, tsp, _, _ = EDL[names.index("tear")]
    add(tear((ts1 - ts0) / tsp), t_tear, 1.0)
    add(riser(t_car - t_flick + 1.2), t_flick - 1.2, 0.9)
    add(impact(), t_car, 1.0)
    add(whoosh(0.4), t_end - 0.2, 0.7)
    mix = mix[: int(total * sr)]
    mix = np.tanh(mix * 1.2)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
    f = int(0.5 * sr)
    mix[-f:] *= np.linspace(1, 0, f)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((mix * 32767).astype(np.int16).tobytes())


# ---------------------------------------------------------------- render
def render_frame(src, studio, tl, i, watch, starts):
    seg, lt, dur, st = tl[i]
    name, s0, s1, sp, z0, z1 = EDL[seg]
    zoom = z0 + (z1 - z0) * ease(lt / max(dur, 1e-6)) if name != "end" else 1.0 + 0.03 * ease(lt / dur)
    rgb, a, hands = src.at(st)
    out = composite(rgb, a, hands, studio, zoom, watch)
    if name == "end":  # soften the freeze so the end-card text reads
        out = cv2.GaussianBlur(out, (0, 0), 1 + 7 * ease(lt / 0.5)) * (1 - 0.35 * ease(lt / 0.5))
    # whip-pan transition: directional smear over the first 3 frames of a segment
    j = int(round(lt * FPS))
    if seg > 0 and j < 3 and name not in ("end",):
        k = int(60 - j * 20)
        if k > 1:
            ker = np.zeros((1, k), np.float32)
            ker[0, :] = 1.0 / k
            out = cv2.filter2D(out, -1, ker)
    if name == "car" and j < 4:  # flash on the reveal
        out = out + (255 - out) * (0.7 * (1 - j / 4))
    img = Image.fromarray(finish(out, i)).convert("RGBA")
    img.alpha_composite(overlays(seg, lt, dur, i / FPS))
    return np.asarray(img.convert("RGB"))


def main(source, matte, out, watch="black", only=None):
    cache_dir = os.path.dirname(os.path.abspath(matte.rstrip("/")))
    src = Source(source, matte, cache_dir)
    studio = Studio()
    tl, starts, total = build_timeline()
    if only is not None:  # preview stills
        for i in only:
            Image.fromarray(render_frame(src, studio, tl, i, watch, starts)).save(f"{out}_{i:04d}.png")
        return
    wav = out.rsplit(".", 1)[0] + "_sound.wav"
    soundtrack(wav, total, starts)
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264",
                            "-preset", "slow", "-crf", "17", "-maxrate", "12M", "-bufsize", "24M",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-shortest",
                            "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(len(tl)):
        enc.stdin.write(render_frame(src, studio, tl, i, watch, starts).tobytes())
        if i % 60 == 0:
            print(f"{i}/{len(tl)}", flush=True)
    enc.stdin.close()
    enc.wait()
    os.remove(wav)
    print(f"wrote {out}: {total:.1f}s")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    watch = "black"
    if "--watch" in sys.argv:
        watch = sys.argv[sys.argv.index("--watch") + 1]
        args = [a for a in args if a != watch]
    only = None
    if "--frames" in sys.argv:
        only = [int(x) for x in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        args = [a for a in args if not a[0].isdigit()]
    if len(args) != 3:
        sys.exit(__doc__)
    main(args[0], args[1], args[2], watch, only)
