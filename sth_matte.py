"""
Studio-quality matte for a handheld unboxing clip -> cached alpha sequence.

  object matte : BiRefNet (rembg "birefnet-general-lite") on every 2nd frame,
                 motion-propagated (DIS optical flow) to the frames between
  hand matte   : sth_bg_swap.Segmenter (skin + MediaPipe hands + GrabCut),
                 used only inside the hand / forearm / watch zone
  refinement   : guided filter on the image, flow-warped temporal smoothing

Writes <cache>/alpha_00000.png ... and <cache>/hands.json (hand landmarks per frame).

    python sth_matte.py in.mp4 cache_dir
"""

import json
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

import sth_bg_swap as B


def probe(src):
    s = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                 "stream=width,height,r_frame_rate", "-of", "csv=p=0", src]).decode().strip()
    w, h, fr = s.split(",")
    n, d = fr.split("/")
    return int(w), int(h), float(n) / float(d)


def frames(src, w, h):
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(w * h * 3)
        if len(b) < w * h * 3:
            break
        yield np.frombuffer(b, np.uint8).reshape(h, w, 3)
    p.wait()


class Flow:
    def __init__(self):
        self.dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)

    def warp(self, prev_rgb, cur_rgb, img):
        """Warp img (aligned with prev_rgb) onto cur_rgb."""
        g0 = cv2.cvtColor(prev_rgb, cv2.COLOR_RGB2GRAY)
        g1 = cv2.cvtColor(cur_rgb, cv2.COLOR_RGB2GRAY)
        f = self.dis.calc(g1, g0, None)  # backward flow: for each pixel in cur, where it was in prev
        h, w = g1.shape
        gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
        return cv2.remap(img, gx + f[..., 0], gy + f[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def hand_zone(hands, h, w):
    z = np.zeros((h, w), np.uint8)
    for p in hands:
        p = np.asarray(p, np.float32)
        size = np.linalg.norm(p[0] - p[9])
        cv2.fillPoly(z, [cv2.convexHull(p.astype(np.int32))], 255)
        d = p[0] - p[9]
        d /= np.linalg.norm(d) + 1e-6
        end = p[0] + d * max(h, w) * 1.5
        cv2.line(z, tuple(p[0].astype(int)), tuple(end.astype(int)), 255, int(size * 1.1))
    return cv2.dilate(z, np.ones((25, 25), np.uint8))


def main(src, cache):
    os.makedirs(cache, exist_ok=True)
    w, h, fps = probe(src)
    biref = new_session("birefnet-general-lite")
    seg = B.Segmenter(fps, use_rembg=False)  # hands come from skin + landmarks; saves memory
    flow = Flow()
    prev_rgb = prev_obj = prev_alpha = None
    hands_log = []
    for k, rgb in enumerate(frames(src, w, h)):
        # object matte
        if k % 2 == 0 or prev_obj is None:
            obj = np.asarray(remove(Image.fromarray(rgb), session=biref, only_mask=True)).astype(np.float32) / 255
        else:
            obj = flow.warp(prev_rgb, rgb, prev_obj)
        # hand matte (only trusted inside the hand / forearm zone, plus visible skin)
        seg.prev = None
        hand = seg(rgb)
        hands = [p.tolist() for p in seg.last_hands]
        ycc = cv2.cvtColor(rgb, cv2.COLOR_RGB2YCrCb)
        skin = cv2.inRange(ycc, (0, 138, 80), (255, 182, 135))
        skin = cv2.dilate(cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)), np.ones((21, 21), np.uint8))
        zone = (np.maximum(hand_zone(hands, h, w), skin) > 0).astype(np.float32)
        zone = cv2.GaussianBlur(zone, (0, 0), 6)
        a = np.maximum(obj, hand * zone)
        # edge refinement guided by the image
        a = cv2.ximgproc.guidedFilter(rgb, a.astype(np.float32), 6, 1e-4)
        a = np.clip(a, 0, 1)
        # temporal stabilisation: blend with the previous final matte warped to this frame
        if prev_alpha is not None:
            a = a * 0.7 + flow.warp(prev_rgb, rgb, prev_alpha) * 0.3
        # tidy: drop tiny islands
        b = (a > 0.5).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(b)
        small = np.zeros_like(b)
        for i in range(1, n):
            if st[i, cv2.CC_STAT_AREA] < 0.004 * h * w:
                small[lab == i] = 1
        a[cv2.dilate(small, np.ones((5, 5), np.uint8)) > 0] = 0
        cv2.imwrite(f"{cache}/alpha_{k:05d}.png", (a * 255).astype(np.uint8))
        hands_log.append(hands)
        prev_rgb, prev_obj, prev_alpha = rgb, obj, a
        if k % 25 == 0:
            print(f"{k} frames", flush=True)
            json.dump(hands_log, open(f"{cache}/hands.json", "w"))
    json.dump(hands_log, open(f"{cache}/hands.json", "w"))
    seg.hands.close()
    print(f"done: {len(hands_log)} frames -> {cache}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
