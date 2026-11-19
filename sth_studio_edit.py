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
BPM = 120
BEAT = 60 / BPM  # every cut lands on a beat; the reveal lands on a bar
# (name, src_start, src_end, beats, zoom_from, zoom_to)  - speed = source length / output length
EDL = [
    ("hook",   14.00, 14.55, 2, 1.28, 1.16),
    ("intro",   0.40,  2.40, 4, 1.00, 1.07),
    ("hero",    4.00,  4.90, 3, 1.02, 1.15),
    ("open",    2.50,  3.90, 2, 1.04, 1.06),
    ("tear",    5.00,  6.90, 2, 1.05, 1.10),
    ("tray",    8.00,  9.90, 3, 1.00, 1.08),   # 16 beats -> the reveal hits bar 5
    ("car",    12.50, 16.30, 8, 1.14, 1.00),
    ("end",    15.60, 15.60, 4, 1.00, 1.00),   # freeze for the end card
]


def build_timeline():
    """(segment, local t, segment length, source time) per output frame + segment start times."""
    tl, starts, t_out = [], [], 0.0
    for i, (name, s0, s1, beats, z0, z1) in enumerate(EDL):
        dur = beats * BEAT
        sp = (s1 - s0) / dur
        starts.append(t_out)
        n = int(round(dur * FPS))
        for j in range(n):
            lt = j / FPS
            src = s0 + lt * sp
            if sp >= 0.98:  # real-time / sped-up: whole source frames only (no blending)
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
        self.hands = self._fill_hand_gaps(json.load(open(f"{matte}/hands.json")))
        raw = f"{cache_dir}/frames_{self.w}x{self.h}.u8"
        need = self.n * self.w * self.h * 3
        if not os.path.exists(raw) or os.path.getsize(raw) < need:
            with open(raw, "wb") as f:
                subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-frames:v", str(self.n),
                                "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=f)
        self.frames = np.memmap(raw, np.uint8, "r", shape=(self.n, self.h, self.w, 3))
        self.dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        self._cache = {}

    @staticmethod
    def _fill_hand_gaps(hands, reach=12):
        """Bridge frames where the hand tracker lost the wrist, so the watch restyle never drops out."""
        known = [i for i, h in enumerate(hands) if h]
        out = []
        for i, h in enumerate(hands):
            if h or not known:
                out.append(h)
                continue
            j = min(known, key=lambda k: abs(k - i))
            out.append(hands[j] if abs(j - i) <= reach else [])
        return out

    def alpha(self, k):
        a = cv2.imread(f"{self.matte}/alpha_{k:05d}.png", cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255
        rgb = np.asarray(self.frames[k])
        # full-res skin matte (sun-lit skin included), only where it touches the subject
        ycc = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCrCb).astype(np.float32)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
        skin = ((ycc[..., 1] > 135) & (ycc[..., 1] < 190) & (ycc[..., 2] > 70) & (ycc[..., 2] < 135)
                & (hsv[..., 1] > 40) & (hsv[..., 2] > 60)).astype(np.uint8)
        skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        skin = cv2.morphologyEx(skin, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        # only skin in a narrow band around the existing matte (fills ragged hand edges,
        # cannot spread into warm-lit asphalt further away)
        band = cv2.dilate((a > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25)))
        add = cv2.morphologyEx(skin & band, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        a = np.maximum(a, add.astype(np.float32))
        # keep the main subject: drop pieces much smaller than the biggest one (stray roadside etc.)
        n, lab, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8))
        if n > 2:
            areas = st[1:, cv2.CC_STAT_AREA]
            drop = np.isin(lab, np.where(areas < areas.max() * 0.15)[0] + 1).astype(np.uint8)
            a[cv2.dilate(drop, np.ones((9, 9), np.uint8)) > 0] = 0
        # solid subject: fill holes / see-through patches inside the outline, keep soft outer edges
        hard = (a > 0.35).astype(np.uint8)
        hard = cv2.morphologyEx(hard, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        cnts, _ = cv2.findContours(hard, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        solid = np.zeros_like(hard)
        cv2.drawContours(solid, cnts, -1, 1, -1)
        inner = cv2.GaussianBlur(cv2.erode(solid, np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 2)
        a = np.maximum(a, inner)
        # choke ~1px so no ground colour survives on the edge, then a clean feather
        # snap the edge to real image edges (removes blocky / ragged outlines)
        a = cv2.ximgproc.guidedFilter(rgb, a.astype(np.float32), 5, 2e-3)
        a = np.clip((a - 0.2) / 0.7, 0, 1)
        a = cv2.erode(a, np.ones((3, 3), np.uint8))
        return cv2.GaussianBlur(a, (0, 0), 0.8)

    def at(self, t):
        """RGB, alpha and hands at source time t (flow-interpolated between frames)."""
        x = min(max(t * self.fps, 0), self.n - 1)
        k0 = int(math.floor(x))
        k1 = min(k0 + 1, self.n - 1)
        f = x - k0
        a0, i0 = self.alpha(k0), np.asarray(self.frames[k0])
        wm = self.watch[k0 if f < 0.5 else k1] if getattr(self, "watch", None) is not None else None
        hands = wm
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


# ---------------------------------------------------------------- watch track
def watch_mask(rgb, hands, alpha):
    """Band mask near each tracked wrist: foreground, not skin (gold metal counts as band)."""
    h, w = rgb.shape[:2]
    if not hands:
        return np.zeros((h, w), np.float32)
    ycc = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCrCb).astype(np.float32)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
    skin = (ycc[..., 1] > 136) & (ycc[..., 1] < 185) & (ycc[..., 2] > 78) & (ycc[..., 2] < 135)
    gold = (hsv[..., 0] * 2 > 28) & (hsv[..., 0] * 2 < 62) & (hsv[..., 1] > 75)
    skin = cv2.morphologyEx((skin & ~gold).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    out = np.zeros((h, w), np.uint8)
    for p in hands:
        p = np.asarray(p, np.float32)
        size = np.linalg.norm(p[0] - p[9])
        d = (p[0] - p[9]) / (np.linalg.norm(p[0] - p[9]) + 1e-6)
        c = p[0] + d * size * 0.5
        region = np.zeros((h, w), np.uint8)
        cv2.ellipse(region, tuple(c.astype(int)), (int(size * 1.4), int(size * 0.6)),
                    math.degrees(math.atan2(d[1], d[0])) + 90, 0, 360, 1, -1)
        band = (region > 0) & ~skin & (alpha > 0.6)
        # the band is metal: bright-ish and low-saturation, or gold
        metal = ((hsv[..., 1] < 70) & (hsv[..., 2] > 70)) | gold
        band &= metal
        band = cv2.morphologyEx(band.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        band = cv2.morphologyEx(band, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(band)
        if n > 1:  # keep the biggest piece = the watch
            out[lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])] = 1
    return out.astype(np.float32)


def grow_band(rgb, seed, alpha):
    """Extend a partial watch mask into the connected metal links around it."""
    ycc = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCrCb).astype(np.float32)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
    gold = (hsv[..., 0] * 2 > 28) & (hsv[..., 0] * 2 < 62) & (hsv[..., 1] > 75)
    skin = (ycc[..., 1] > 136) & (ycc[..., 1] < 185) & (ycc[..., 2] > 78) & (ycc[..., 2] < 135) & ~gold
    metal = (((hsv[..., 1] < 70) & (hsv[..., 2] > 60)) | gold | (hsv[..., 2] < 60)) & ~skin & (alpha > 0.6)
    near = cv2.dilate(seed, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (45, 45))) > 0
    cand = cv2.morphologyEx((metal & near).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lab = cv2.connectedComponents(np.maximum(cand, seed))
    hit = np.unique(lab[seed > 0])
    return np.isin(lab, hit[hit > 0]).astype(np.uint8)


def build_watch_track(src, cache):
    """Watch masks for every frame: detected where the wrist is tracked, carried through the gaps
    with optical flow (forward + backward), so the restyle never drops out."""
    if os.path.exists(cache):
        return np.load(cache)["m"]
    n = src.n
    det = [watch_mask(np.asarray(src.frames[k]), src.hands[k], src.alpha(k)) for k in range(n)]
    ok = [m.sum() > 250 for m in det]
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    gx, gy = np.meshgrid(np.arange(src.w, dtype=np.float32), np.arange(src.h, dtype=np.float32))

    def carry(order):
        res, prev, age = [None] * n, None, 99
        for k in order:
            if ok[k]:
                prev, age = det[k], 0
            elif prev is not None and age < 45:
                g_prev = cv2.cvtColor(np.asarray(src.frames[last]), cv2.COLOR_RGB2GRAY)
                g_cur = cv2.cvtColor(np.asarray(src.frames[k]), cv2.COLOR_RGB2GRAY)
                f = dis.calc(g_cur, g_prev, None)
                prev = cv2.remap(prev, gx + f[..., 0], gy + f[..., 1], cv2.INTER_LINEAR)
                prev = prev * (src.alpha(k) > 0.5)
                age += 1
            else:
                prev = None
            res[k] = prev
            last = k
        return res

    fw, bw = carry(range(n)), carry(range(n - 1, -1, -1))
    m = np.zeros((n, src.h, src.w), np.uint8)
    for k in range(n):
        a = fw[k] if fw[k] is not None else 0
        b = bw[k] if bw[k] is not None else 0
        seed = (np.maximum(a, b) > 0.4).astype(np.uint8)
        if seed.any():
            seed = grow_band(np.asarray(src.frames[k]), seed, src.alpha(k))
        m[k] = seed * 255
    np.savez_compressed(cache, m=m)
    return m


def recolor_watch(rgb, mask, style):
    if style == "none" or mask is None or not mask.any():
        return rgb
    m = cv2.GaussianBlur(mask.astype(np.float32) / 255, (0, 0), 1.2)[..., None]
    lum = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)[..., None]
    if style == "black":
        new = lum * 0.28 + np.array([6, 7, 10]) + np.clip(lum - 185, 0, 70) * 1.3
    elif style == "gold":
        new = np.clip(lum * 1.05, 0, 255) * np.array([1.0, 0.8, 0.42])
    else:
        new = np.repeat(lum, 3, axis=2) * 0.97
    return np.clip(rgb.astype(np.float32) * (1 - m) + new * m, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- compositing
def decontaminate(rgb, a):
    """Replace edge colours (which carry the old asphalt) with nearby interior foreground colour."""
    inner = (a > 0.96).astype(np.float32)
    num = cv2.GaussianBlur(rgb.astype(np.float32) * inner[..., None], (0, 0), 4)
    den = cv2.GaussianBlur(inner, (0, 0), 4)[..., None] + 1e-4
    fill = num / den
    wgt = np.clip((a - 0.6) / 0.36, 0, 1)[..., None]
    return rgb.astype(np.float32) * wgt + fill * (1 - wgt)


class Studio:
    """Product-shoot studio: warm mid-tone seamless backdrop, orange glow behind the subject,
    lit floor with a soft horizon, and a key light that follows the subject."""

    def __init__(self):
        yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
        self.yy, self.xx = yy, xx
        g = yy / OH
        horizon = 0.74
        wall_top, wall_mid = np.array([70, 64, 60]), np.array([104, 94, 86])
        floor_far, floor_near = np.array([128, 116, 104]), np.array([88, 80, 74])
        gw = np.clip(g / horizon, 0, 1)[..., None]
        wall = wall_top * (1 - gw) + wall_mid * gw
        fz = np.clip((g - horizon) / (1 - horizon), 0, 1)[..., None]
        floor = floor_far * (1 - fz) + floor_near * fz
        t = np.clip((g - horizon) / 0.05 + 0.5, 0, 1)[..., None]  # curved cyc join
        base = wall * (1 - t) + floor * t
        base += np.exp(-((g - horizon) / 0.025) ** 2)[..., None] * np.array([14, 12, 10])  # sheen on the curve
        # side falloff so the frame has shape
        side = (np.abs(xx - OW / 2) / (OW / 2)) ** 2.2
        base *= (1 - side * 0.38)[..., None]
        rng = np.random.default_rng(2)
        base += cv2.GaussianBlur(rng.normal(0, 1.8, (OH, OW)).astype(np.float32), (0, 0), 1.0)[..., None]
        self.base = base.astype(np.float32)
        self.key = np.array([OW * 0.5, OH * 0.45], np.float32)

    def frame(self, centroid):
        self.key = self.key * 0.9 + np.asarray(centroid, np.float32) * 0.1
        cx, cy = self.key
        # orange backlight glow right behind the subject (product-shot halo)
        d = np.sqrt(((self.xx - cx) / (OW * 0.55)) ** 2 + ((self.yy - (cy - OH * 0.05)) / (OH * 0.36)) ** 2)
        glow = (np.clip(1 - d, 0, 1) ** 2.2)[..., None] * np.array([150, 82, 30])
        # soft top key
        d2 = np.sqrt(((self.xx - cx) / (OW * 0.9)) ** 2 + ((self.yy - OH * 0.12) / (OH * 0.5)) ** 2)
        key = (np.clip(1 - d2, 0, 1) ** 2)[..., None] * np.array([40, 38, 36])
        return self.base + glow + key


def composite(rgb, a, watch_m, studio, zoom, watch):
    rgb = recolor_watch(rgb, watch_m, watch)
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


def _emoji(ch, h):
    ef = ImageFont.truetype(F_EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=ef, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)


def kinetic(lay, txt, fp, size, col, y, t, t_in, t_out=None, track=0, shadow=True):
    """Headline whose letters rise into place through a mask (masked slide-up), then slide out."""
    f = font(fp, size)
    widths = [f.getlength(c) for c in txt]
    total = sum(widths) + track * (len(txt) - 1)
    x = OW / 2 - total / 2
    asc, desc = f.getmetrics()
    hgt = asc + desc
    strip = Image.new("RGBA", (OW, hgt + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(strip)
    for i, (c, cw) in enumerate(zip(txt, widths)):
        p = ease((t - t_in - i * 0.025) / 0.32)
        if t_out is not None:
            p_out = ease((t - t_out - i * 0.015) / 0.22)
        else:
            p_out = 0
        dy = (1 - p) * hgt + p_out * -hgt
        if p > 0:
            d.text((x, 10 + dy), c, font=f, fill=col + (255,))
        x += cw + track
    if shadow:
        sh = strip.copy()
        sh = Image.fromarray(cv2.GaussianBlur(np.asarray(sh), (0, 0), 10))
        sh = Image.merge("RGBA", (*Image.new("RGB", sh.size, (0, 0, 0)).split(), sh.getchannel("A").point(lambda v: v * 0.55)))
        lay.alpha_composite(sh, (0, int(y) + 6))
    lay.alpha_composite(strip, (0, int(y)))


def label(lay, txt, y, t, t_in, t_out=None, col=(235, 235, 235)):
    """Small tracked label with an orange rule underneath."""
    p = ease((t - t_in) / 0.35) * (1 - (ease((t - t_out) / 0.2) if t_out is not None else 0))
    if p <= 0:
        return
    f = font(F_BOLD, 34)
    track = 9
    w = sum(f.getlength(c) for c in txt) + track * (len(txt) - 1)
    d = ImageDraw.Draw(lay)
    x = OW / 2 - w / 2
    for c in txt:
        d.text((x, y), c, font=f, fill=col + (int(255 * p),))
        x += f.getlength(c) + track
    rw = 90 * p
    d.rectangle((OW / 2 - rw, y + 52, OW / 2 + rw, y + 56), fill=ORANGE + (int(255 * p),))


def spec(lay, txt, y, t, t_in, t_out, emo=None, accent=False):
    """Spec line: orange tick + text, slides in from the left on its beat."""
    p = ease((t - t_in) / 0.3) * (1 - ease((t - t_out) / 0.2))
    if p <= 0:
        return
    f = font(F_XB, 44)
    tw = f.getlength(txt)
    e = _emoji(emo, 46) if emo else None
    w = 22 + 24 + tw + (e.width + 14 if e else 0) + 30
    x0 = OW / 2 - w / 2 - (1 - p) * 80
    a = int(255 * p)
    d = ImageDraw.Draw(lay)
    bg = ORANGE if accent else (14, 14, 16)
    d.rounded_rectangle((x0, y, x0 + w, y + 78), radius=18, fill=bg + (int(a * 0.88),))
    d.rectangle((x0 + 22, y + 22, x0 + 30, y + 56), fill=((0, 0, 0) if accent else ORANGE) + (a,))
    d.text((x0 + 46, y + 39), txt, font=f, fill=((0, 0, 0) if accent else (255, 255, 255)) + (a,), anchor="lm")
    if e is not None:
        e = e.copy()
        e.putalpha(e.getchannel("A").point(lambda v: int(v * p)))
        lay.alpha_composite(e, (int(x0 + 46 + tw + 14), int(y + 16)))


def overlays(seg, lt, dur, t_global):
    name = EDL[seg][0]
    lay = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    W_, O_ = (255, 255, 255), ORANGE
    b = BEAT
    if name == "hook":
        kinetic(lay, "THE SUPRA", F_BLACK_I, 150, W_, 230, lt, 0.0, dur - 0.2)
        kinetic(lay, "IS HERE.", F_BLACK_I, 150, O_, 390, lt, b * 0.5, dur - 0.2)
    elif name == "intro":
        label(lay, "HOT WHEELS PREMIUM", 210, lt, 0.1, dur - 0.25)
        kinetic(lay, "FAST & FURIOUS", F_BLACK_I, 112, W_, 280, lt, 0.2, dur - 0.3)
    elif name == "hero":
        kinetic(lay, "25 YEARS", F_BLACK_I, 140, O_, 1500, lt, 0.1, dur - 0.25)
        label(lay, "OF FAST & FURIOUS", 1680, lt, 0.3, dur - 0.25)
    elif name == "open":
        kinetic(lay, "UNBOXING", F_BLACK_I, 104, W_, 220, lt, 0.0, track=10)
    elif name == "tear":
        kinetic(lay, "UNBOXING", F_BLACK_I, 104, W_, 220, lt, -5, dur - 0.2, track=10)
    elif name == "tray":
        label(lay, "MOMENT OF TRUTH", 230, lt, 0.2, dur - 0.2)
    elif name == "car":
        label(lay, "TOYOTA", 200, lt, b * 0.25, dur - 0.3)
        kinetic(lay, "SUPRA", F_BLACK_I, 230, O_, 260, lt, b * 0.25, dur - 0.3, track=4)
        spec(lay, "Metal / Metal", 1500, lt, b * 2, dur - 0.3)
        spec(lay, "Real Riders tires", 1600, lt, b * 3, dur - 0.3)
        spec(lay, "Brian's iconic Supra", 1700, lt, b * 4, dur - 0.3, emo="🧡", accent=True)
    elif name == "end":
        kinetic(lay, "WOULD YOU", F_BLACK_I, 124, W_, 270, lt, 0.05)
        kinetic(lay, "COP THIS?", F_BLACK_I, 124, O_, 420, lt, b * 0.5)
        spec(lay, "comment below", 1560, lt, b * 1.5, 99, emo="👇")
        spec(lay, "follow for more drops", 1660, lt, b * 2, 99, emo="🔥", accent=True)
    return lay


# ---------------------------------------------------------------- audio
def soundtrack(path, total, starts):
    """Original 120 BPM track: filtered intro groove, riser into a drop on the reveal (a bar line),
    plucked arpeggio + chords, sidechained pads, and sound design on every cut."""
    sr = 44100
    n = int(total * sr) + sr
    mix = np.zeros(n)
    duck = np.ones(n)
    rng = np.random.default_rng(21)

    def add(sig, at, g=1.0, target=None):
        target = mix if target is None else target
        i = int(round(at * sr))
        if 0 <= i < n:
            j = min(n, i + len(sig))
            target[i:j] += sig[: j - i] * g

    def env(m, k):
        return np.exp(-np.arange(m) / sr * k)

    def kick():
        m = int(0.45 * sr)
        tt = np.arange(m) / sr
        ph = 2 * np.pi * np.cumsum(42 + 120 * np.exp(-tt * 32)) / sr
        click = rng.standard_normal(m) * np.exp(-tt * 400) * 0.3
        return np.tanh(1.6 * np.sin(ph)) * env(m, 7) + click

    def clap():
        m = int(0.3 * sr)
        nz = rng.standard_normal(m)
        nz -= np.convolve(nz, np.ones(12) / 12, "same")
        e = env(m, 16)
        for dd in (0.0, 0.01, 0.021):
            k = int(dd * sr)
            e[k:] += env(m - k, 70) * 0.7
        return nz * e * 0.42

    def hat(o=False):
        m = int((0.22 if o else 0.05) * sr)
        nz = rng.standard_normal(m)
        nz -= np.convolve(nz, np.ones(3) / 3, "same")
        return nz * env(m, 12 if o else 75) * 0.13

    def pluck(f, d=0.35):
        m = int(d * sr)
        tt = np.arange(m) / sr
        s = np.sign(np.sin(2 * np.pi * f * tt)) * 0.35 + np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)
        s = np.convolve(s, np.ones(6) / 6, "same")
        return s * env(m, 9) * 0.11

    def bass(f, d):
        m = int(d * sr)
        tt = np.arange(m) / sr
        s = np.tanh(2.2 * (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)))
        return s * np.minimum(1, tt / 0.008) * np.minimum(1, (d - tt) / 0.03).clip(0, 1) * 0.42

    def pad(freqs, d):
        m = int(d * sr)
        tt = np.arange(m) / sr
        s = sum(np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 1.005 * tt) for f in freqs)
        return s * np.minimum(1, tt / 0.3) * np.clip((d - tt) / 0.3, 0, 1) * 0.035

    def whoosh(d=0.32):
        m = int(d * sr)
        nz = rng.standard_normal(m)
        out = np.zeros(m)
        for i in range(0, m, 256):
            k = 2 + int((i / m) * 28)
            seg_ = nz[i:i + 256]
            out[i:i + 256] = seg_ - np.convolve(seg_, np.ones(k) / k, "same")
        return out * np.sin(np.linspace(0, np.pi, m)) ** 2 * 0.32

    def riser(d):
        m = int(d * sr)
        tt = np.arange(m) / sr
        sw = np.sin(2 * np.pi * np.cumsum(180 + 2000 * (tt / d) ** 2.2) / sr)
        nz = rng.standard_normal(m)
        nz -= np.convolve(nz, np.ones(5) / 5, "same")
        return (sw * 0.22 + nz * 0.16) * (tt / d) ** 2.2

    def impact():
        m = int(1.6 * sr)
        tt = np.arange(m) / sr
        boom = np.sin(2 * np.pi * np.cumsum(36 + 95 * np.exp(-tt * 6)) / sr) * np.exp(-tt * 2.2)
        return boom * 1.1 + rng.standard_normal(m) * np.exp(-tt * 14) * 0.35

    def tear(d):
        m = int(d * sr)
        nz = rng.standard_normal(m)
        crackle = (rng.random(m) < 0.025) * rng.standard_normal(m) * 3
        s = np.convolve(nz + crackle, np.ones(4) / 4, "same")
        return s * np.sin(np.linspace(0, np.pi, m)) * 0.1

    names = [e[0] for e in EDL]
    t_car, t_end, t_tear = starts[names.index("car")], starts[names.index("end")], starts[names.index("tear")]
    # A minor: Am - F - C - G
    chords = [(110.0, [220.0, 261.6, 329.6]), (87.3, [174.6, 220.0, 261.6]),
              (130.8, [261.6, 329.6, 392.0]), (98.0, [196.0, 246.9, 293.7])]
    nbeats = int(round(total / BEAT))
    for bt in range(nbeats):
        at = bt * BEAT
        bar, pos = divmod(bt, 4)
        root, tri = chords[bar % 4]
        drop = at >= t_car - 1e-6
        outro = at >= t_end + BEAT * 2
        if outro:
            continue
        # arpeggio throughout (filtered feel before the drop: quieter)
        for s16 in range(4):
            note = tri[(pos * 4 + s16) % 3] * (2 if s16 % 2 else 1)
            add(pluck(note), at + s16 * BEAT / 4, 1.0 if drop else 0.55)
        if pos == 0:
            add(pad(tri, BEAT * 4), at, 1.3 if drop else 0.9)
        if not drop:
            if pos in (0, 2):
                add(kick(), at, 0.65)
            add(hat(), at + BEAT / 2)
            if bt >= 12:  # build: 16ths in the last bar before the drop
                for k in range(4):
                    add(hat(), at + k * BEAT / 4, 0.6 + 0.1 * k)
        else:
            add(kick(), at)
            d = np.ones(int(0.25 * sr))
            d[:] = 1 - 0.6 * np.exp(-np.arange(len(d)) / sr * 14)
            i0 = int(at * sr)
            duck[i0:i0 + len(d)] = np.minimum(duck[i0:i0 + len(d)], d[: max(0, min(len(d), n - i0))])
            if pos in (1, 3):
                add(clap(), at, 0.8)
            for k in range(2):
                add(hat(), at + k * BEAT / 2)
            if pos == 3:
                add(hat(True), at + BEAT / 2)
            add(bass(root / 2, BEAT * 0.9), at)
            add(bass(root / 2, BEAT * 0.4), at + BEAT * 0.75, 0.7)
    mix *= duck
    # sound design on every cut
    for i, st in enumerate(starts[1:], 1):
        if names[i] not in ("car",):
            add(whoosh(), st - 0.16, 0.75)
    add(impact(), 0.0, 0.55)
    _, ts0, ts1, tb, _, _ = EDL[names.index("tear")]
    add(tear(tb * BEAT), t_tear, 1.0)
    add(riser(BEAT * 6), t_car - BEAT * 6, 0.9)
    add(impact(), t_car, 1.0)
    mix = mix[: int(total * sr)]
    mix = np.tanh(mix * 1.15)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
    f = int(0.6 * sr)
    mix[-f:] *= np.linspace(1, 0, f)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((mix * 32767).astype(np.int16).tobytes())


# ---------------------------------------------------------------- render
def zoom_blur(img, strength, center=(OW / 2, OH * 0.47)):
    """Radial zoom blur (average of progressively scaled copies)."""
    acc = img.astype(np.float32).copy()
    steps = 6
    for k in range(1, steps + 1):
        z = 1 + strength * k / steps
        M = cv2.getRotationMatrix2D(center, 0, z)
        acc += cv2.warpAffine(img, M, (OW, OH), borderMode=cv2.BORDER_REFLECT)
    return acc / (steps + 1)


def render_frame(src, studio, tl, i, watch, starts):
    seg, lt, dur, st = tl[i]
    name, s0, s1, beats, z0, z1 = EDL[seg]
    j = int(round(lt * FPS))
    zoom = z0 + (z1 - z0) * ease(lt / max(dur, 1e-6)) if name != "end" else 1.0 + 0.03 * ease(lt / dur)
    if j < 4 and name in ("intro", "hero"):  # punch-in on the cut
        zoom *= 1 + 0.06 * (1 - j / 4)
    rgb, a, hands = src.at(st)
    out = composite(rgb, a, hands, studio, zoom, watch)
    if name == "end":  # soften the freeze so the end-card text reads
        out = cv2.GaussianBlur(out, (0, 0), 1 + 6 * ease(lt / 0.5)) * (1 - 0.25 * ease(lt / 0.5))
    if name in ("open", "tear", "tray") and j < 3:  # whip-pan into the unboxing beats
        k = int(64 - j * 22)
        ker = np.full((1, k), 1.0 / k, np.float32)
        out = cv2.filter2D(out, -1, ker)
    if name == "car" and j < 6:  # the drop: flash + zoom blur
        out = zoom_blur(out, 0.18 * (1 - j / 6))
        out = out + (255 - out) * (0.75 * max(0, 1 - j / 4))
    img = Image.fromarray(finish(out, i)).convert("RGBA")
    img.alpha_composite(overlays(seg, lt, dur, i / FPS))
    return np.asarray(img.convert("RGB"))


def main(source, matte, out, watch="black", only=None):
    cache_dir = os.path.dirname(os.path.abspath(matte.rstrip("/")))
    src = Source(source, matte, cache_dir)
    src.watch = build_watch_track(src, f"{cache_dir}/watch_track.npz")
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
