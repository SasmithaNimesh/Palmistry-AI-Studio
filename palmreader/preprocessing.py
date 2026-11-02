"""Task 02: digital image processing pipeline (every stage is returned for display)."""
from __future__ import annotations
import cv2
import numpy as np
from .segmentation import segment_hand

TARGET_WIDTH = 900


def _to_rgb(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if img.ndim == 3 else img


# Original-vs-processed comparisons shown in the UI: first panel is the "before".
COMPARISONS = [
    dict(title="Resize + normalise, then grayscale", panels=["1 Resized + normalised", "2 Grayscale"],
         why="Fixed width makes every threshold scale-independent; min-max normalisation stretches the "
             "intensity range; grayscale keeps the luminance in which creases appear as dark valleys."),
    dict(title="Noise reduction (Gaussian blur)", panels=["2 Grayscale", "3 Gaussian blur (denoise)"],
         why="Skin texture and sensor noise create false edges. A 5x5 Gaussian (sigma 1.2) removes the "
             "high-frequency grain while keeping crease-sized structures."),
    dict(title="Contrast enhancement (CLAHE)", panels=["3 Gaussian blur (denoise)", "4 CLAHE contrast",
                                                       "4h Histogram before/after CLAHE"],
         why="CLAHE equalises the histogram per 8x8 tile with a clip limit, so faint creases gain contrast "
             "without amplifying noise or blowing out bright areas (plain global equalisation would)."),
    dict(title="Hand segmentation", panels=["1 Resized + normalised", "5b Segmentation overlay"],
         why="The mask limits all later steps to the palm. The threshold is chosen from the image itself "
             "(Otsu / k-means), so it adapts to skin tone."),
    dict(title="Edge detection (Sobel vs Canny)", panels=["4 CLAHE contrast", "7a Sobel gradient", "7b Canny edges"],
         why="Sobel shows gradient strength everywhere (soft, thick). Canny thins it to 1-px edges with "
             "hysteresis thresholds taken from the image median."),
    dict(title="Thresholding + morphology", panels=["6 Black-hat (line boost)", "8a Global Otsu threshold",
                                                    "8 Threshold + morphology"],
         why="Black-hat highlights thin dark creases. One global Otsu threshold breaks under uneven light; "
             "the adaptive threshold decides per neighbourhood, then close/open morphology joins gaps and "
             "deletes specks."),
]


def histogram_image(before: np.ndarray, after: np.ndarray, mask: np.ndarray | None = None,
                    size: tuple[int, int] = (512, 256)) -> np.ndarray:
    """RGB line plot of the grey-level histograms (hand pixels only): grey = before, red = after."""
    w, h = size
    canvas = np.full((h, w, 3), 255, np.uint8)
    m = mask if mask is not None and mask.any() else None
    for img, col in ((before, (120, 120, 120)), (after, (220, 40, 40))):
        hist = cv2.calcHist([img], [0], m, [256], [0, 256]).ravel()
        hist = hist / max(hist.max(), 1) * (h - 20)
        pts = np.array([[int(i * (w - 1) / 255), h - 5 - int(v)] for i, v in enumerate(hist)], np.int32)
        cv2.polylines(canvas, [pts], False, col, 2, cv2.LINE_AA)
    cv2.putText(canvas, "grey = before CLAHE", (10, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (90, 90, 90), 1, cv2.LINE_AA)
    cv2.putText(canvas, "red = after CLAHE", (10, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 30, 30), 1, cv2.LINE_AA)
    return canvas


def enhance_sharpness(img: np.ndarray, strength: float = 0.6) -> np.ndarray:
    """Enhance edge contrast and crease definition before processing via unsharp masking.

    Formula: sharpened = original + strength * (original - gaussian_blur)
    """
    if strength <= 0.01:
        return img
    blurred = cv2.GaussianBlur(img, (0, 0), sigmaX=2.0, sigmaY=2.0)
    sharpened = cv2.addWeighted(img, 1.0 + strength, blurred, -strength, 0)
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def run_pipeline(bgr: np.ndarray, hand_mask: np.ndarray | None = None, sharpen_strength: float = 0.0) -> dict[str, np.ndarray]:
    """Return a dict of stage name -> display image (RGB or single channel).

    Keys starting with "_" are internal arrays used by the feature stage.

    Techniques used:
      0. Pre-processing sharpness enhancement     (unsharp masking)
      1. Resize + min-max normalisation           (geometric / intensity normalisation)
      2. RGB -> grayscale                         (colour-space conversion)
      3. Gaussian blur                            (noise reduction)
      4. CLAHE                                    (local contrast enhancement)
      5. Adaptive hand segmentation (Otsu / k-means on colour, GrabCut fallback) + morphology
      6. Black-hat transform                      (morphological line enhancement)
      7. Sobel gradient magnitude and Canny edges (edge detection)
      8. Global Otsu vs adaptive threshold, then morphological close/open (binary crease map)

    hand_mask: optional full-size mask from validation (avoids segmenting twice).
    """
    if sharpen_strength > 0.01:
        bgr = enhance_sharpness(bgr, sharpen_strength)

    h, w = bgr.shape[:2]
    scale = TARGET_WIDTH / w
    img = cv2.resize(bgr, (TARGET_WIDTH, int(h * scale)),
                     interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
    norm = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
    gray = cv2.cvtColor(norm, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 1.2)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(blur)

    if hand_mask is not None:
        hand = cv2.resize(hand_mask, (norm.shape[1], norm.shape[0]), interpolation=cv2.INTER_NEAREST)
    else:
        hand = segment_hand(norm).mask
    segmented = cv2.bitwise_and(norm, norm, mask=hand)
    overlay = norm.copy()
    overlay[hand > 0] = (0.55 * overlay[hand > 0] + 0.45 * np.array([0, 200, 0])).astype(np.uint8)
    cv2.drawContours(overlay, cv2.findContours(hand, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0], -1, (0, 255, 255), 2)

    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
    blackhat = cv2.morphologyEx(clahe, cv2.MORPH_BLACKHAT, k)
    # crease depth in grey levels measured on the blurred image BEFORE CLAHE and before the
    # max-normalisation above, both of which would turn a barely visible crease into a strong one
    # (also before the min-max normalisation of step 1, whose offset would inflate relative depth)
    blur_raw = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (5, 5), 1.2)
    blackhat_abs = cv2.morphologyEx(blur_raw, cv2.MORPH_BLACKHAT, k).astype(np.float32)
    blackhat = cv2.normalize(blackhat, None, 0, 255, cv2.NORM_MINMAX)

    sx = cv2.Sobel(clahe, cv2.CV_32F, 1, 0, ksize=3)
    sy = cv2.Sobel(clahe, cv2.CV_32F, 0, 1, ksize=3)
    sobel = cv2.normalize(cv2.magnitude(sx, sy), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    med = float(np.median(clahe[hand > 0])) if hand.any() else float(np.median(clahe))
    canny = cv2.Canny(clahe, int(max(0, 0.66 * med)), int(min(255, 1.33 * med)))
    canny = cv2.bitwise_and(canny, canny, mask=cv2.erode(hand, np.ones((15, 15), np.uint8)))

    inner = cv2.erode(hand, np.ones((25, 25), np.uint8))
    # global Otsu: ONE threshold for the whole image -> fails under uneven lighting (shown for comparison)
    otsu_src = cv2.bitwise_not(clahe)                      # creases are darker -> invert so they are "on"
    if inner.any():
        otsu_thr, _ = cv2.threshold(otsu_src[inner > 0].reshape(-1, 1), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        otsu_thr = 255.0
    otsu_map = cv2.bitwise_and(((otsu_src > otsu_thr) * 255).astype(np.uint8), inner)
    # adaptive: threshold computed per 31x31 neighbourhood on the black-hat map -> robust to shading
    thr = cv2.adaptiveThreshold(blackhat, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, -6)
    thr = cv2.bitwise_and(thr, thr, mask=inner)
    creases = cv2.morphologyEx(thr, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    creases = cv2.morphologyEx(creases, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))

    return {
        "1 Resized + normalised": _to_rgb(norm),
        "2 Grayscale": gray,
        "3 Gaussian blur (denoise)": blur,
        "4 CLAHE contrast": clahe,
        "5 Hand segmentation": _to_rgb(segmented),
        "5b Segmentation overlay": _to_rgb(overlay),
        "6 Black-hat (line boost)": blackhat,
        "7a Sobel gradient": sobel,
        "7b Canny edges": canny,
        "8a Global Otsu threshold": otsu_map,
        "8 Threshold + morphology": creases,
        "4h Histogram before/after CLAHE": histogram_image(gray, clahe, hand),
        "_hand_mask": hand,
        "_clahe": clahe,
        "_blackhat": blackhat,
        "_blackhat_abs": blackhat_abs,
        "_blur": blur_raw,
        "_creases": creases,
        "_norm": norm,
    }
