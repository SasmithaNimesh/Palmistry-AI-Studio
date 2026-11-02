"""Task 03: palm geometry + principal-line detection and annotation.

Everything here is classical computer vision (no LLM). Each line carries a
confidence and a status ("detected", "uncertain" or "not_detected") so that
downstream text never invents features.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import cv2
import numpy as np
from skimage.morphology import skeletonize

LINE_COLORS = {  # RGB
    "heart_line": (230, 57, 70),
    "head_line": (29, 120, 220),
    "life_line": (46, 170, 90),
    "fate_line": (240, 160, 20),
}
DETECT_T, UNCERTAIN_T = 0.55, 0.30
MIN_PIECE_PX = 8     # shortest skeleton piece kept for re-joining
MERGE_GAP_PX = 16    # max gap bridged when re-joining pieces cut at a junction
SPUR_PX = 8           # side branches shorter than this are pruned before splitting at junctions
MAX_CANDIDATES = 60   # longest skeleton pieces examined per palm
MIN_REL_DEPTH = 0.07  # crease must be >= 7% darker than the palm's mean brightness (absolute, not normalised)
MIN_CONTRAST = 2.0    # line response / mean response of the surrounding palm texture


@dataclass
class LineFeature:
    name: str
    status: str = "not_detected"           # detected | uncertain | not_detected
    confidence: float = 0.0
    relative_length: float | None = None   # path length / palm radius
    curvature: str | None = None           # straight | gently curved | strongly curved
    prominence: str | None = None          # faint | moderate | strong (ridge strength)
    start_region: str | None = None
    end_region: str | None = None
    crease_depth: float | None = None      # depth below the surrounding skin / mean palm brightness
    ridge_contrast: float | None = None    # line response / palm texture level (for threshold tuning)
    path: list | None = None               # pixel points, for drawing only


def _open_disc(hand: np.ndarray, dist: np.ndarray, radius: float) -> np.ndarray:
    """Morphological opening with a disc of the given radius, via two distance transforms.

    Identical in effect to cv2.morphologyEx(OPEN, ellipse) but O(pixels): the huge (~280 px) kernel
    took 1-8 s per palm, which made the app and the tests sluggish."""
    core = (dist > radius).astype(np.uint8)                       # erosion by the disc
    grown = cv2.distanceTransform(1 - core, cv2.DIST_L2, 5)       # distance to the eroded core
    return (((grown <= radius) & (hand > 0)) * 255).astype(np.uint8)   # dilation by the disc


def _palm_frame(hand: np.ndarray):
    """Find palm centre, radius, finger direction u and thumb direction t."""
    dist = cv2.distanceTransform(hand, cv2.DIST_L2, 5)
    _, r, _, cxy = cv2.minMaxLoc(dist)
    c = np.array(cxy, dtype=np.float32)
    palm = _open_disc(hand, dist, 0.6 * r)    # remove everything narrower than 1.2 r: the fingers
    # the distance-transform maximum wanders by several px on a plateau; the centroid of the
    # opened palm is stable under rotation, so use it as the palm centre
    m = cv2.moments(palm, binaryImage=True)
    if m["m00"] > 0:
        c = np.array([m["m10"] / m["m00"], m["m01"] / m["m00"]], dtype=np.float32)
    fingers = cv2.subtract(hand, cv2.dilate(palm, np.ones((5, 5), np.uint8)))
    fingers = cv2.morphologyEx(fingers, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, _, stats, cent = cv2.connectedComponentsWithStats(fingers)
    blobs = [(stats[i, cv2.CC_STAT_AREA], cent[i]) for i in range(1, n)
             if stats[i, cv2.CC_STAT_AREA] > 0.15 * r * r]
    if not blobs:
        return None
    pts = np.array([b[1] for b in blobs], dtype=np.float32) - c
    w = np.array([b[0] for b in blobs], dtype=np.float32)
    def direction(sel):
        v = (pts[sel] * w[sel, None]).sum(0)
        far = pts[sel][np.argmax(np.linalg.norm(pts[sel], axis=1))]
        v = v / (np.linalg.norm(v) + 1e-6)
        return v if np.dot(v, far) >= 0 else far / (np.linalg.norm(far) + 1e-6)

    # pass 1: rough finger direction from all blobs (thumb included) -> find the thumb
    u = direction(np.ones(len(pts), bool))
    thumb_i = int(np.argmin(pts @ u))          # thumb = lowest blob along u, off to one side
    # pass 2: re-estimate the direction from the four fingers only; the thumb drags pass 1 ~5 deg off
    if len(pts) >= 3:
        keep = np.arange(len(pts)) != thumb_i
        u = direction(keep)
    t_perp = np.array([-u[1], u[0]], dtype=np.float32)
    t = t_perp if np.dot(pts[thumb_i], t_perp) >= 0 else -t_perp
    ys, xs = np.nonzero(palm)
    q = np.stack([xs, ys], 1).astype(np.float32) - c
    pu, pv = q @ u, q @ t
    fys, fxs = np.nonzero(fingers)
    fq = np.stack([fxs, fys], 1).astype(np.float32) - c
    finger_len = float((fq @ u).max() - pu.max()) if len(fq) else 0.0
    return dict(c=c, r=float(r), u=u, t=t, palm=palm,
                palm_len=float(pu.max() - pu.min()), palm_wid=float(pv.max() - pv.min()),
                finger_len=max(finger_len, 0.0),
                n_fingers=len(blobs) - 1)   # the thumb blob is NOT a finger


# Palm-shape thresholds (heuristics, NOT validated on a labelled dataset):
#  * SQUARE_MAX_RATIO: palmistry calls a palm "square" when its length is about its width.
#    1.15 allows +-15% for segmentation error (the wrist end of the palm is cut by the
#    opening operation, so measured length is only approximate) and for camera tilt.
#  * LONG_FINGER_RATIO: finger length (longest finger beyond the palm) / palm length.
#    Adult anthropometric tables put the middle finger at roughly 0.75-0.85 of palm length,
#    so 0.8 splits the typical range in the middle; "long" therefore means "longer than
#    average", which is how palmistry uses the term. Photos taken at an angle or with curled
#    fingers shorten the measured value, so the label is approximate and reported as such.
SQUARE_MAX_RATIO = 1.15
LONG_FINGER_RATIO = 0.8
# A measured ratio within this distance of a threshold flips with a few pixels of segmentation
# jitter (the same synthetic hand measured 1.14-1.16 across rotations against a 1.15 limit and
# changed type), so such hands are reported as "Uncertain" instead of being forced into a class.
BORDERLINE_MARGIN = 0.05


def _palm_shape(fr) -> dict:
    ratio_pl = fr["palm_len"] / max(fr["palm_wid"], 1.0)
    finger_ratio = fr["finger_len"] / max(fr["palm_len"], 1.0)
    shape = "square" if ratio_pl < SQUARE_MAX_RATIO else "rectangular"
    fingers = "long" if finger_ratio > LONG_FINGER_RATIO else "short"
    element = {("square", "short"): "Earth", ("square", "long"): "Air",
               ("rectangular", "short"): "Fire", ("rectangular", "long"): "Water"}[(shape, fingers)]
    border = [n for n, v, t in (("palm length/width", ratio_pl, SQUARE_MAX_RATIO),
                                ("finger/palm length", finger_ratio, LONG_FINGER_RATIO))
              if abs(v - t) < BORDERLINE_MARGIN]
    note = "approximate: derived from silhouette ratios"
    if border:
        element = "Uncertain"
        note += f"; {' and '.join(border)} is too close to the class boundary to call"
    return dict(palm_shape=shape, finger_length=fingers, palmistry_hand_type=element,
                palm_length_to_width=round(ratio_pl, 2), finger_to_palm_length=round(finger_ratio, 2), note=note)


def _region(a: float, b: float) -> str:
    v = "upper" if a > 0.35 else ("lower" if a < -0.35 else "middle")
    h = "thumb side" if b > 0.35 else ("pinky side" if b < -0.35 else "centre")
    return f"{v} palm, {h}"


def _neighbours(sk: np.ndarray) -> np.ndarray:
    return cv2.filter2D(sk, -1, np.ones((3, 3), np.float32), borderType=cv2.BORDER_CONSTANT) - sk


def _prune_spurs(sk: np.ndarray, n: int = SPUR_PX) -> np.ndarray:
    """Remove side branches shorter than ~n px. JPEG noise grows tiny spurs on a skeleton; each spur
    creates a junction, and cutting at junctions then split one real crease into two short pieces
    that scored too low (seen on a JPEG-compressed synthetic hand)."""
    cur = sk.copy()
    for _ in range(n):                                   # eat every free end n steps
        cur[(cur > 0) & (_neighbours(cur) <= 1)] = 0
    grow = ((cur > 0) & (_neighbours(cur) <= 1)).astype(np.uint8)   # ends of the surviving long branches
    for _ in range(n):                                   # grow them back along the original skeleton
        grow = cv2.dilate(grow, np.ones((3, 3), np.uint8)) & sk
    return (cur | grow).astype(np.uint8)


def _candidates(ridge: np.ndarray, fr):
    """Skeletonise strong ridges inside the palm; return components in palm-frame coords."""
    roi = cv2.erode(fr["palm"], cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    br = cv2.bitwise_and(ridge, ridge, mask=roi)
    br = cv2.dilate(br, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))  # bridge small gaps
    sk = _prune_spurs(skeletonize(br > 0).astype(np.uint8))
    # split at junctions so crossing/touching creases become separate candidates
    nb = cv2.filter2D(sk, -1, np.ones((3, 3), np.float32), borderType=cv2.BORDER_CONSTANT) - sk
    junction = ((sk > 0) & (nb >= 3)).astype(np.uint8)
    sk[cv2.dilate(junction, np.ones((5, 5), np.uint8)) > 0] = 0
    n, lab = cv2.connectedComponents(sk, connectivity=8)
    c, u, t, r = fr["c"], fr["u"], fr["t"], fr["r"]
    # Arc length, not pixel count: a diagonal step covers sqrt(2) px of length but is ONE skeleton
    # pixel, so counting pixels made identical lines look ~10% shorter when the hand was rotated.
    length = np.zeros(n)
    for da, db, w in ((lab[:, :-1], lab[:, 1:], 1.0), (lab[:-1], lab[1:], 1.0),
                      (lab[:-1, :-1], lab[1:, 1:], 2 ** 0.5), (lab[:-1, 1:], lab[1:, :-1], 2 ** 0.5)):
        same = (da == db) & (da > 0)
        length += w * np.bincount(da[same], minlength=n)
    # pieces of at least MIN_PIECE_PX are kept so short stubs can be re-joined to their crease;
    # the 200 longest bound the work on a very textured palm
    order = [i for i in np.argsort(length)[::-1][:200] if i > 0 and length[i] >= MIN_PIECE_PX]
    pieces = []
    for i in order:
        ys, xs = np.nonzero(lab == i)
        pieces.append((np.stack([xs, ys], 1).astype(np.float32), float(length[i])))
    comps = []
    # only creases at least half a palm radius long are candidates; cap the count
    for p, ln in sorted(_merge_pieces(pieces), key=lambda x: -x[1]):
        if ln < 0.5 * r or len(comps) >= MAX_CANDIDATES:
            continue
        q = p - c
        comps.append(dict(px=p, a=(q @ u) / r, b=(q @ t) / r, n=ln))
    return comps


def _ends(px: np.ndarray):
    """The two extreme points of a piece along its principal axis, each with an outward direction."""
    centre = px.mean(0)
    axis = np.linalg.svd(px - centre, full_matrices=False)[2][0]
    proj = (px - centre) @ axis
    out = []
    for idx in (int(np.argmin(proj)), int(np.argmax(proj))):
        e = px[idx]
        near = px[np.linalg.norm(px - e, axis=1) <= 20]
        d = e - near.mean(0)
        out.append((e, d / (np.linalg.norm(d) + 1e-6)))
    return out


def _merge_pieces(pieces, gap: float = MERGE_GAP_PX, min_cos: float = 0.8):
    """Re-join pieces of one crease that were cut at a junction (a crossing line, or a JPEG-noise
    spur). Two pieces merge when two of their ends are within `gap` px AND point at each other
    (anti-parallel outward directions, connecting vector along them), so a crossing crease is
    rejoined but a T-junction between different lines is not."""
    pieces = [(p, n, _ends(p)) for p, n in pieces if len(p) >= 3]
    merged = True
    while merged and len(pieces) > 1:
        merged = False
        for i in range(len(pieces)):
            for j in range(i + 1, len(pieces)):
                (pi, ni, ei), (pj, nj, ej) = pieces[i], pieces[j]
                hit = False
                for a, da in ei:
                    for b, db in ej:
                        g = b - a
                        dist = float(np.linalg.norm(g))
                        if dist <= gap and float(da @ db) < -min_cos and (dist < 1e-3 or float((g / dist) @ da) > 0.7):
                            hit = True
                if hit:
                    px = np.vstack([pi, pj])
                    pieces[j] = (px, ni + nj + gap / 2, _ends(px))
                    del pieces[i]
                    merged = True
                    break
            if merged:
                break
    return [(p, n) for p, n, _ in pieces]


def _gauss(x: float, m: float, s: float) -> float:
    return float(np.exp(-((x - m) / s) ** 2))


def _score(name: str, k: dict, r: float) -> float:
    a, b, n = k["a"], k["b"], k["n"]
    da, db = float(np.ptp(a)), float(np.ptp(b))
    hor = db / (da + db + 1e-6)
    ver = 1 - hor
    ln = min(1.0, n / (1.3 * r))
    if name == "heart_line":
        return ln * hor * _gauss(a.mean(), 0.55, 0.30) * (0.6 + 0.4 * min(1, db))
    if name == "head_line":
        return ln * hor * _gauss(a.mean(), 0.05, 0.30) * (0.6 + 0.4 * min(1, db))
    if name == "life_line":
        return ln * ver * min(1.0, da / 0.9) * float(1 / (1 + np.exp(-6 * (b.mean() - 0.1))))
    if name == "fate_line":
        return ln * ver * min(1.0, da / 0.8) * _gauss(b.mean(), -0.05, 0.28) * _gauss(a.mean(), -0.1, 0.5)
    return 0.0


def _describe(name: str, k: dict, score: float, strength: float, fr, contrast: float, depth: float) -> LineFeature:
    # order points: life/fate run along u (start high), heart/head along t (start thumb side)
    key = k["a"] if name in ("life_line", "fate_line") else k["b"]
    order = np.argsort(key)[::-1]
    px = k["px"][order]
    chord = float(np.linalg.norm(px[0] - px[-1]))
    ratio = chord / max(k["n"], 1)
    curv = "straight" if ratio > 0.9 else ("gently curved" if ratio > 0.7 else "strongly curved")
    prom = "strong" if strength > 110 else ("moderate" if strength > 70 else "faint")
    # "detected" needs a good geometric fit AND a crease that is clearly visible: absolutely deep
    # enough (>= MIN_REL_DEPTH below the skin) and standing out from the palm's own texture
    # (>= MIN_CONTRAST). A well-placed but faint ridge is reported as uncertain (and not drawn).
    # (An earlier gate on the max-normalised ridge strength was dropped: it was biased against dark skin.)
    status = "detected" if (score >= DETECT_T and contrast >= MIN_CONTRAST and depth >= MIN_REL_DEPTH) else "uncertain"
    ia, ib = order[0], order[-1]
    return LineFeature(name, status, round(float(min(score, 1.0)), 2), round(k["n"] / fr["r"], 2), curv, prom,
                       _region(k["a"][ia], k["b"][ia]), _region(k["a"][ib], k["b"][ib]), round(depth, 3), round(contrast, 2),
                       px[:: max(1, len(px) // 120)].astype(int).tolist())


def analyse_palm(stages: dict, side: str) -> tuple[dict, np.ndarray]:
    """Return (structured feature dict, annotated RGB image)."""
    hand = stages["_hand_mask"]
    base = stages["1 Resized + normalised"].copy()
    fr = _palm_frame(hand)
    out = {"side": side, "palm_detected": fr is not None, "lines": {}, "notes": []}
    if fr is None:
        out["notes"].append("Palm geometry could not be established (fingers/thumb not separable).")
        for n in LINE_COLORS:
            out["lines"][n] = asdict(LineFeature(n))
        _legend(base, out["lines"])
        return out, base

    out["palm"] = _palm_shape(fr)
    if fr["n_fingers"] < 4:
        out["notes"].append(f"Only {fr['n_fingers']} of 4 fingers (thumb excluded) could be separated; "
                            "orientation and palm-shape values may be unreliable. Spread the fingers apart.")

    comps = _candidates(stages["_creases"], fr)
    bh = stages["_blackhat"]
    roi = cv2.erode(fr["palm"], np.ones((15, 15), np.uint8)) > 0
    palm_bh = float(bh[roi].mean()) if roi.any() else 1.0   # background crease-texture level
    palm_level = max(float(stages["_blur"][roi].mean()), 1.0) if roi.any() else 255.0   # mean palm brightness
    names = list(LINE_COLORS)
    pairs = sorted(((_score(n, k, fr["r"]), n, i) for n in names for i, k in enumerate(comps)), reverse=True)
    chosen: dict[str, tuple[int, float]] = {}
    used: set[int] = set()
    for s, n, i in pairs:  # greedy: best score first, one crease per line
        if n in chosen or i in used or s < UNCERTAIN_T:
            continue
        chosen[n] = (i, s)
        used.add(i)

    for n in names:
        if n in chosen:
            i, s = chosen[n]
            k = comps[i]
            strength = float(bh[k["px"][:, 1].astype(int), k["px"][:, 0].astype(int)].mean())
            contrast = strength / max(palm_bh, 1.0)
            depth = float(stages["_blackhat_abs"][k["px"][:, 1].astype(int), k["px"][:, 0].astype(int)].mean()) / palm_level
            out["lines"][n] = asdict(_describe(n, k, s, strength, fr, contrast, depth))
        else:
            out["lines"][n] = asdict(LineFeature(n))

    ann = base.copy()
    ctr = tuple(int(x) for x in fr["c"])
    cv2.circle(ann, ctr, int(fr["r"]), (255, 255, 255), 1)
    cv2.arrowedLine(ann, ctr, tuple(int(x) for x in fr["c"] + fr["u"] * fr["r"] * 1.3),
                    (255, 255, 255), 2, tipLength=0.15)
    for n, d in out["lines"].items():
        if d["status"] != "detected":      # never draw a line the pipeline is not confident about
            continue
        pts = np.array(d["path"], dtype=np.int32).reshape(-1, 1, 2)
        col = LINE_COLORS[n]
        cv2.polylines(ann, [pts], False, col, 4, cv2.LINE_AA)
        x, y = (int(v) for v in pts[len(pts) // 2, 0])
        label = n.replace("_", " ").title()
        cv2.putText(ann, label, (x + 6, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(ann, label, (x + 6, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, col, 2, cv2.LINE_AA)
    _legend(ann, out["lines"])
    return out, ann


def _legend(img: np.ndarray, lines: dict) -> None:
    """Status of every line in the corner: uncertain / absent lines are listed, never drawn."""
    pad, lh = 8, 22
    box_h = pad * 2 + lh * len(lines)
    cv2.rectangle(img, (6, 6), (330, 6 + box_h), (255, 255, 255), -1)
    cv2.rectangle(img, (6, 6), (330, 6 + box_h), (60, 60, 60), 1)
    for i, (n, d) in enumerate(lines.items()):
        y = 6 + pad + lh * i + 14
        txt = {"detected": "detected", "uncertain": "uncertain (not drawn)",
               "not_detected": "not detected"}[d["status"]]
        cv2.circle(img, (20, y - 5), 6, LINE_COLORS[n] if d["status"] == "detected" else (170, 170, 170), -1)
        cv2.putText(img, f"{n.replace('_', ' ').title()}: {txt}", (34, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (30, 30, 30), 1, cv2.LINE_AA)
