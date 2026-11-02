"""Task 01: file + image-quality validation with actionable messages.

Quality metrics (sharpness, brightness) are measured on the HAND REGION only, found by
adaptive segmentation. Measuring the whole frame made a plain white background look
"overexposed" and "blurry" (flat areas have ~zero Laplacian variance).
"""
from __future__ import annotations
from dataclasses import dataclass, field
import io
import cv2
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError
from .segmentation import segment_hand

ALLOWED_EXT = {"jpg", "jpeg", "png"}
MIN_SIDE = 400             # px, shortest side of the whole photo
EDGE_WIDTH_MAX = 5.0       # px: silhouette edge wider than this (at 800 px image width) = blurry
MIN_EDGE_STEP = 8.0        # grey levels: below this the edge is unmeasurable, blur is not judged
BRIGHT_RANGE = (35, 230)   # mean grey level of the HAND only. Wide on the low side because
                           # dark skin in good light is legitimately dark (~50-90).
CLIP_MAX = 0.20            # max fraction of hand pixels that may be blown out (>=250)
MIN_HAND_FRACTION = 0.12   # hand area / image area
EDGE_CONTACT_MIN = 0.08    # a side counts as "touched" if the hand covers >8% of its length
MAX_BYTES = 15 * 1024 * 1024
_QUALITY_WIDTH = 800


@dataclass
class ValidationResult:
    ok: bool
    image: np.ndarray | None = None          # BGR uint8
    hand_mask: np.ndarray | None = None      # full-size uint8 0/255 from adaptive segmentation
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


def _edge_width(chan: np.ndarray, m: np.ndarray) -> tuple[float, float]:
    """Width (px) of the hand's silhouette edge = step height / peak gradient.

    Contrast-invariant: a sharp edge is ~1-3 px wide at 800 px image width, defocus or
    motion blur widens it. Laplacian variance was rejected because it scales with
    skin/background contrast (pale skin on white scored "blurry" even when sharp).
    Returns (median width, step height); width = inf when there is no measurable step.
    """
    f = cv2.GaussianBlur(chan.astype(np.float32), (0, 0), 0.7)
    gx, gy = cv2.Sobel(f, cv2.CV_32F, 1, 0, ksize=3) / 8, cv2.Sobel(f, cv2.CV_32F, 0, 1, ksize=3) / 8
    g = cv2.dilate(cv2.magnitude(gx, gy), np.ones((5, 5), np.uint8))   # peak gradient within +-2 px
    k = np.ones((3, 3), np.uint8)
    boundary = (cv2.dilate(m, k) > 0) & (cv2.erode(m, k) == 0)
    h, w = m.shape
    boundary[:6], boundary[-6:], boundary[:, :6], boundary[:, -6:] = False, False, False, False  # wrist/crop
    inside = (cv2.erode(m, np.ones((21, 21), np.uint8)) == 0) & (m > 0)       # rim just inside
    outside = (cv2.dilate(m, np.ones((21, 21), np.uint8)) > 0) & (m == 0)     # rim just outside
    if boundary.sum() < 200 or not inside.any() or not outside.any():
        return float("inf"), 0.0
    step = abs(float(f[inside].mean()) - float(f[outside].mean()))
    peak = float(np.median(g[boundary]))
    return (step / peak if peak > 1e-3 else float("inf")), step


def hand_quality(bgr: np.ndarray, mask: np.ndarray) -> dict:
    """Edge sharpness and exposure measured on the hand region only."""
    h, w = bgr.shape[:2]
    s = _QUALITY_WIDTH / w
    small = cv2.resize(bgr, (_QUALITY_WIDTH, int(h * s)), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    m = cv2.resize(mask, (gray.shape[1], gray.shape[0]), interpolation=cv2.INTER_NEAREST)
    inner = cv2.erode(m, np.ones((9, 9), np.uint8))                 # skin only, away from the silhouette
    region = inner if (inner > 0).sum() > 500 else m
    px = gray[region > 0]
    # use the colour channel with the largest skin/background step (pale skin on a pale wall
    # has almost no luminance step but still differs in colour)
    best = (float("inf"), 0.0)
    for chan in (gray, *cv2.split(small)):
        wd, st = _edge_width(chan, m)
        if st > best[1]:
            best = (wd, st)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    return {"edge_width": best[0], "edge_step": best[1],
            "texture": float(lap[region > 0].var()) if px.size else 0.0,
            "brightness": float(px.mean()) if px.size else 0.0,
            "clipped": float((px >= 250).mean()) if px.size else 0.0}


def _edge_contacts(mask: np.ndarray) -> list[str]:
    h, w = mask.shape
    sides = {"top": mask[0] > 0, "bottom": mask[-1] > 0, "left": mask[:, 0] > 0, "right": mask[:, -1] > 0}
    return [n for n, v in sides.items() if v.mean() > EDGE_CONTACT_MIN]


def validate_upload(name: str, data: bytes, side: str) -> ValidationResult:
    res = ValidationResult(ok=False)
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in ALLOWED_EXT:
        res.errors.append(f"{side} palm: '{name}' is not supported. Upload a JPG, JPEG or PNG file.")
        return res
    if len(data) > MAX_BYTES:
        res.errors.append(f"{side} palm: file is larger than 15 MB. Resize or compress it and re-upload.")
        return res
    try:
        Image.open(io.BytesIO(data)).verify()
        pil = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")  # honour phone rotation
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError):
        res.errors.append(f"{side} palm: the file is corrupted or not a real image. Please re-export it and upload again.")
        return res

    bgr = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    h, w = bgr.shape[:2]
    res.image = bgr
    if min(h, w) < MIN_SIDE:
        res.errors.append(f"{side} palm: resolution {w}x{h} is too low (shortest side must be ≥ {MIN_SIDE}px). Take the photo closer or with a better camera.")

    seg = segment_hand(bgr)
    res.hand_mask = seg.mask
    frac = float((seg.mask > 0).mean())
    res.metrics = {"width": w, "height": h, "hand_fraction": round(frac, 3),
                   "segmentation": seg.method}
    if frac < MIN_HAND_FRACTION:
        res.errors.append(f"{side} palm: no clear palm detected (hand covers only {frac:.0%} of the photo). "
                          "Show the full open palm facing the camera against a plain, contrasting background.")
        res.ok = False
        return res

    q = hand_quality(bgr, seg.mask)
    ew = q["edge_width"]
    res.metrics.update(edge_width_px=round(ew, 2) if np.isfinite(ew) else None, texture=round(q["texture"], 1),
                       brightness=round(q["brightness"], 1), clipped=round(q["clipped"], 3))
    if q["edge_step"] < MIN_EDGE_STEP:
        res.warnings.append(f"{side} palm: the hand barely differs from the background, so focus could not be "
                            "checked. Use a plain background that contrasts with your skin.")
    elif ew > EDGE_WIDTH_MAX:
        res.errors.append(f"{side} palm: the hand looks blurry (edge width {ew:.1f}px > {EDGE_WIDTH_MAX:.0f}px). "
                          "Hold the phone steady and tap the palm to focus.")
    if q["brightness"] < BRIGHT_RANGE[0]:
        res.errors.append(f"{side} palm: the hand is too dark (brightness {q['brightness']:.0f}). Use bright, even lighting.")
    elif q["brightness"] > BRIGHT_RANGE[1] or q["clipped"] > CLIP_MAX:
        res.errors.append(f"{side} palm: the hand is overexposed (brightness {q['brightness']:.0f}, "
                          f"{q['clipped']:.0%} blown-out pixels). Avoid direct flash or strong glare.")

    touched = _edge_contacts(seg.mask)
    if len(touched) >= 2:
        res.errors.append(f"{side} palm: the hand appears cut off by the image edge ({', '.join(touched)}). "
                          "Keep the whole palm and fingers inside the frame (only the wrist may leave it).")
    elif len(touched) == 1:
        res.warnings.append(f"{side} palm: the hand touches the {touched[0]} edge; this is fine for the wrist, "
                            "but fingertips must be fully inside the frame.")
    res.ok = not res.errors
    return res
