"""
Prepare clean product cut-outs for the reel -> assets/products/cut/*.png

  * Ferrari box and Mustang: AI background removal (rembg, isnet-general-use).
  * Blister cards: flood-fill the studio background, then rebuild a crisp
    straight-edged card outline (OpenCV polygon fit) so glare / white plastic
    doesn't leave bites or white fringes.

    pip install "rembg[cpu]" opencv-python-headless
    python prepare_cutouts.py
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets", "products")
OUT = os.path.join(SRC, "cut")
def card_cutout(path, thresh=22):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    # 1) background = near-white region connected to the border
    work = im.copy()
    key = (255, 0, 255)
    for x in range(0, w, max(1, w // 20)):
        for y in (0, h - 1):
            if work.getpixel((x, y)) != key and min(work.getpixel((x, y))) > 200:
                ImageDraw.floodfill(work, (x, y), key, thresh=thresh)
    for y in range(0, h, max(1, h // 20)):
        for x in (0, w - 1):
            if work.getpixel((x, y)) != key and min(work.getpixel((x, y))) > 200:
                ImageDraw.floodfill(work, (x, y), key, thresh=thresh)
    a = np.asarray(work)
    fg = ~((a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255))
    m = Image.fromarray((fg * 255).astype(np.uint8))
    # 2) smooth outline: closing repairs bites taken out of light card edges
    k = max(5, (min(w, h) // 60) | 1)
    m = m.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.MinFilter(k))
    # 3) fill holes (anything not reachable from the border is foreground)
    pad = Image.new("L", (w + 2, h + 2), 0)
    pad.paste(m, (1, 1))
    ImageDraw.floodfill(pad, (0, 0), 128)
    m = pad.crop((1, 1, w + 1, h + 1)).point(lambda v: 0 if v == 128 else 255)
    # 4) open to drop specks, shave 1-2px white fringe, feather
    m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    m = m.filter(ImageFilter.MinFilter(3 if min(w, h) < 800 else 5))
    m = m.filter(ImageFilter.GaussianBlur(0.8))
    out = im.convert("RGBA")
    out.putalpha(m)
    return out.crop(m.getbbox())



def _median_1d(a, win):
    pad = win // 2
    ap = np.pad(a.astype(np.float32), pad, mode="edge")
    from numpy.lib.stride_tricks import sliding_window_view
    return np.median(sliding_window_view(ap, win), axis=1)


def single_card_cutout(path, win_frac=0.035):
    """For one card: rebuild the outline from smoothed row/column extents."""
    base = card_cutout(path)  # rough mask, already cropped
    a = np.asarray(base.getchannel("A")) > 128
    h, w = a.shape
    win = max(9, int(min(h, w) * win_frac) | 1)
    rows = np.where(a.any(1))[0]
    L = np.full(h, w, np.float32); R = np.full(h, -1, np.float32)
    for y in rows:
        xs = np.where(a[y])[0]; L[y], R[y] = xs[0], xs[-1]
    T = np.full(w, h, np.float32); B = np.full(w, -1, np.float32)
    for x in np.where(a.any(0))[0]:
        ys = np.where(a[:, x])[0]; T[x], B[x] = ys[0], ys[-1]
    L, R, T, B = (_median_1d(v, win) for v in (L, R, T, B))
    yy, xx = np.mgrid[:h, :w]
    m = (xx >= L[:, None]) & (xx <= R[:, None]) & (yy >= T[None, :]) & (yy <= B[None, :])
    mi = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))
    out = base.copy(); out.putalpha(mi)
    return out.crop(mi.getbbox())


def poly_card_cutout(path, eps_frac=0.004):
    """Fit a straight-edged polygon to the card outline (crisp, no bites)."""
    import cv2
    base = single_card_cutout(path, 0.05)
    a = (np.asarray(base.getchannel("A")) > 128).astype(np.uint8) * 255
    cs, _ = cv2.findContours(a, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    poly = cv2.approxPolyDP(c, eps_frac * cv2.arcLength(c, True), True)
    m = np.zeros_like(a)
    cv2.fillPoly(m, [poly], 255, lineType=cv2.LINE_AA)
    mi = Image.fromarray(m).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    out = base.copy(); out.putalpha(mi)
    return out.crop(mi.getbbox())


def ai_cutout(path, session):
    from rembg import remove
    out = remove(Image.open(path).convert("RGB"), session=session)
    a = out.getchannel("A").point(lambda v: 0 if v < 24 else v)
    out.putalpha(a)
    return out.crop(a.getbbox())


def main():
    from rembg import new_session
    os.makedirs(OUT, exist_ok=True)
    sess = new_session("isnet-general-use")
    jobs = {
        "ferrari": lambda: ai_cutout(os.path.join(SRC, "ferrari.webp"), sess),
        "mustang": lambda: ai_cutout(os.path.join(SRC, "mustang.jpg"), sess),
        "godzilla": lambda: poly_card_cutout(os.path.join(SRC, "godzilla.jpg")),
        "tfox": lambda: poly_card_cutout(os.path.join(SRC, "tfox.jpg")),
        "brian_set": lambda: card_cutout(os.path.join(SRC, "brian_set.jpg")),
    }
    for name, fn in jobs.items():
        fn().save(os.path.join(OUT, name + ".png"))
        print("saved", name)


if __name__ == "__main__":
    main()
