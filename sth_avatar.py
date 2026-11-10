"""
Memoji-style cartoon avatar (drawn with Pillow, no AI models).

Look: curly black hair, thin rectangular glasses, full beard + moustache,
open white shirt and a bead necklace. The mouth opens with the voice level,
the eyes blink, and the head bobs/tilts slightly.

    from sth_avatar import Avatar
    av = Avatar()
    rgba = av.frame(t, mouth=0.0..1.0)   # 1080 x 1300 RGBA image
"""

import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 2  # supersampling factor for smooth edges
AW, AH = 1080, 1300  # output size of the avatar layer

SKIN = (198, 140, 100)
SKIN_DARK = (160, 104, 70)
SKIN_LIGHT = (226, 175, 135)
HAIR = (28, 22, 20)
BEARD = (34, 26, 22)
SHIRT = (246, 244, 238)
SHIRT_SHADE = (214, 210, 202)
FRAME = (40, 40, 44)
IRIS = (70, 44, 28)


def radial_shade(size, center, radius, inner, outer):
    """RGBA radial gradient (inner colour at centre, outer at radius)."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.clip(np.sqrt((xx - center[0]) ** 2 + (yy - center[1]) ** 2) / radius, 0, 1)[..., None]
    col = np.array(inner) * (1 - d) + np.array(outer) * d
    a = np.full((h, w, 1), 255)
    return Image.fromarray(np.concatenate([col, a], 2).astype(np.uint8), "RGBA")


def masked(fill_img, mask):
    out = fill_img.copy()
    out.putalpha(mask)
    return out


class Avatar:
    def __init__(self, seed=4):
        self.rnd = random.Random(seed)
        # pre-generate curl positions so the hair doesn't shimmer
        self.curls = []
        for _ in range(140):
            a = self.rnd.uniform(math.pi * 0.95, math.pi * 2.05)
            r = self.rnd.uniform(0.75, 1.08)
            self.curls.append((a, r, self.rnd.uniform(30, 52)))
        self.blinks = sorted(self.rnd.uniform(0, 60) for _ in range(30))
        self._body = self._draw_body()

    # ------------------------------------------------------------- static parts
    def _draw_body(self):
        W, H = AW * SS, AH * SS
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cx = W // 2
        neck_top = int(H * 0.60)
        # neck
        d.rounded_rectangle((cx - 120 * SS, neck_top - 80 * SS, cx + 120 * SS, neck_top + 200 * SS),
                            radius=60 * SS, fill=SKIN_DARK)
        # shoulders / shirt
        d.rounded_rectangle((cx - 470 * SS, neck_top + 110 * SS, cx + 470 * SS, H + 200 * SS),
                            radius=260 * SS, fill=SHIRT)
        # open collar V with chest skin
        d.polygon([(cx - 130 * SS, neck_top + 90 * SS), (cx + 130 * SS, neck_top + 90 * SS),
                   (cx, neck_top + 400 * SS)], fill=SKIN_DARK)
        # collar flaps
        d.polygon([(cx - 135 * SS, neck_top + 80 * SS), (cx - 250 * SS, neck_top + 150 * SS),
                   (cx - 40 * SS, neck_top + 330 * SS)], fill=SHIRT_SHADE)
        d.polygon([(cx + 135 * SS, neck_top + 80 * SS), (cx + 250 * SS, neck_top + 150 * SS),
                   (cx + 40 * SS, neck_top + 330 * SS)], fill=SHIRT_SHADE)
        # necklace (thin cord + dark red bead)
        d.arc((cx - 115 * SS, neck_top + 20 * SS, cx + 115 * SS, neck_top + 300 * SS), 20, 160,
              fill=(110, 40, 30), width=5 * SS)
        d.ellipse((cx - 26 * SS, neck_top + 270 * SS, cx + 26 * SS, neck_top + 322 * SS), fill=(92, 36, 28))
        d.ellipse((cx - 12 * SS, neck_top + 280 * SS, cx + 2 * SS, neck_top + 294 * SS), fill=(150, 80, 60))
        # soft shading on the shirt
        shade = radial_shade((W, H), (cx, H * 1.05), W * 0.6, (0, 0, 0), (60, 60, 60))
        g = Image.new("L", (W, H), 0)
        ImageDraw.Draw(g).rounded_rectangle((cx - 470 * SS, neck_top + 110 * SS, cx + 470 * SS, H + 200 * SS),
                                            radius=260 * SS, fill=40)
        img.alpha_composite(masked(shade, g))
        return img

    # ------------------------------------------------------------- head
    def _head(self, mouth, blink):
        if not hasattr(self, "_head_base"):
            self._head_base = self._draw_head_base()
        img = self._head_base.copy()
        W, H = img.size
        cx, cy = W // 2, int(H * 0.52)
        fw, fh = 300 * SS, 380 * SS
        d = ImageDraw.Draw(img)
        return self._features(img, d, cx, cy, fw, fh, mouth, blink)

    def _draw_head_base(self):
        W, H = 820 * SS, 980 * SS
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cx, cy = W // 2, int(H * 0.52)
        fw, fh = 300 * SS, 380 * SS  # face half-width / half-height

        # back hair volume
        for a, r, s in self.curls:
            x = cx + math.cos(a) * fw * r * 1.12
            y = cy - 40 * SS + math.sin(a) * fh * r * 0.95
            s *= SS
            d.ellipse((x - s, y - s, x + s, y + s), fill=HAIR)

        # ears
        for sgn in (-1, 1):
            ex = cx + sgn * (fw - 6 * SS)
            d.ellipse((ex - 55 * SS, cy - 40 * SS, ex + 55 * SS, cy + 110 * SS), fill=SKIN_DARK)
            d.ellipse((ex - 30 * SS, cy - 10 * SS, ex + 30 * SS, cy + 80 * SS), fill=SKIN)

        # face shape with 3D shading
        face_mask = Image.new("L", (W, H), 0)
        fm = ImageDraw.Draw(face_mask)
        fm.ellipse((cx - fw, cy - fh, cx + fw, cy + fh * 0.98), fill=255)
        fm.rounded_rectangle((cx - fw * 0.96, cy - fh * 0.2, cx + fw * 0.96, cy + fh * 0.78),
                             radius=int(fw * 0.7), fill=255)
        face = radial_shade((W, H), (cx - fw * 0.25, cy - fh * 0.35), fw * 1.7, SKIN_LIGHT, SKIN_DARK)
        img.alpha_composite(masked(face, face_mask))
        d = ImageDraw.Draw(img)

        # front hairline curls (forehead)
        for k in range(16):
            a = math.pi * (1.08 + 0.84 * k / 15)
            x = cx + math.cos(a) * fw * 0.88
            y = cy - fh * 0.62 + math.sin(a) * fh * 0.3
            s = (46 + 10 * math.sin(k * 1.7)) * SS
            d.ellipse((x - s, y - s, x + s, y + s), fill=HAIR)
        d.ellipse((cx - fw * 0.75, cy - fh * 1.08, cx + fw * 0.75, cy - fh * 0.62), fill=HAIR)

        # beard: covers jaw, chin and cheeks
        # beard = face minus the upper-face skin area -> sideburns + curved cheek line
        skin_area = Image.new("L", (W, H), 0)
        ImageDraw.Draw(skin_area).ellipse((cx - fw * 0.84, cy - fh * 1.35, cx + fw * 0.84, cy + fh * 0.40),
                                          fill=255)
        beard = Image.fromarray(np.minimum(np.asarray(face_mask), 255 - np.asarray(skin_area)))
        # extend slightly below the face outline for a fuller beard
        chin = Image.new("L", (W, H), 0)
        ImageDraw.Draw(chin).ellipse((cx - fw * 0.8, cy + fh * 0.35, cx + fw * 0.8, cy + fh * 1.03), fill=255)
        beard = Image.fromarray(np.maximum(np.asarray(beard), np.asarray(chin)))
        # rough edge so it reads as hair
        beard = beard.filter(ImageFilter.GaussianBlur(4 * SS)).point(lambda v: 255 if v > 110 else 0)
        img.alpha_composite(masked(Image.new("RGBA", (W, H), BEARD + (255,)), beard))
        d = ImageDraw.Draw(img)

        # soft blush on the cheeks
        blush = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(blush)
        for sgn in (-1, 1):
            bx = cx + sgn * fw * 0.5
            bd.ellipse((bx - 70 * SS, cy + fh * 0.05, bx + 70 * SS, cy + fh * 0.25), fill=(220, 120, 100, 60))
        img.alpha_composite(blush.filter(ImageFilter.GaussianBlur(14 * SS)))
        d = ImageDraw.Draw(img)

        # nose
        d.ellipse((cx - 46 * SS, cy + fh * 0.08, cx + 46 * SS, cy + fh * 0.32), fill=SKIN_DARK)
        d.ellipse((cx - 36 * SS, cy + fh * 0.06, cx + 36 * SS, cy + fh * 0.27), fill=SKIN)
        d.ellipse((cx - 14 * SS, cy + fh * 0.1, cx + 6 * SS, cy + fh * 0.16), fill=SKIN_LIGHT)

        return img

    def _features(self, img, d, cx, cy, fw, fh, mouth, blink):
        W, H = img.size
        # mouth (opens with the voice)
        my = cy + fh * 0.52
        mw = 92 * SS
        mh = (14 + 70 * mouth) * SS
        d.rounded_rectangle((cx - mw, my - mh / 2, cx + mw, my + mh / 2), radius=int(min(mw, mh / 2 + 1)),
                            fill=(70, 22, 26))
        if mouth <= 0.15:  # closed: show a lower lip
            d.chord((cx - mw * 0.8, my - 8 * SS, cx + mw * 0.8, my + 26 * SS), 0, 180, fill=(170, 92, 84))
        if mouth > 0.15:
            d.rounded_rectangle((cx - mw * 0.82, my - mh / 2, cx + mw * 0.82, my - mh / 2 + 22 * SS),
                                radius=10 * SS, fill=(245, 240, 232))
            d.ellipse((cx - mw * 0.5, my + mh * 0.05, cx + mw * 0.5, my + mh / 2 + 4 * SS), fill=(176, 70, 72))
        # moustache over the top lip
        mt = my - mh / 2
        d.polygon([(cx - mw * 1.35, mt + 18 * SS), (cx - mw * 0.9, mt - 34 * SS), (cx - 20 * SS, mt - 46 * SS),
                   (cx, mt - 38 * SS), (cx + 20 * SS, mt - 46 * SS), (cx + mw * 0.9, mt - 34 * SS),
                   (cx + mw * 1.35, mt + 18 * SS), (cx + mw * 0.9, mt + 2 * SS), (cx, mt - 6 * SS),
                   (cx - mw * 0.9, mt + 2 * SS)], fill=(22, 16, 14))

        # eyes
        ey = cy - fh * 0.12
        for sgn in (-1, 1):
            ex = cx + sgn * fw * 0.42
            if blink > 0.5:
                d.arc((ex - 52 * SS, ey - 20 * SS, ex + 52 * SS, ey + 30 * SS), 10, 170, fill=HAIR, width=8 * SS)
            else:
                d.ellipse((ex - 54 * SS, ey - 40 * SS, ex + 54 * SS, ey + 40 * SS), fill=(250, 248, 244))
                d.ellipse((ex - 30 * SS, ey - 32 * SS, ex + 30 * SS, ey + 32 * SS), fill=IRIS)
                d.ellipse((ex - 15 * SS, ey - 17 * SS, ex + 15 * SS, ey + 17 * SS), fill=(15, 10, 8))
                d.ellipse((ex - 4 * SS, ey - 24 * SS, ex + 12 * SS, ey - 8 * SS), fill=(255, 255, 255))
            # thick, slightly arched eyebrows above the frames
            ix, ox = ex - sgn * 80 * SS, ex + sgn * 95 * SS
            d.polygon([(ix, ey - 98 * SS), (ex, ey - 122 * SS), (ox, ey - 108 * SS),
                       (ox, ey - 92 * SS), (ex, ey - 100 * SS), (ix, ey - 76 * SS)], fill=HAIR)

        # glasses: thin rectangular frames with a light lens tint
        lens = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lens)
        for sgn in (-1, 1):
            ex = cx + sgn * fw * 0.42
            box = (ex - 108 * SS, ey - 70 * SS, ex + 108 * SS, ey + 72 * SS)
            ld.rounded_rectangle(box, radius=26 * SS, fill=(200, 230, 225, 50))
            ld.rounded_rectangle(box, radius=26 * SS, outline=FRAME + (255,), width=9 * SS)
            # glare
            ld.line((ex - 70 * SS, ey - 40 * SS, ex - 30 * SS, ey - 60 * SS), fill=(255, 255, 255, 120), width=8 * SS)
        ld.line((cx - fw * 0.42 + 108 * SS, ey - 30 * SS, cx + fw * 0.42 - 108 * SS, ey - 30 * SS),
                fill=FRAME + (255,), width=9 * SS)
        for sgn in (-1, 1):
            ld.line((cx + sgn * (fw * 0.42 + 108 * SS), ey - 40 * SS, cx + sgn * fw * 0.98, ey - 30 * SS),
                    fill=FRAME + (255,), width=9 * SS)
        img.alpha_composite(lens)
        return img

    # ------------------------------------------------------------- frame
    def frame(self, t, mouth=0.0):
        blink = 1.0 if any(0 <= t - b < 0.12 for b in self.blinks) else 0.0
        head = self._head(mouth, blink)
        tilt = 4 * math.sin(t * 1.3) + 2 * math.sin(t * 2.9)
        bob = 10 * math.sin(t * 2.1) + mouth * 6
        head = head.rotate(tilt, resample=Image.BICUBIC, center=(head.width / 2, head.height * 0.8))
        img = self._body.copy()
        hx = (img.width - head.width) // 2
        hy = int(img.height * 0.60 - head.height * 0.80 + bob * SS)
        img.alpha_composite(head, (hx, hy))
        return img.resize((AW, AH), Image.LANCZOS)


if __name__ == "__main__":
    import sys
    av = Avatar()
    out = sys.argv[1] if len(sys.argv) > 1 else "avatar_preview.png"
    frames = [av.frame(0.5, 0.0), av.frame(1.0, 0.7)]
    sheet = Image.new("RGBA", (AW * 2, AH), (120, 90, 220, 255))
    for i, f in enumerate(frames):
        sheet.alpha_composite(f, (i * AW, 0))
    sheet.convert("RGB").resize((AW, AH // 2)).save(out)
