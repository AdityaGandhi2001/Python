"""Render the diecast promo as a 9:16 motion-graphics video.
Usage: python make_video.py <vo_dir> <out.mp4> [STORE] [HANDLE]
vo_dir must contain 0.wav .. 8.wav (one per script line)."""
import math, os, random, subprocess, sys, wave
from PIL import Image, ImageDraw, ImageFilter, ImageFont

VO, OUT = sys.argv[1], sys.argv[2]
STORE = sys.argv[3] if len(sys.argv) > 3 else "YOUR STORE"
HANDLE = sys.argv[4] if len(sys.argv) > 4 else "@yourstore"
W, H, FPS, GAP = 720, 1280, 30, 0.3
F = "/usr/share/fonts/opentype/inter/"
def font(s, w="Black"):
    for n in (f"Inter-{w}.otf", "Inter-Bold.otf"):
        if os.path.exists(F + n): return ImageFont.truetype(F + n, s)
    return ImageFont.load_default()

def dur(p):
    with wave.open(p) as w: return w.getnframes() / w.getframerate()
segs, t = [], 0.4
for i in range(9):
    d = dur(f"{VO}/{i}.wav"); segs.append((t, d)); t += d + GAP
TOTAL = t + 0.6

ease = lambda x: 1 - (1 - max(0, min(1, x))) ** 3
PINK, TEAL, GOLD, Y, R = (236, 60, 160), (40, 210, 200), (230, 180, 50), (255, 210, 0), (230, 40, 40)

def bg(top, bot):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / H; d.line([(0, y), (W, y)], tuple(int(top[c] * (1 - k) + bot[c] * k) for c in range(3)))
    return im

BGS = {}
def getbg(k, a, b):
    if k not in BGS: BGS[k] = bg(a, b)
    return BGS[k].copy()

def ctext(d, y, s, sz, fill=(255, 255, 255), w="Black", stroke=0, sc=(0, 0, 0), x=None):
    f = font(sz, w); bw = d.textlength(s, font=f)
    d.text(((W - bw) / 2 if x is None else x, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sc)

def car(d, cx, cy, s=1.0, rot=0):
    """Stylised bottle-shaped race car seen from the side."""
    def P(x, y):
        c, sn = math.cos(rot), math.sin(rot)
        return (cx + (x * c - y * sn) * s, cy + (x * sn + y * c) * s)
    body = [(-170, 10), (-150, -30), (-40, -45), (60, -40), (110, -22), (175, -18), (180, 15), (-170, 25)]
    d.polygon([P(*p) for p in body], fill=PINK, outline=(255, 255, 255))
    d.polygon([P(*p) for p in [(-30, -42), (60, -38), (70, -10), (-30, -12)]], fill=TEAL)
    d.polygon([P(*p) for p in [(-175, -60), (-140, -60), (-130, -25), (-160, -25)]], fill=(200, 200, 210))  # wing
    d.text(P(0, -5), "37", font=font(int(30 * s)), fill=(255, 255, 255))
    for wx in (-115, 120):
        x, y = P(wx, 28); r = 34 * s
        d.ellipse([x - r, y - r, x + r, y + r], fill=(25, 25, 25))
        d.ellipse([x - r * .6, y - r * .6, x + r * .6, y + r * .6], fill=GOLD)

def bottle(d, cx, cy, s=1.0, col=(120, 60, 20), label="YOUR FAVOURITE DRINK", cap=True):
    d.rounded_rectangle([cx - 70 * s, cy - 60 * s, cx + 70 * s, cy + 260 * s], 40 * s, fill=col)
    d.polygon([(cx - 70 * s, cy - 40 * s), (cx - 25 * s, cy - 170 * s), (cx + 25 * s, cy - 170 * s), (cx + 70 * s, cy - 40 * s)], fill=col)
    d.rectangle([cx - 25 * s, cy - 230 * s, cx + 25 * s, cy - 165 * s], fill=col)
    d.rounded_rectangle([cx - 62 * s, cy + 40 * s, cx + 62 * s, cy + 170 * s], 10 * s, fill=(245, 235, 210))
    words = label.split(" ")
    for j, wd in enumerate(words):
        f = font(int(19 * s)); bw = d.textlength(wd, font=f)
        d.text((cx - bw / 2, cy + (105 - 14 * len(words) + j * 28) * s), wd, font=f, fill=(60, 30, 10))
    if cap: d.rectangle([cx - 30 * s, cy - 250 * s, cx + 30 * s, cy - 228 * s], fill=(200, 170, 60))

def phone(im, draw_screen, tilt=0):
    p = Image.new("RGBA", (460, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(p)
    d.rounded_rectangle([0, 0, 459, 899], 50, fill=(20, 20, 24)); d.rounded_rectangle([14, 14, 445, 885], 40, fill=(12, 12, 14))
    draw_screen(d, 14, 14, 431, 871)
    p = p.rotate(tilt, expand=True, resample=Image.BICUBIC)
    im.paste(p, ((W - p.width) // 2, (H - p.height) // 2 + 40), p)

def sparkles(d, t, n=40, seed=1, col=(255, 255, 255)):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y, sp, ph = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(.5, 2), rnd.uniform(0, 6)
        a = (math.sin(t * sp * 4 + ph) + 1) / 2; r = 2 + 3 * a
        d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(c * a) for c in col))

def badge(d):
    d.ellipse([W - 92, H - 92, W - 32, H - 32], fill=(255, 120, 20))
    f = font(15); s = HANDLE[:9]; d.text((W - 62 - d.textlength(s, font=f) / 2, H - 70), s, font=f, fill="white")

def scene(i, lt, gt):
    if i == 0:  # cap pop
        im = getbg(0, (40, 25, 15), (5, 5, 5)); d = ImageDraw.Draw(im)
        bottle(d, W / 2, 760, 1.4, cap=lt < 1.0)
        cx = W / 2 + 140 - ease(lt / 0.9) * 120; car(d, cx + 150, 400, 0.8, rot=-0.5 if lt < 1 else -0.2)
        if lt >= 1.0:
            k = lt - 1.0; d.rectangle([W / 2 - 42 + k * 200, 400 - k * 700 + k * k * 500, W / 2 + 42 + k * 200, 430 - k * 700 + k * k * 500], fill=(200, 170, 60))
            for j in range(12):
                a = j / 12 * 6.28; r = 40 + k * 300
                d.ellipse([W / 2 + math.cos(a) * r - 6, 420 + math.sin(a) * r - 6, W / 2 + math.cos(a) * r + 6, 420 + math.sin(a) * r + 6], fill=(255, 240, 200))
        ctext(d, 120, "WAIT...", 80, Y, stroke=4)
    elif i == 1:  # title
        im = getbg(1, (60, 60, 70), (15, 15, 20)); d = ImageDraw.Draw(im); sparkles(d, gt, seed=2)
        sh = 8 * math.sin(lt * 40) * max(0, 1 - lt * 2); k = ease(lt / 0.4)
        ctext(d, 250 + sh, "HOT WHEELS", int(40 + 60 * k), R, stroke=6, sc=Y)
        ctext(d, 380, "CARBONATOR", int(30 + 40 * k), Y, stroke=4)
        car(d, W / 2 + (1 - k) * 600, 800, 1.3)
    elif i == 2:  # bottle -> car
        im = getbg(2, (230, 220, 205), (200, 188, 170)); d = ImageDraw.Draw(im)
        k = ease((lt - segs[2][1] * 0.45) / 0.8)
        if k <= 0:
            bottle(d, W / 2, 700, 1.0, col=PINK, label="IT'S A BOTTLE"); ctext(d, 200, "Looks like a bottle...", 46, (60, 40, 30))
        else:
            car(d, W / 2, 720, 0.6 + 0.9 * k, rot=(1 - k) * -1.57)
            ctext(d, 200, "BOOM!", int(60 + 50 * k), R, stroke=5, sc=Y); ctext(d, 320, "It's a race car", 46, (60, 40, 30))
    elif i == 3:  # opener
        im = getbg(3, (210, 215, 225), (150, 155, 165)); d = ImageDraw.Draw(im)
        if lt < segs[3][1] / 2:
            bottle(d, W / 2, 760, 1.2, col=(200, 230, 225), cap=lt < 1.2)
        else:
            d.rounded_rectangle([W / 2 - 120, 520, W / 2 + 120, 1040], 30, fill=(200, 205, 215), outline=(240, 240, 250), width=6)
            ctext(d, 720, "YOUR", 40, (90, 70, 30)); ctext(d, 770, "FAVOURITE", 40, (90, 70, 30)); ctext(d, 820, "DRINK", 40, (90, 70, 30))
        car(d, W / 2 + 160, 420 + 20 * math.sin(lt * 6), 0.7, rot=-0.4)
        ctext(d, 150, "IT OPENS BOTTLES!", 58, R, stroke=4, sc=(255, 255, 255))
    elif i == 4:  # friends
        im = getbg(4, (255, 170, 80), (180, 60, 90)); d = ImageDraw.Draw(im); rnd = random.Random(4)
        for j in range(80):
            x = rnd.uniform(0, W); y = (rnd.uniform(0, H) + lt * rnd.uniform(200, 500)) % H
            d.rectangle([x, y, x + 12, y + 6], fill=rnd.choice([Y, TEAL, PINK, (255, 255, 255)]))
        for j, x in enumerate((180, 360, 540)):
            yb = 980 - (25 * abs(math.sin(lt * 5 + j)))
            d.ellipse([x - 55, yb - 260, x + 55, yb - 150], fill=(150, 95, 60)); d.rounded_rectangle([x - 90, yb - 140, x + 90, yb + 200], 60, fill=[TEAL, Y, (250, 250, 250)][j])
        car(d, W / 2, 470 - 30 * abs(math.sin(lt * 4)), 0.6)
        ctext(d, 170, "EVERYONE WANTS ONE", 50, (255, 255, 255), stroke=4)
    elif i == 5:  # sold out
        im = getbg(5, (110, 35, 25), (40, 15, 10)); d = ImageDraw.Draw(im)
        for r in range(4):
            for c in range(3):
                x, y = 60 + c * 210, 260 + r * 230
                d.rounded_rectangle([x, y, x + 180, y + 210], 12, fill=(30, 90, 200)); d.text((x + 20, y + 15), "DIECAST", font=font(26), fill=Y)
                d.rounded_rectangle([x + 25, y + 110, x + 155, y + 160], 20, fill=[R, TEAL, Y, PINK][(r + c) % 4])
                if lt > 0.3 + (r * 3 + c) * 0.12:
                    d.text((x + 10, y + 70), "SOLD OUT", font=font(34), fill=(255, 40, 40), stroke_width=3, stroke_fill="white")
        ctext(d, 110, "SOLD OUT EVERYWHERE", 52, (255, 255, 255), stroke=4, sc=R)
    elif i == 6:  # instagram
        im = getbg(6, (30, 10, 50), (5, 5, 15)); d = ImageDraw.Draw(im); sparkles(d, gt, 50, 6, (200, 120, 255))
        def scr(s, x0, y0, w, h):
            s.rectangle([x0, y0, x0 + w, y0 + h], fill=(0, 0, 0))
            s.text((x0 + 30, y0 + 40), HANDLE, font=font(26), fill="white")
            s.ellipse([x0 + 30, y0 + 100, x0 + 150, y0 + 220], fill=(255, 120, 20)); s.text((x0 + 62, y0 + 140), "DC", font=font(36), fill="white")
            for j, (n, l) in enumerate([("1.2K", "posts"), ("48K", "followers"), ("210", "following")]):
                s.text((x0 + 180 + j * 85, y0 + 130), n, font=font(24), fill="white"); s.text((x0 + 180 + j * 85, y0 + 165), l, font=font(14, "Regular"), fill=(180, 180, 180))
            s.text((x0 + 30, y0 + 240), "Premium Diecast Store", font=font(20, "Bold"), fill="white")
            s.text((x0 + 30, y0 + 270), "Hot Wheels • Matchbox • Mini GT", font=font(17, "Regular"), fill=(200, 200, 200))
            s.rounded_rectangle([x0 + 30, y0 + 320, x0 + w - 30, y0 + 370], 10, fill=(0, 120, 255)); s.text((x0 + w / 2 - 40, y0 + 332), "Follow", font=font(24), fill="white")
            for r in range(3):
                for c in range(3):
                    s.rectangle([x0 + c * 144, y0 + 400 + r * 144, x0 + c * 144 + 141, y0 + 541 + r * 144], fill=[PINK, TEAL, Y, R, (30, 90, 200)][(r * 3 + c) % 5])
        phone(im, scr, tilt=-8 * (1 - ease(lt / 0.8)))
        d = ImageDraw.Draw(im); k = ease((lt - 0.8) / 0.4)
        if k > 0:
            ctext(d, 120, "FOLLOW!", int(90 * k) + 1, Y, stroke=6, sc=(255, 90, 0))
        ctext(d, 1160, STORE, 48, (255, 255, 255), stroke=3, sc=(150, 50, 255))
    elif i == 7:  # whatsapp
        im = getbg(7, (10, 40, 30), (5, 15, 10)); d = ImageDraw.Draw(im)
        def scr(s, x0, y0, w, h):
            s.rectangle([x0, y0, x0 + w, y0 + h], fill=(11, 20, 26)); s.rectangle([x0, y0, x0 + w, y0 + 90], fill=(31, 44, 52))
            s.text((x0 + 30, y0 + 25), STORE[:18], font=font(24), fill="white"); s.text((x0 + 30, y0 + 58), "Group • 1,287 members", font=font(14, "Regular"), fill=(170, 180, 180))
            items = [("Nissan Skyline GT-R", R), ("BMW M4 GT3", TEAL), ("Ferrari F40", Y), ("Lamborghini Huracan", PINK)]
            n = min(len(items), int(lt / 1.2) + 1); off = max(0, n - 3) * 230
            for j in range(n):
                yy = y0 + 110 + j * 230 - off
                if yy < y0 + 90: continue
                s.rounded_rectangle([x0 + 20, yy, x0 + w - 60, yy + 210], 14, fill=(32, 44, 51))
                s.rounded_rectangle([x0 + 35, yy + 15, x0 + w - 75, yy + 120], 8, fill=items[j][1]); s.text((x0 + 50, yy + 50), "HOT WHEELS", font=font(26), fill="white")
                s.text((x0 + 35, yy + 132), f"{items[j][0]} — MRP ₹179", font=font(18, "Bold"), fill="white")
                s.text((x0 + 35, yy + 165), "Stock available • DM to claim", font=font(15, "Regular"), fill=(150, 220, 170))
        phone(im, scr)
        ctext(d, 110, "DROPS AT MRP", 64, (60, 230, 120), stroke=4, sc=(0, 0, 0))
    else:  # notification + end card
        im = getbg(8, (40, 20, 60), (10, 5, 20)); d = ImageDraw.Draw(im); sparkles(d, gt, 60, 8, (255, 200, 80))
        k = ease(lt / 0.5); y = -200 + k * 420
        d.rounded_rectangle([50, y, W - 50, y + 170], 30, fill=(245, 245, 248))
        d.rounded_rectangle([75, y + 30, 165, y + 120], 20, fill=(37, 211, 102)); d.text((100, y + 45), "S", font=font(56), fill="white")
        d.text((190, y + 30), STORE[:20], font=font(26), fill=(20, 20, 20))
        d.text((190, y + 70), "New drop is now LIVE!", font=font(22, "Bold"), fill=(40, 40, 40))
        d.text((190, y + 105), "Limited stock • DM to claim", font=font(19, "Regular"), fill=(90, 90, 90))
        car(d, W / 2, 760, 1.2 + 0.05 * math.sin(lt * 4))
        ctext(d, 980, "LINK IN BIO", 70, Y, stroke=5, sc=R); ctext(d, 1080, HANDLE, 44, (255, 255, 255))
    badge(ImageDraw.Draw(im))
    return im

os.makedirs("frames", exist_ok=True)
N = int(TOTAL * FPS)
for n in range(N):
    gt = n / FPS; i = 0
    for j, (s, _) in enumerate(segs):
        if gt >= s - GAP / 2: i = j
    lt = gt - segs[i][0]
    im = scene(i, max(0, lt), gt)
    sw = segs[i][0] - GAP / 2  # white flash transition
    if i and 0 <= gt - sw < 0.12: im = Image.blend(im, Image.new("RGB", (W, H), "white"), 0.6 * (1 - (gt - sw) / 0.12))
    im.save(f"frames/{n:05d}.jpg", quality=90)

inputs, filt = [], []
for j, (s, _) in enumerate(segs):
    inputs += ["-i", f"{VO}/{j}.wav"]; filt.append(f"[{j + 1}:a]adelay={int(s * 1000)}|{int(s * 1000)}[a{j}]")
filt.append("".join(f"[a{j}]" for j in range(9)) + "amix=inputs=9:normalize=0,apad[vo]")
filt.append(f"anoisesrc=d={TOTAL}:c=pink:a=0.0,volume=0[sil]")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", "frames/%05d.jpg", *inputs,
                "-filter_complex", ";".join(filt[:-1]), "-map", "0:v", "-map", "[vo]", "-t", f"{TOTAL:.2f}",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-b:a", "160k", OUT], check=True)
print("done", OUT, round(TOTAL, 1), "s")
