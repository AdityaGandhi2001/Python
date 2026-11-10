"""
Natural "good filter" for the face-cam clip: smoother, brighter skin and a
fuller, darker, neater beard - on the real face, no cartoon.

Uses the MediaPipe Face Landmarker (478 face points) to build masks:
  beard  = lower face below the cheek line (incl. moustache), lips excluded
  skin   = forehead / cheeks / nose, eyes, brows and lips excluded
Landmarks are smoothed over time so the masks don't jitter.

Model: https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
"""

import cv2
import mediapipe as mp
import numpy as np

FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377,
             152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
# lower part of the oval, from the right face edge round the chin to the left edge
JAW = [454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234]
# cheek line: left edge -> left cheek -> under the nose -> right cheek -> right edge
CHEEK_LINE = [234, 227, 116, 117, 118, 101, 36, 203, 98, 97, 2, 326, 327, 423, 266, 330, 347, 346, 345, 447, 454]
LIPS = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]
LEFT_EYE = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
RIGHT_EYE = [263, 466, 388, 387, 386, 385, 384, 398, 362, 382, 381, 380, 374, 373, 390, 249]
LEFT_BROW = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]
RIGHT_BROW = [300, 293, 334, 296, 336, 285, 295, 282, 283, 276]

BEARD_COL = np.array([22, 26, 32], np.float32)  # BGR, very dark brown


class FaceFilter:
    def __init__(self, model_path, fps=30, sunkissed=True):
        self.sunkissed = sunkissed
        opts = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=mp.tasks.vision.RunningMode.VIDEO, num_faces=1)
        self.det = mp.tasks.vision.FaceLandmarker.create_from_options(opts)
        self.fps = fps
        self.k = 0
        self.pts = None

    def landmarks(self, rgb):
        h, w = rgb.shape[:2]
        res = self.det.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb),
                                        int(self.k * 1000 / self.fps))
        self.k += 1
        if not res.face_landmarks:
            return self.pts
        p = np.array([(lm.x * w, lm.y * h) for lm in res.face_landmarks[0]], np.float32)
        self.pts = p if self.pts is None else self.pts * 0.45 + p * 0.55
        return self.pts

    def masks(self, shape, p):
        h, w = shape[:2]

        def poly(idx, extra=None):
            m = np.zeros((h, w), np.uint8)
            pts = p[idx] if extra is None else extra
            cv2.fillPoly(m, [pts.astype(np.int32)], 255)
            return m

        face_h = np.linalg.norm(p[10] - p[152])
        centre = p[[234, 454]].mean(0)
        # beard: cheek line on top, jaw pushed outward/down a little (beards sit outside the jawline)
        jaw = p[JAW].copy()
        jaw = centre + (jaw - centre) * np.array([1.04, 1.0])
        jaw[:, 1] += np.clip((jaw[:, 1] - centre[1]) / face_h, 0, 1) * face_h * 0.30
        beard = poly(None, np.vstack([p[CHEEK_LINE], jaw[::-1][1:-1]]))
        lips = cv2.dilate(poly(LIPS), np.ones((5, 5), np.uint8))
        beard = cv2.subtract(beard, lips)
        face = poly(FACE_OVAL)
        feats = poly(LEFT_EYE) | poly(RIGHT_EYE) | poly(LEFT_BROW) | poly(RIGHT_BROW) | lips
        feats = cv2.dilate(feats, np.ones((15, 15), np.uint8))
        skin = cv2.subtract(cv2.subtract(face, beard), feats)
        f = int(face_h * 0.04) | 1
        return (cv2.GaussianBlur(beard, (f, f), 0).astype(np.float32) / 255,
                cv2.GaussianBlur(skin, (f * 2 + 1, f * 2 + 1), 0).astype(np.float32) / 255,
                face_h)

    def _sun_kiss(self, out, p, skin_m, beard_m, face_h):
        """Golden, bronzed skin + soft warm glow on the face's high points + golden-hour grade."""
        h, w = out.shape[:2]
        img8 = np.clip(out, 0, 255).astype(np.uint8)
        # all visible skin (face, neck, hands) by colour, softened -> smooth, even tan
        ycc = cv2.cvtColor(img8, cv2.COLOR_BGR2YCrCb).astype(np.float32)
        cr, cb = ycc[..., 1], ycc[..., 2]
        skin = np.clip(1 - np.maximum(np.abs(cr - 152) / 22, np.abs(cb - 108) / 22), 0, 1)
        skin = cv2.GaussianBlur(skin, (0, 0), face_h * 0.02) * (1 - beard_m * 0.6)
        warm = out * np.array([0.86, 0.99, 1.07], np.float32) + np.array([0, 4, 12], np.float32)
        a = (skin * 0.8)[..., None]
        out = out * (1 - a) + warm * a
        # soft glow on cheekbones, nose and forehead, inside the face only (no holes)
        face = np.zeros((h, w), np.float32)
        cv2.fillPoly(face, [p[FACE_OVAL].astype(np.int32)], 1.0)
        face = cv2.GaussianBlur(face, (0, 0), face_h * 0.04)
        glow = np.zeros((h, w), np.float32)
        for idx, r in ((50, 0.11), (280, 0.11), (6, 0.08), (4, 0.06), (151, 0.13)):
            cv2.circle(glow, tuple(int(v) for v in p[idx]), int(face_h * r), 1.0, -1)
        glow = cv2.GaussianBlur(glow, (0, 0), face_h * 0.09)
        glow = (np.clip(glow / max(1e-6, glow.max()), 0, 1) * face * (1 - beard_m))[..., None]
        out = out + glow * np.array([8, 20, 34], np.float32)  # peach / rose-gold light
        # golden-hour grade: warm highlights, gentle lift, soft bloom
        lum = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
        hi = (lum ** 1.5)[..., None]
        out = out + hi * np.array([-7, 4, 12], np.float32) + (1 - hi) * np.array([3, 2, 0], np.float32)
        bloom = cv2.GaussianBlur(np.clip(out, 0, 255), (0, 0), 18)
        return out * 0.9 + bloom * 0.1 + 2

    def __call__(self, rgb):
        p = self.landmarks(rgb)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        out = bgr.astype(np.float32)
        if p is not None:
            beard_m, skin_m, face_h = self.masks(bgr.shape, p)
            # --- skin: smooth while keeping edges, then brighten slightly
            smooth = cv2.bilateralFilter(bgr, 0, 28, 9).astype(np.float32)
            smooth = smooth * 1.05 + 6
            a = skin_m[..., None] * 0.7
            out = out * (1 - a) + smooth * a
            # --- beard: only where hair already is; thicken it and fill thin patches inside it
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
            skin_lum = np.median(gray[skin_m > 0.8]) if (skin_m > 0.8).any() else 150
            lum = cv2.GaussianBlur(gray, (0, 0), 2)
            hair = np.clip((skin_lum * 0.78 - lum) / (skin_lum * 0.3), 0, 1) * beard_m
            k = int(face_h * 0.035) | 1
            dense = cv2.morphologyEx(hair, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
            dense = cv2.GaussianBlur(dense, (0, 0), face_h * 0.006)
            dense = np.minimum(dense, beard_m)
            detail = gray - cv2.GaussianBlur(gray, (0, 0), 2.5)
            # natural shade: sample the person's own beard colour (darker hair pixels), smoothed over time
            sel = hair > 0.6
            if sel.sum() > 500:
                own = np.median(bgr[sel].astype(np.float32), axis=0)
                self.shade = own if getattr(self, "shade", None) is None else self.shade * 0.9 + own * 0.1
            shade = getattr(self, "shade", None)
            shade = BEARD_COL if shade is None else shade * 0.92
            target = shade[None, None, :] + detail[..., None] * 1.1
            amt = (dense * 0.5)[..., None]
            out = out * (1 - amt) + target * amt
        if p is not None and self.sunkissed:
            out = self._sun_kiss(out, p, skin_m, beard_m, face_h)
        # --- global grade: gentle contrast, warmth, saturation
        out = np.clip(out, 0, 255).astype(np.uint8)
        lab = cv2.cvtColor(out, cv2.COLOR_BGR2LAB).astype(np.float32)
        lab[..., 0] = np.clip((lab[..., 0] - 128) * 1.06 + 131, 0, 255)
        lab[..., 1] = np.clip((lab[..., 1] - 128) * 1.08 + 129, 0, 255)
        lab[..., 2] = np.clip((lab[..., 2] - 128) * 1.08 + 130, 0, 255)
        out = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
        sharp = cv2.addWeighted(out, 1.25, cv2.GaussianBlur(out, (0, 0), 2), -0.25, 0)
        return cv2.cvtColor(sharp, cv2.COLOR_BGR2RGB)


if __name__ == "__main__":
    import sys
    model, src, dst = sys.argv[1:4]
    rgb = cv2.cvtColor(cv2.imread(src), cv2.COLOR_BGR2RGB)
    ff = FaceFilter(model)
    out = ff(rgb)
    p = ff.pts
    b, s, _ = ff.masks(rgb.shape, p)
    dbg = rgb.copy()
    dbg[..., 0] = np.clip(dbg[..., 0] + b * 120, 0, 255)
    dbg[..., 1] = np.clip(dbg[..., 1] + s * 120, 0, 255)
    sheet = np.hstack([cv2.resize(x, (405, 720)) for x in (rgb, dbg, out)])
    cv2.imwrite(dst, cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR))
