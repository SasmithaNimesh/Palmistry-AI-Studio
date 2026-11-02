"""Synthetic hand generator used by the tests (no personal images involved).

Returns the image AND the ground-truth hand mask so segmentation can be scored.
Only the geometry is realistic enough for the pipeline; it is NOT a substitute for
testing on real consented palm photos (see tools/run_photo_tests.py).
"""
from __future__ import annotations
import cv2
import numpy as np

# BGR skin colours (approximate Fitzpatrick I-II / III-IV / V-VI looks)
TONES = {"light": (170, 198, 240), "medium": (105, 145, 200), "dark": (40, 58, 92),
         "deep": (15, 40, 85)}   # deep, warm-lit brown: leaves the old fixed HSV range (S>190)
BACKGROUNDS = {"white": (242, 242, 242), "grey": (150, 150, 150), "cream": (215, 225, 232)}


def synthetic_hand(tone="medium", angle=0.0, mirror=False, creases=True, bg="white",
                   blur=0.0, brightness=1.0, seed=0, w=900, h=1100, crease_strength=1.0):
    rng = np.random.default_rng(seed)
    skin = np.array(TONES[tone], np.float32)
    bgc = BACKGROUNDS[bg]
    img = np.full((h, w, 3), bgc, np.uint8)
    gt = np.zeros((h, w), np.uint8)

    def shape(draw):
        for target, col in ((img, tuple(int(v) for v in skin)), (gt, 255)):
            draw(target, col)

    shape(lambda t, c: cv2.ellipse(t, (450, 700), (230, 270), 0, 0, 360, c, -1))           # palm
    for x, top, hh in [(290, 200, 330), (390, 130, 400), (490, 120, 410), (590, 190, 340)]:  # fingers
        shape(lambda t, c, x=x, top=top, hh=hh: (cv2.rectangle(t, (x - 38, top), (x + 38, top + hh), c, -1),
                                                  cv2.circle(t, (x, top), 38, c, -1)))
    shape(lambda t, c: cv2.ellipse(t, (240, 760), (60, 150), 40, 0, 360, c, -1))            # thumb (image-left)

    # soft shading + skin texture so sharpness metrics are meaningful
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    shade = 1.0 - 0.18 * (((xx - 450) / 450) ** 2 + ((yy - 650) / 650) ** 2)
    f = img.astype(np.float32)
    on = gt > 0
    f[on] *= shade[on, None]
    f[on] += rng.normal(0, 5.0, f[on].shape)
    img = np.clip(f, 0, 255).astype(np.uint8)

    if creases:
        dark = tuple(int(v) for v in skin * (1 - 0.38 * crease_strength))
        for pts in ([[260, 560], [360, 540], [470, 545], [620, 520]],      # heart
                    [[270, 640], [380, 650], [500, 670], [610, 700]],      # head
                    [[300, 600], [290, 720], [320, 840], [400, 940]]):     # life
            cv2.polylines(img, [np.array(pts)], False, dark, 5, cv2.LINE_AA)
    img = cv2.GaussianBlur(img, (3, 3), 0.8)
    img = np.clip(img.astype(np.float32) * brightness, 0, 255).astype(np.uint8)
    if blur > 0:
        img = cv2.GaussianBlur(img, (0, 0), blur)

    if mirror:
        img, gt = cv2.flip(img, 1), cv2.flip(gt, 1)
    if angle:
        cx, cy = w / 2, h / 2
        M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
        cos, sin = abs(M[0, 0]), abs(M[0, 1])
        nw, nh = int(h * sin + w * cos), int(h * cos + w * sin)
        M[0, 2] += nw / 2 - cx
        M[1, 2] += nh / 2 - cy
        img = cv2.warpAffine(img, M, (nw, nh), flags=cv2.INTER_LINEAR, borderValue=bgc)
        gt = cv2.warpAffine(gt, M, (nw, nh), flags=cv2.INTER_NEAREST, borderValue=0)
    return img, gt


def png_bytes(img) -> bytes:
    return cv2.imencode(".png", img)[1].tobytes()
