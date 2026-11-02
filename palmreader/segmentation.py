"""Adaptive hand/skin segmentation (used by validation, preprocessing and features).

Fixed YCrCb/HSV skin ranges fail on darker skin, so the image itself decides the
threshold. Several independent candidate masks are produced, each is scored for
"does this look like a hand?", and the best one wins. If none is plausible,
GrabCut (iterative graph-cut using a centred rectangle prior) is the fallback.

Candidates
  background-distance : Otsu on the Lab distance from the border-ring colour
                        (works for any skin tone on a plain background)
  chroma-otsu         : Otsu on the Cr channel (skin is more red than neutral surfaces)
  chroma-kmeans       : 2-means on (Cr, Cb), keep the more saturated cluster
  fixed-range         : the old fixed YCrCb+HSV range (kept as a cheap candidate)
"""
from __future__ import annotations
from dataclasses import dataclass
import cv2
import numpy as np

WORK_WIDTH = 640          # segmentation runs on a downscaled copy for speed
REJECT_SCORE = 0.15       # below this even the fallback found nothing hand-like -> empty mask
ACCEPT_SCORE = 0.35       # below this the candidates are rejected -> GrabCut fallback


@dataclass
class Segmentation:
    mask: np.ndarray      # uint8 0/255, same size as the input, single filled hand blob
    method: str
    score: float


def _largest_filled(mask: np.ndarray) -> np.ndarray:
    """Keep the largest connected blob and fill its holes."""
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = np.zeros_like(mask)
    if cnts:
        cv2.drawContours(out, [max(cnts, key=cv2.contourArea)], -1, 255, -1)
    return out


def _clean(mask: np.ndarray) -> np.ndarray:
    # Deliberately small kernels: a bigger closing welds neighbouring fingers together (gaps
    # between spread fingers are only ~10 px at this working size) and the palm frame then
    # cannot separate fingers/thumb. Holes inside the hand are handled by _largest_filled.
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    m = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k)
    return _largest_filled(m)


def _fixed_range(bgr: np.ndarray) -> np.ndarray:
    ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    m1 = cv2.inRange(ycrcb, (0, 133, 77), (255, 180, 135))
    m2 = cv2.inRange(hsv, (0, 15, 40), (30, 190, 255))
    return cv2.bitwise_and(m1, m2)


def _background_distance(bgr: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(cv2.GaussianBlur(bgr, (5, 5), 0), cv2.COLOR_BGR2LAB).astype(np.float32)
    h, w = lab.shape[:2]
    t = max(3, int(0.03 * min(h, w)))
    ring = np.concatenate([lab[:t].reshape(-1, 3), lab[-t:].reshape(-1, 3),
                           lab[:, :t].reshape(-1, 3), lab[:, -t:].reshape(-1, 3)])
    bg = np.median(ring, axis=0)
    d = np.linalg.norm(lab - bg, axis=2)
    d8 = cv2.normalize(d, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    _, m = cv2.threshold(d8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return m


def _chroma_otsu(bgr: np.ndarray) -> np.ndarray:
    cr = cv2.GaussianBlur(cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)[:, :, 1], (5, 5), 0)
    _, m = cv2.threshold(cr, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return m


def _chroma_kmeans(bgr: np.ndarray) -> np.ndarray:
    ycc = cv2.cvtColor(cv2.GaussianBlur(bgr, (5, 5), 0), cv2.COLOR_BGR2YCrCb)
    data = ycc[:, :, 1:].reshape(-1, 2).astype(np.float32)
    cv2.setRNGSeed(0)  # deterministic
    _, lab, cen = cv2.kmeans(data, 2, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5),
                             3, cv2.KMEANS_PP_CENTERS)
    # skin = the cluster further from neutral grey (128, 128) in the chroma plane
    fg = int(np.argmax(np.linalg.norm(cen - 128.0, axis=1)))
    return ((lab.reshape(ycc.shape[:2]) == fg) * 255).astype(np.uint8)


def _plausibility(m: np.ndarray) -> float:
    """0..1: how much does this blob look like a photographed open hand?"""
    h, w = m.shape
    area = float((m > 0).sum())
    frac = area / (h * w)
    if frac < 0.06 or frac > 0.80:
        return 0.0
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cnts, key=cv2.contourArea)
    hull = cv2.contourArea(cv2.convexHull(c))
    solidity = area / max(hull, 1.0)
    border = np.concatenate([m[0], m[-1], m[:, 0], m[:, -1]])
    contact = float((border > 0).mean())
    # An open hand with spread fingers has solidity ~0.6-0.85; a ragged background
    # blob is far lower, a filled rectangle (whole frame) far higher.
    s = float(np.clip((solidity - 0.45) / 0.25, 0, 1)) * (1 - 0.6 * min(contact / 0.5, 1.0))
    if solidity > 0.97:
        s *= 0.3
    return s * (1.0 if 0.10 <= frac <= 0.65 else 0.7)


def _grabcut(bgr: np.ndarray) -> np.ndarray:
    h, w = bgr.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    rect = (int(0.06 * w), int(0.04 * h), int(0.88 * w), int(0.92 * h))
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(bgr, mask, rect, bgd, fgd, 4, cv2.GC_INIT_WITH_RECT)
    return np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)


def segment_hand(bgr: np.ndarray) -> Segmentation:
    h, w = bgr.shape[:2]
    s = WORK_WIDTH / w if w > WORK_WIDTH else 1.0
    small = cv2.resize(bgr, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else bgr
    cands = {"background-distance": _background_distance, "chroma-otsu": _chroma_otsu,
             "chroma-kmeans": _chroma_kmeans, "fixed-range": _fixed_range}
    best_name, best_mask, best = "", None, -1.0
    for name, fn in cands.items():
        m = _clean(fn(small))
        if not m.any():
            continue
        sc = _plausibility(m)
        if sc > best:
            best_name, best_mask, best = name, m, sc
    if best < ACCEPT_SCORE:
        g = _clean(_grabcut(small))
        gs = _plausibility(g) if g.any() else 0.0
        if gs > best:
            best_name, best_mask, best = "grabcut", g, gs
    if best_mask is None or best < REJECT_SCORE:      # nothing hand-like (blank wall, uniform image...)
        return Segmentation(np.zeros((h, w), np.uint8), "none", 0.0)
    if s < 1:
        best_mask = cv2.resize(best_mask, (w, h), interpolation=cv2.INTER_NEAREST)
    return Segmentation(best_mask, best_name, round(best, 2))
