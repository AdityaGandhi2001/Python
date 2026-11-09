"""
Green-screen background for a face-cam STH reel.

Load the output as the background in Instagram / CapCut "Green Screen" and
talk in front of it. All content sits in the top ~60% of the frame so the
speaker (bottom of the frame) never covers it. Calm pacing (~4 s per car),
no music, no flashes - your voice is the soundtrack.

    python sth_greenscreen.py sth_assets out_dir
Writes out_dir/2027_STH_GreenScreen.mp4 and out_dir/2027_STH_GreenScreen_still.png
"""

import math
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

from sth_reveal_video import (CARS, F_BLACK, F_BLACK_I, F_XB, FPS, H, HIDDEN, TOTAL_MIXES, W, Car,
                              back_out, bg_frame, caption_box, draw_text_c, expo_out, fit, font,
                              make_grain, make_grid, make_vignette, marquee, p_, slam_text)

SAFE_BOTTOM = 1180  # keep everything above this line; the speaker stands below

T_INTRO = 3.5
T_CAR = 4.0
T_HIDDEN = 4.5
T_GRID = 6.0
TOTAL = T_INTRO + T_CAR * len(CARS) + T_HIDDEN + T_GRID
BLUE = (90, 130, 255)


def progress_dots(base, active):
    """15 dots across the top: revealed ones filled, current one highlighted."""
    d = ImageDraw.Draw(base)
    n, gap = TOTAL_MIXES, 52
    x0 = W / 2 - (n - 1) * gap / 2
    for k in range(n):
        x = x0 + k * gap
        r = 13 if k == active else 9
        if k < len(CARS):
            fill = (255, 255, 255, 255 if k <= active else 110)
        else:
            fill = BLUE + (120,)
        d.ellipse((x - r, 150 - r, x + r, 150 + r), fill=fill)


def bottom_fade(base):
    """Darken the speaker zone a little so a cut-out person pops."""
    g = Image.linear_gradient("L").resize((W, H - SAFE_BOTTOM + 200))
    g = g.point(lambda v: int(v * 0.55))
    shade = Image.new("RGBA", g.size, (0, 0, 0, 255))
    shade.putalpha(g)
    base.alpha_composite(shade, (0, SAFE_BOTTOM - 200))


def scene_intro(base, t):
    slam_text(base, W / 2, 380, "2027", F_BLACK_I, 280, (255, 255, 255), p_(t, 0.1, 0.4), start=1.8)
    slam_text(base, W / 2, 600, "SUPER TREASURE HUNTS", F_BLACK_I, 74, (255, 214, 0), p_(t, 0.6, 0.35))
    caption_box(base, W / 2, 760, f"{len(CARS)}/{TOTAL_MIXES} REVEALED", font(F_BLACK, 60), (0, 0, 0),
                (255, 255, 255), p_(t, 1.1, 0.35), emo="👀", rot=-2)


def scene_car(base, t, i, car):
    label, name, _, _ = CARS[i]
    acc = car.accent
    progress_dots(base, i)
    marquee(base, 520, label, font(F_BLACK_I, 220), acc, t * 120 + i * 300, outline=True, alpha=60)
    slam_text(base, W / 2, 300, label, F_BLACK_I, 170, acc, p_(t, 0, 0.3), start=1.6)

    pin = expo_out(p_(t, 0.1, 0.5))
    pout = clamp01((t - (T_CAR - 0.3)) / 0.3)
    side = 1 if i % 2 == 0 else -1
    dx = side * (1 - pin) * W - side * pout * W
    cx, cy = W / 2 + dx, 690 + 8 * math.sin(t * 2.2)
    x0, y0 = int(cx - car.img.width / 2), int(cy - car.img.height / 2)
    gp = car.glow_pad
    base.alpha_composite(car.glow, (x0 - gp, y0 - gp))
    base.alpha_composite(car.reflection, (x0, y0 + car.img.height - 6))
    base.alpha_composite(car.img, (x0, y0))

    pn = p_(t, 0.5, 0.35)
    if pn > 0:
        nf = fit(name, F_BLACK, 66, W - 100)
        lay = Image.new("RGBA", (W, 130), (0, 0, 0, 0))
        draw_text_c(lay, W / 2, 65, name, nf, (255, 255, 255), stroke=6, sfill=(0, 0, 0))
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * pn)))
        base.alpha_composite(lay, (0, int(960 + 20 * (1 - expo_out(pn)))))
    if label == "MIX ?":
        draw_text_c(base, W / 2, 1090, "mix not confirmed yet", font(F_XB, 34), (255, 255, 255, 160))


def clamp01(x):
    return max(0.0, min(1.0, x))


def tiles(base, t, cars, cover, top, start, step, tile_w=196, gap=12, cols=5):
    """15-slot grid (revealed + hidden), pops in one by one."""
    slots = [(c, CARS[k][0], c.accent) for k, c in enumerate(cars)] + \
        [(cover, f"MIX {h}", BLUE) for h in HIDDEN]
    tile_h = int(tile_w * 0.82)
    x0 = (W - (cols * tile_w + (cols - 1) * gap)) / 2
    d = ImageDraw.Draw(base)
    for k, (car, lab, acc) in enumerate(slots):
        pk = p_(t, start + k * step, 0.3)
        if pk <= 0:
            continue
        s = back_out(pk)
        r, c = divmod(k, cols)
        cx = x0 + c * (tile_w + gap) + tile_w / 2
        cy = top + r * (tile_h + gap) + tile_h / 2
        tw, th = tile_w * s, tile_h * s
        d.rounded_rectangle((cx - tw / 2, cy - th / 2, cx + tw / 2, cy + th / 2), radius=int(18 * s),
                            fill=acc + (70,), outline=acc + (230,), width=3)
        iw = tile_w * 0.86 * s
        im = car.img.resize((max(1, int(iw)), max(1, int(car.img.height * iw / car.img.width))),
                            Image.LANCZOS)
        base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2 - 16 * s)))
        draw_text_c(base, cx, cy + th / 2 - 24 * s, lab, font(F_BLACK_I, max(10, 28 * s)),
                    (255, 255, 255))


def scene_hidden(base, t, cover):
    progress_dots(base, len(CARS))
    slam_text(base, W / 2, 300, "STILL HIDDEN", F_BLACK_I, 120, (255, 255, 255), p_(t, 0, 0.3))
    small = cover.img.resize((250, int(cover.img.height * 250 / cover.img.width)), Image.LANCZOS)
    pos = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0.5), (1, 1.5), (1, 2.5)]
    for k, (letter, (r, c)) in enumerate(zip(HIDDEN, pos)):
        pk = p_(t, 0.4 + k * 0.25, 0.3)
        if pk <= 0:
            continue
        s = back_out(pk)
        cx, cy = 165 + c * 250, 560 + r * 260
        im = small.resize((max(1, int(small.width * s)), max(1, int(small.height * s))), Image.BICUBIC)
        base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
        draw_text_c(base, cx, cy + 85 * s, f"MIX {letter}", font(F_BLACK_I, max(10, 40 * s)), BLUE,
                    stroke=4, sfill=(0, 0, 0))
    caption_box(base, W / 2, 1060, f"{len(HIDDEN)} more coming", font(F_BLACK, 52), (0, 0, 0),
                (255, 255, 255), p_(t, 2.4, 0.3), emo="👀", rot=-2)


def scene_grid(base, t, cars, cover):
    slam_text(base, W / 2, 230, "2027 STH LINE-UP", F_BLACK_I, 96, (255, 255, 255), p_(t, 0, 0.3))
    caption_box(base, W / 2, 345, f"{len(CARS)}/{TOTAL_MIXES} so far", font(F_BLACK, 44), (0, 0, 0),
                (255, 214, 0), p_(t, 0.3, 0.3), rot=-2)
    tiles(base, t, cars, cover, top=420, start=0.6, step=0.18)


def render(t, cars, cover, grid, vignette, grain, fi):
    t_cars = T_INTRO + T_CAR * len(CARS)
    if t < T_INTRO:
        acc = (255, 40, 90)
    elif t < t_cars:
        acc = cars[int((t - T_INTRO) // T_CAR)].accent
    elif t < t_cars + T_HIDDEN:
        acc = (60, 90, 255)
    else:
        acc = (255, 214, 0)
    frame = bg_frame(t, acc, grid, glow_strength=0.8)
    if t < T_INTRO:
        scene_intro(frame, t)
    elif t < t_cars:
        k = int((t - T_INTRO) // T_CAR)
        scene_car(frame, t - T_INTRO - k * T_CAR, k, cars[k])
    elif t < t_cars + T_HIDDEN:
        scene_hidden(frame, t - t_cars, cover)
    else:
        scene_grid(frame, t - t_cars - T_HIDDEN, cars, cover)
    bottom_fade(frame)
    arr = np.asarray(frame.convert("RGB")).astype(np.float32) * vignette + grain[fi % len(grain)] * 0.6
    return np.clip(arr, 0, 255).astype(np.uint8)


def main(assets, out_dir):
    cars = [Car(f"{assets}/sth{i}.png", width=940) for i in range(len(CARS))]
    cover = Car(f"{assets}/sth{len(CARS)}.png", width=940)
    grid, vignette, grain = make_grid(), make_vignette(), make_grain()

    # still image: the full line-up, for the photo version of the green-screen effect
    still = bg_frame(0, (255, 214, 0), grid, glow_strength=0.8)
    scene_grid(still, 99, cars, cover)
    bottom_fade(still)
    still = np.clip(np.asarray(still.convert("RGB")).astype(np.float32) * vignette, 0, 255).astype(np.uint8)
    Image.fromarray(still).save(f"{out_dir}/2027_STH_GreenScreen_still.png")

    out = f"{out_dir}/2027_STH_GreenScreen.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
         "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE)
    n = int(TOTAL * FPS)
    for fi in range(n):
        ff.stdin.write(render(fi / FPS, cars, cover, grid, vignette, grain, fi).tobytes())
    ff.stdin.close()
    ff.wait()
    print(f"wrote {out}: {TOTAL:.1f}s")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
