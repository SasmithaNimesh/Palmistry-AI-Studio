"""Adaptive skin segmentation across tones, backgrounds, rotations and mirroring."""
import numpy as np
import pytest

from synthetic import synthetic_hand
from palmreader.segmentation import _fixed_range, _clean, segment_hand


def iou(a, b):
    a, b = a > 0, b > 0
    return (a & b).sum() / max((a | b).sum(), 1)


@pytest.mark.parametrize("tone", ["light", "medium", "dark", "deep"])
@pytest.mark.parametrize("bg", ["white", "grey", "cream"])
@pytest.mark.parametrize("angle,mirror", [(0, False), (90, False), (37, True), (180, True)])
def test_adaptive_segmentation_matches_ground_truth(tone, bg, angle, mirror):
    img, gt = synthetic_hand(tone, angle, mirror, bg=bg)
    seg = segment_hand(img)
    assert iou(seg.mask, gt) > 0.9, (seg.method, seg.score)


def test_old_fixed_ranges_fail_on_deep_skin_but_adaptive_does_not():
    img, gt = synthetic_hand("deep")
    old = _clean(_fixed_range(img))
    assert iou(old, gt) < 0.5          # the original bug
    assert iou(segment_hand(img).mask, gt) > 0.9


def test_grabcut_fallback_on_cluttered_background():
    """Strong vertical gradient + noise background: the colour-distance candidates are poor, the
    fallback must still return a hand-sized blob (weaker bar than the clean cases)."""
    img, gt = synthetic_hand("medium")
    yy = np.linspace(0, 1, img.shape[0], dtype=np.float32)[:, None, None]
    bgc = (60 + 170 * yy) * np.ones((1, img.shape[1], 3), np.float32)
    bgc += np.random.default_rng(1).normal(0, 10, bgc.shape)
    img2 = np.where((gt > 0)[:, :, None], img, np.clip(bgc, 0, 255).astype(np.uint8))
    seg = segment_hand(img2)
    assert iou(seg.mask, gt) > 0.75, (seg.method, seg.score)
