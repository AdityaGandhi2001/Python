"""
Background swap (+ optional watch restyle) for a handheld unboxing clip.

Foreground = hands + forearms + card + car, found by combining
  * rembg (isnet-general-use) - salient object (card / car)
  * MediaPipe Hand Landmarker  - hand + forearm shape (covers the watch)
  * OpenCV GrabCut             - edge refinement from those seeds
and smoothed over time. The new background is generated (no stock images).

    python sth_bg_swap.py in.mp4 out.mp4 [--watch black|gold|silver|none]
"""

import math
import subprocess
import sys

import cv2
import mediapipe as mp
import numpy as np
from rembg import new_session, remove
from PIL import Image

MODELS = "sth_assets/models"
HAND_BONES = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), (5, 9), (9, 10), (10, 11),
              (11, 12), (9, 13), (13, 14), (14, 15), (15, 16), (13, 17), (17, 18), (18, 19), (19, 20), (0, 17)]
PALM = [0, 1, 5, 9, 13, 17]


class Segmenter:
    def __init__(self, fps):
        self.rembg = new_session("isnet-general-use")
        opts = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=f"{MODELS}/hand_landmarker.task"),
            running_mode=mp.tasks.vision.RunningMode.VIDEO, num_hands=2,
            min_hand_detection_confidence=0.3, min_tracking_confidence=0.3)
        self.hands = mp.tasks.vision.HandLandmarker.create_from_options(opts)
        self.fps, self.k, self.prev = fps, 0, None
        self.last_hands = []

    def hand_mask(self, rgb):
        h, w = rgb.shape[:2]
        res = self.hands.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)),
                                          int(self.k * 1000 / self.fps))
        m = np.zeros((h, w), np.uint8)
        hands = []
        for lms in res.hand_landmarks:
            p = np.array([(l.x * w, l.y * h) for l in lms], np.float32)
            hands.append(p)
            size = np.linalg.norm(p[0] - p[9])  # wrist -> middle knuckle
            th = max(6, int(size * 0.28))
            for a, b in HAND_BONES:
                cv2.line(m, tuple(p[a].astype(int)), tuple(p[b].astype(int)), 255, th)
            for i in (4, 8, 12, 16, 20):
                cv2.circle(m, tuple(p[i].astype(int)), th // 2 + 2, 255, -1)
            cv2.fillPoly(m, [cv2.convexHull(p[PALM].astype(np.int32))], 255)
            # forearm: from the wrist away from the knuckles to the frame edge (covers the watch)
            d = p[0] - p[9]
            d /= np.linalg.norm(d) + 1e-6
            end = p[0] + d * max(h, w) * 1.5
            cv2.line(m, tuple(p[0].astype(int)), tuple(end.astype(int)), 255, int(size * 0.7))
        self.last_hands = hands
        return m

    def __call__(self, rgb):
        h, w = rgb.shape[:2]
        sal = np.asarray(remove(Image.fromarray(rgb), session=self.rembg, only_mask=True)).astype(np.float32) / 255
        hm = self.hand_mask(rgb)
        self.k += 1
        sw, sh = w // 2, h // 2
        small = cv2.resize(rgb, (sw, sh), interpolation=cv2.INTER_AREA)
        sal_s = cv2.resize(sal, (sw, sh))
        hm_s = cv2.resize(hm, (sw, sh), interpolation=cv2.INTER_NEAREST) > 0
        hsv = cv2.cvtColor(small, cv2.COLOR_RGB2HSV).astype(np.float32)
        sat, val = hsv[..., 1] / 255, hsv[..., 2] / 255
        ycc = cv2.cvtColor(small, cv2.COLOR_RGB2YCrCb).astype(np.float32)
        skin = (ycc[..., 1] > 138) & (ycc[..., 1] < 182) & (ycc[..., 2] > 80) & (ycc[..., 2] < 135) & (val > 0.2)
        skin = cv2.morphologyEx(skin.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) > 0
        k = lambda n: np.ones((n, n), np.uint8)
        # learn this frame's ground colour from pixels far away from any foreground cue
        cue = ((sal_s > 0.25) | skin | hm_s).astype(np.uint8)
        far = cv2.dilate(cue, k(45)) == 0
        lab = cv2.cvtColor(small, cv2.COLOR_RGB2LAB).astype(np.float32)
        if far.sum() > 2000:
            ref = lab[far]
            lo, hi = np.percentile(ref, 3, axis=0), np.percentile(ref, 97, axis=0)
            pad = np.array([6, 4, 4], np.float32)
            asphalt = np.all((lab >= lo - pad) & (lab <= hi + pad), axis=2)
        else:
            asphalt = (sat < 0.17) & (val > 0.12) & (val < 0.74)
        sure = cv2.erode(((sal_s > 0.6) | skin).astype(np.uint8), k(7)) > 0
        maybe = (sal_s > 0.25) | skin | hm_s | ~asphalt
        near = cv2.dilate(((sal_s > 0.25) | skin | hm_s).astype(np.uint8), k(31)) > 0
        gc = np.full((sh, sw), cv2.GC_PR_BGD, np.uint8)
        gc[maybe] = cv2.GC_PR_FGD
        gc[asphalt & ~near] = cv2.GC_BGD
        gc[sure] = cv2.GC_FGD
        if (gc == cv2.GC_FGD).any() and (gc == cv2.GC_BGD).any():
            bgm, fgm = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
            cv2.grabCut(cv2.cvtColor(small, cv2.COLOR_RGB2BGR), gc, None, bgm, fgm, 3, cv2.GC_INIT_WITH_MASK)
            fg = np.isin(gc, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8)
        else:
            fg = sure.astype(np.uint8)
        # keep only regions connected to confident foreground (drops road lines / stray patches)
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, k(5))
        n, lab = cv2.connectedComponents(fg)
        good = np.unique(lab[sure & (fg > 0)])
        fg = np.isin(lab, good[good > 0]).astype(np.uint8)
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, k(9))
        fg = cv2.resize(fg.astype(np.float32), (w, h), interpolation=cv2.INTER_LINEAR)
        a = cv2.GaussianBlur(fg, (0, 0), 2.0)
        self.prev = a if self.prev is None else self.prev * 0.35 + a * 0.65
        return self.prev


def make_background(w, h, t):
    """Dark studio backdrop with a warm spotlight and slowly drifting bokeh."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    base = np.zeros((h, w, 3), np.float32)
    top, bot = np.array([18, 16, 22]), np.array([46, 34, 30])
    g = (yy / h)[..., None]
    base += top * (1 - g) + bot * g
    cx, cy = w * 0.5 + 30 * math.sin(t * 0.4), h * 0.42
    d = np.sqrt(((xx - cx) / (w * 0.75)) ** 2 + ((yy - cy) / (h * 0.55)) ** 2)
    base += (np.clip(1 - d, 0, 1) ** 1.6)[..., None] * np.array([120, 70, 35])
    rnd = np.random.default_rng(7)
    bok = np.zeros((h, w, 3), np.float32)
    for _ in range(26):
        x0, y0 = rnd.uniform(0, w), rnd.uniform(0, h * 0.75)
        r = rnd.uniform(18, 55)
        sp = rnd.uniform(6, 18)
        x = (x0 + sp * t) % (w + 120) - 60
        col = np.array([255, 150, 60]) if rnd.random() < 0.6 else np.array([90, 140, 255])
        cv2.circle(bok, (int(x), int(y0)), int(r), (col * rnd.uniform(0.12, 0.3)).tolist(), -1)
    bok = cv2.GaussianBlur(bok, (0, 0), 6)
    return np.clip(base + bok, 0, 255)


def restyle_watch(rgb, hands, alpha, style):
    """Restyle the watch: everything on the wrist that is foreground but not skin is the band."""
    if style == "none" or not hands:
        return rgb
    h, w = rgb.shape[:2]
    out = rgb.astype(np.float32)
    ycc = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCrCb).astype(np.float32)
    skin = (ycc[..., 1] > 136) & (ycc[..., 1] < 185) & (ycc[..., 2] > 78) & (ycc[..., 2] < 135)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
    gold = (hsv[..., 0] * 2 > 28) & (hsv[..., 0] * 2 < 62) & (hsv[..., 1] > 75)  # yellow metal, not skin
    skin &= ~gold
    skin = cv2.morphologyEx(skin.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    lum = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)[..., None]
    for p in hands:
        size = np.linalg.norm(p[0] - p[9])
        d = p[0] - p[9]
        d /= np.linalg.norm(d) + 1e-6
        c = p[0] + d * size * 0.5
        region = np.zeros((h, w), np.uint8)
        cv2.ellipse(region, tuple(c.astype(int)), (int(size * 1.4), int(size * 0.6)),
                    math.degrees(math.atan2(d[1], d[0])) + 90, 0, 360, 255, -1)
        band = (region > 0) & ~skin & (alpha > 0.6)
        band = cv2.morphologyEx(band.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        band = cv2.morphologyEx(band, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        m = cv2.GaussianBlur(band.astype(np.float32), (0, 0), 1.2)[..., None]
        if style == "black":  # dark steel: keeps the link detail and the shine
            new = lum * 0.28 + np.array([6, 7, 10]) + np.clip(lum - 185, 0, 70) * 1.3
        elif style == "gold":
            new = np.clip(lum * 1.05, 0, 255) * np.array([1.0, 0.8, 0.42])
        else:  # silver
            new = np.repeat(lum, 3, axis=2) * 0.97
        out = out * (1 - m) + new * m
    return np.clip(out, 0, 255).astype(np.uint8)


def main(src, dst, watch="black"):
    probe = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                     "stream=width,height,r_frame_rate", "-of", "csv=p=0", src]).decode().strip()
    w, h, fr = probe.split(",")
    w, h = int(w), int(h)
    num, den = fr.split("/")
    fps = float(num) / float(den)
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{w}x{h}", "-r", fr, "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a?",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-c:a", "copy", "-shortest", "-movflags", "+faststart", dst], stdin=subprocess.PIPE)
    seg = Segmenter(fps)
    k = 0
    while True:
        buf = dec.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        rgb = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        a = seg(rgb)
        fgimg = restyle_watch(rgb, seg.last_hands, a, watch).astype(np.float32)
        bg = make_background(w, h, k / fps)
        # soft contact shadow so the foreground sits in the scene
        sh = cv2.GaussianBlur(a, (0, 0), 18)
        sh = np.roll(np.roll(sh, 14, 0), 8, 1)[..., None]
        bg = bg * (1 - sh * 0.45)
        out = fgimg * a[..., None] + bg * (1 - a[..., None])
        enc.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
        k += 1
        if k % 60 == 0:
            print(f"{k} frames", flush=True)
    enc.stdin.close()
    enc.wait()
    seg.hands.close()
    print(f"wrote {dst} ({k} frames)")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    style = "black"
    if "--watch" in sys.argv:
        style = sys.argv[sys.argv.index("--watch") + 1]
        args = [a for a in args if a != style]
    if len(args) != 2:
        sys.exit(__doc__)
    main(args[0], args[1], style)
