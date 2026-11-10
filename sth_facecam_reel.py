"""
Face-cam STH reel: your talking clip as the hook, then the beat-synced car reveals.

    python sth_facecam_reel.py sth_assets facecam.mov out.mp4 [--toon]

--avatar replaces the footage with the Memoji-style cartoon from sth_avatar.py,
         lip-synced to the clip's voice (the video itself is not shown).
--filter keeps the real face with a natural beauty filter and a fuller beard
         (sth_face_filter.py, needs sth_assets/models/face_landmarker.task).
--toon turns the face-cam footage into a painted cartoon (OpenCV stylization
plus ink outlines, smoothed over time so the lines don't flicker).

Part 1: the face-cam clip full screen with a title overlay and a strip of the
        STH cars along the bottom; the beat plays quietly under your voice.
Part 2: the reel from sth_reveal_video.py, starting at the first car reveal.
"""

import math
import subprocess
import sys
import wave

import cv2
import numpy as np
from PIL import Image, ImageDraw

import sth_reveal_video as R
from sth_reveal_video import (CARS, F_BLACK, F_BLACK_I, FPS, H, TOTAL_MIXES, W, Car, caption_box, p_,
                              slam_text)

SR = 44100
BED_GAIN = 0.13  # music level under the voice


def probe_duration(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", path])
    return float(out)


def cam_frames(path):
    """Yield the clip's frames as 1080x1920 RGB arrays (HDR iPhone footage converted to 8-bit)."""
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", path, "-map", "0:v:0",
                          "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},format=rgb24",
                          "-r", str(FPS), "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    p.wait()


class Toon:
    """Painted-cartoon filter for video frames (RGB in, RGB out)."""

    def __init__(self):
        self.edge_avg = None

    def __call__(self, rgb):
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        small = cv2.resize(bgr, (540, 960), interpolation=cv2.INTER_AREA)
        paint = cv2.stylization(small, sigma_s=60, sigma_r=0.45)
        hsv = cv2.cvtColor(paint, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 1] *= 1.18
        hsv[..., 2] = hsv[..., 2] * 1.06 + 6
        paint = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        g = cv2.medianBlur(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), 5)
        e = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 7)
        e = (255 - e).astype(np.float32) / 255  # 1 where there is a line
        self.edge_avg = e if self.edge_avg is None else self.edge_avg * 0.5 + e * 0.5
        line = np.clip((self.edge_avg - 0.35) / 0.4, 0, 1)[..., None]
        out = paint.astype(np.float32) * (1 - line * 0.92)
        out = cv2.resize(np.clip(out, 0, 255).astype(np.uint8), (W, H), interpolation=cv2.INTER_CUBIC)
        return cv2.cvtColor(out, cv2.COLOR_BGR2RGB)


def mouth_track(cam, n_frames):
    """Mouth openness per video frame (0..1) from the voice loudness."""
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", cam, "-map", "0:a:0", "-ac", "1",
                                   "-ar", "16000", "-f", "s16le", "-"])
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    hop = 16000 // FPS
    rms = np.array([np.sqrt((x[i * hop:(i + 1) * hop] ** 2).mean() + 1e-12) for i in range(n_frames)])
    lo, hi = np.percentile(rms, 20), np.percentile(rms, 95)
    m = np.clip((rms - lo * 1.3) / max(1e-6, hi - lo * 1.3), 0, 1)
    out, v = [], 0.0
    for a in m:  # fast attack, slower release, like real lips
        v = a if a > v else v * 0.6 + a * 0.4
        out.append(v)
    return np.array(out)


def avatar_frames(cam, n_frames, grid):
    from sth_avatar import AH, Avatar
    av = Avatar()
    mouth = mouth_track(cam, n_frames)
    for k in range(n_frames):
        t = k / FPS
        base = R.bg_frame(t, (255, 40, 90), grid)
        base.alpha_composite(av.frame(t, float(mouth[k])), (0, H - AH - 40))
        yield np.asarray(base.convert("RGB"))


def make_overlay_assets(cars):
    top = Image.linear_gradient("L").rotate(180).resize((W, 520)).point(lambda v: int(v * 0.75))
    shade_top = Image.new("RGBA", (W, 520), (0, 0, 0, 255))
    shade_top.putalpha(top)
    bot = Image.linear_gradient("L").resize((W, 420)).point(lambda v: int(v * 0.8))
    shade_bot = Image.new("RGBA", (W, 420), (0, 0, 0, 255))
    shade_bot.putalpha(bot)
    small = [c.img.resize((300, int(c.img.height * 300 / c.img.width)), Image.LANCZOS) for c in cars]
    return shade_top, shade_bot, small


def cam_overlay(frame, t, dur, assets):
    shade_top, shade_bot, small = assets
    # slow push-in so the shot feels alive
    s = 1 + 0.05 * (t / dur)
    if s > 1.001:
        w2, h2 = int(W * s), int(H * s)
        frame = frame.resize((w2, h2), Image.BILINEAR).crop(((w2 - W) // 2, (h2 - H) // 2,
                                                             (w2 - W) // 2 + W, (h2 - H) // 2 + H))
    base = frame.convert("RGBA")
    base.alpha_composite(shade_top, (0, 0))
    base.alpha_composite(shade_bot, (0, H - 420))
    slam_text(base, W / 2, 150, "2027 STH", F_BLACK_I, 150, (255, 255, 255), p_(t, 0.15, 0.3),
              stroke=6, sfill=(0, 0, 0), start=1.8)
    caption_box(base, W / 2, 300, f"{len(CARS)}/{TOTAL_MIXES} REVEALED", font_(58), (0, 0, 0),
                (255, 214, 0), p_(t, 0.6, 0.3), emo="👀", rot=-3)
    # cars rolling along the bottom
    x = W - (t * 260) % (len(small) * 330) - 330
    for k in range(len(small) * 2):
        im = small[k % len(small)]
        xx = x + k * 330
        if -330 < xx < W:
            base.alpha_composite(im, (int(xx), H - 150 - im.height // 2))
    # flash into the reel
    if t > dur - 0.25:
        a = (t - (dur - 0.25)) / 0.25
        white = Image.new("RGBA", (W, H), (255, 255, 255, int(255 * a * 0.85)))
        base.alpha_composite(white)
    return np.asarray(base.convert("RGB"))


def font_(size):
    return R.font(F_BLACK, size)


def read_wav_mono(path):
    with wave.open(path) as wf:
        sr, ch, n = wf.getframerate(), wf.getnchannels(), wf.getnframes()
        a = np.frombuffer(wf.readframes(n), np.int16).astype(np.float32) / 32768
    if ch > 1:
        a = a.reshape(-1, ch).mean(1)
    assert sr == SR, sr
    return a


def build_audio(cam, out_wav, cam_dur):
    beat_wav = out_wav.replace(".wav", "_beat.wav")
    R.synth_audio(beat_wav)
    beat = read_wav_mono(beat_wav)
    voice_wav = out_wav.replace(".wav", "_voice.wav")
    subprocess.check_call(["ffmpeg", "-loglevel", "error", "-y", "-i", cam, "-map", "0:a:0", "-ac", "1",
                           "-ar", str(SR), voice_wav])
    voice = read_wav_mono(voice_wav)
    n_cam = int(cam_dur * SR)
    voice = np.pad(voice, (0, max(0, n_cam - len(voice))))[:n_cam]
    voice = voice / max(1e-6, np.abs(voice).max()) * 0.95
    start = int(R.T_HOOK * SR)
    bed = beat[start:start + n_cam]
    bed = np.pad(bed, (0, n_cam - len(bed)))
    part1 = voice + bed * BED_GAIN
    part2 = beat[start:]
    mix = np.concatenate([part1, part2])
    mix = mix / max(1e-6, np.abs(mix).max()) * 0.92
    with wave.open(out_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((mix * 32767).astype(np.int16).tobytes())


def main(assets, cam, out, toon=False, avatar=False, beauty=False):
    cars = [Car(f"{assets}/sth{i}.png") for i in range(len(CARS))]
    cover = Car(f"{assets}/sth{len(CARS)}.png")
    grid, vignette, grain = R.make_grid(), R.make_vignette(), R.make_grain()
    ov = make_overlay_assets(cars)
    cam_dur = probe_duration(cam)
    n_cam = int(round(cam_dur * FPS))

    wav = out.rsplit(".", 1)[0] + "_audio.wav"
    build_audio(cam, wav, n_cam / FPS)

    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "20",
         "-maxrate", "9M", "-bufsize", "18M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
         "-shortest", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE)
    k = 0
    style = Toon() if toon else None
    if beauty:
        from sth_face_filter import FaceFilter
        style = FaceFilter(f"{assets}/models/face_landmarker.task", fps=FPS)
    source = avatar_frames(cam, n_cam, grid) if avatar else cam_frames(cam)
    for arr in source:
        if style is not None:
            arr = style(arr)
        if k >= n_cam:
            break
        ff.stdin.write(cam_overlay(Image.fromarray(arr), k / FPS, n_cam / FPS, ov).tobytes())
        k += 1
    for i in range(n_cam - k):  # pad if the decoder delivered fewer frames
        ff.stdin.write(arr.tobytes())
    if hasattr(style, "det"):
        style.det.close()  # release the MediaPipe face tracker cleanly
    n_reel = int((R.TOTAL - R.T_HOOK) * FPS)
    for fi in range(n_reel):
        t = R.T_HOOK + fi / FPS
        ff.stdin.write(R.render_frame(t, cars, cover, grid, vignette, grain, fi).tobytes())
    ff.stdin.close()
    ff.wait()
    print(f"wrote {out}: {n_cam / FPS + R.TOTAL - R.T_HOOK:.1f}s")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 3:
        sys.exit(__doc__)
    main(*args, toon="--toon" in sys.argv, avatar="--avatar" in sys.argv, beauty="--filter" in sys.argv)
