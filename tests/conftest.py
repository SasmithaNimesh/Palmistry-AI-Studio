"""Shared fixtures: run the whole pipeline on a synthetic hand once and reuse the result."""
from functools import lru_cache

from synthetic import png_bytes, synthetic_hand
from palmreader.features import analyse_palm
from palmreader.preprocessing import run_pipeline
from palmreader.validation import validate_upload


@lru_cache(maxsize=3)   # stage dicts are large; an unbounded cache made the suite swap
def analyse(tone="medium", angle=0.0, mirror=False, creases=True, bg="white"):
    img, gt = synthetic_hand(tone, angle, mirror, creases, bg)
    v = validate_upload("hand.png", png_bytes(img), "Left")
    stages = run_pipeline(v.image, v.hand_mask)
    feat, ann = analyse_palm(stages, "Left")
    return v, stages, feat, ann
