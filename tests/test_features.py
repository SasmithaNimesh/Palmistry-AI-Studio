"""Task 02/03: pipeline stages, palm geometry, line detection and honest labelling."""
import numpy as np
import pytest

from conftest import analyse
from synthetic import png_bytes, synthetic_hand
from palmreader import features as F
from palmreader.preprocessing import COMPARISONS
from palmreader.features import LINE_COLORS, _palm_shape

DETECTABLE = ("heart_line", "head_line", "life_line")


def statuses(feat):
    return {n: d["status"] for n, d in feat["lines"].items()}


def test_pipeline_has_all_stages_and_comparisons():
    _, stages, _, _ = analyse()
    public = [k for k in stages if not k.startswith("_")]
    assert len(public) >= 10
    for comp in COMPARISONS:                       # every before/after panel exists and is displayable
        for key in comp["panels"]:
            assert key in stages and stages[key].ndim in (2, 3)
    titles = " ".join(c["title"] for c in COMPARISONS)
    for word in ("CLAHE", "Sobel", "Canny", "Thresholding"):
        assert word in titles


def test_clahe_changes_contrast_and_histogram_image_is_rgb():
    _, st, _, _ = analyse()
    assert st["4 CLAHE contrast"].std() > st["3 Gaussian blur (denoise)"].std() * 0.9
    assert st["4h Histogram before/after CLAHE"].shape[2] == 3


@pytest.mark.parametrize("tone", ["light", "medium", "dark", "deep"])
@pytest.mark.parametrize("angle,mirror", [(0, False), (0, True), (90, False), (37, True), (180, False)])
def test_lines_found_for_every_tone_rotation_and_mirror(tone, angle, mirror):
    v, _, feat, _ = analyse(tone, angle, mirror)
    assert v.ok
    assert feat["palm_detected"]
    assert feat["notes"] == []                     # 4 fingers separated, thumb not counted as a finger
    st = statuses(feat)
    assert all(st[n] == "detected" for n in DETECTABLE), st
    assert st["fate_line"] == "not_detected"       # the synthetic hand has no fate line


def test_no_lines_invented_on_a_palm_without_creases():
    for tone in ("light", "dark"):
        _, _, feat, _ = analyse(tone, creases=False)
        assert set(statuses(feat).values()) == {"not_detected"}


def test_detected_lines_are_drawn_and_others_are_not():
    _, _, feat, ann = analyse()
    legend_h = 6 + 16 + 22 * 4 + 6                 # rows below the legend box only
    body = ann[legend_h:]

    def n_px(name):
        return int((np.all(body == LINE_COLORS[name], axis=2)).sum())
    assert all(n_px(n) > 100 for n in DETECTABLE)
    assert n_px("fate_line") == 0


def test_uncertain_lines_are_never_drawn(monkeypatch):
    monkeypatch.setattr(F, "MIN_REL_DEPTH", 1e9)    # force every candidate into "uncertain"
    img, _ = synthetic_hand("medium")
    from palmreader.preprocessing import run_pipeline
    from palmreader.validation import validate_upload
    v = validate_upload("h.png", png_bytes(img), "Left")
    feat, ann = F.analyse_palm(run_pipeline(v.image, v.hand_mask), "Left")
    assert {statuses(feat)[n] for n in DETECTABLE} == {"uncertain"}
    body = ann[130:]
    for n, col in LINE_COLORS.items():
        assert int(np.all(body == col, axis=2).sum()) == 0, f"{n} was drawn although uncertain"


@pytest.mark.parametrize("strength", [0.05, 0.1])
def test_barely_visible_creases_are_never_confident(strength):
    """Creases at 5-10% of normal depth are lost in the skin texture: the pipeline may say
    'uncertain' or 'not detected' but must not claim a confident 'detected' line."""
    from palmreader.preprocessing import run_pipeline
    from palmreader.validation import validate_upload
    img, _ = synthetic_hand("medium", crease_strength=strength)
    v = validate_upload("h.png", png_bytes(img), "Left")
    feat, _ = F.analyse_palm(run_pipeline(v.image, v.hand_mask), "Left")
    assert "detected" not in statuses(feat).values(), feat["lines"]


def test_palm_shape_thresholds_boundaries():
    def fr(pl, pw, fl):
        return dict(palm_len=pl, palm_wid=pw, finger_len=fl)
    assert _palm_shape(fr(100, 100, 60))["palmistry_hand_type"] == "Earth"          # square, short
    assert _palm_shape(fr(100, 100, 100))["palmistry_hand_type"] == "Air"           # square, long
    assert _palm_shape(fr(130, 100, 80))["palmistry_hand_type"] == "Fire"           # rectangular, short
    assert _palm_shape(fr(130, 100, 130))["palmistry_hand_type"] == "Water"         # rectangular, long


def test_borderline_palm_shape_is_reported_as_uncertain_not_forced():
    def fr(pl, pw, fl):
        return dict(palm_len=pl, palm_wid=pw, finger_len=fl)
    for pl, fl in ((114, 60), (118, 60), (100, 80), (130, 108)):                    # near 1.15 or near 0.8
        shape = _palm_shape(fr(pl, 100, fl))
        assert shape["palmistry_hand_type"] == "Uncertain", (pl, fl, shape)
        assert "boundary" in shape["note"]


def test_hand_type_is_stable_under_rotation_and_mirroring():
    types = {analyse("medium", a, m)[2]["palm"]["palmistry_hand_type"]
             for a, m in ((0, False), (15, True), (90, False), (180, False), (200, True))}
    assert len(types) == 1, types


def _through_jpeg(img, quality):
    import cv2
    return cv2.imdecode(cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])[1], cv2.IMREAD_COLOR)


@pytest.mark.parametrize("tone,mirror,angle", [("deep", True, 0), ("light", False, 37), ("medium", True, 90)])
def test_jpeg_compression_does_not_break_lines(tone, mirror, angle):
    """Regression: JPEG noise cut a crease that crosses another into two short pieces (life line
    fell to 'uncertain'); pieces are now re-joined across junctions."""
    from palmreader.preprocessing import run_pipeline
    from palmreader.validation import validate_upload
    img, _ = synthetic_hand(tone, angle, mirror, bg="grey" if tone == "deep" else "white")
    v = validate_upload("h.jpg", png_bytes(_through_jpeg(img, 75)), "Left")
    assert v.ok, (v.errors, v.metrics)
    feat, _ = F.analyse_palm(run_pipeline(v.image, v.hand_mask), "Left")
    assert all(statuses(feat)[n] == "detected" for n in DETECTABLE), statuses(feat)


def test_jpeg_palm_without_creases_still_has_no_lines():
    from palmreader.preprocessing import run_pipeline
    from palmreader.validation import validate_upload
    img, _ = synthetic_hand("medium", creases=False)
    v = validate_upload("h.png", png_bytes(_through_jpeg(img, 60)), "Left")
    feat, _ = F.analyse_palm(run_pipeline(v.image, v.hand_mask), "Left")
    assert set(statuses(feat).values()) == {"not_detected"}
