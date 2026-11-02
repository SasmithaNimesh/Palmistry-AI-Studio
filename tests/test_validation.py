"""Task 01: validation on file problems and on image quality (hand-region metrics)."""
import cv2
import numpy as np
import pytest

from synthetic import png_bytes, synthetic_hand
from palmreader.validation import validate_upload


def v_of(img, name="x.png"):
    return validate_upload(name, png_bytes(img), "Left")


def test_rejects_unsupported_and_corrupt_files():
    assert not validate_upload("x.gif", b"GIF89a", "Left").ok
    assert not validate_upload("x.png", b"not an image", "Left").ok
    assert any("corrupted" in e for e in validate_upload("x.jpg", b"\xff\xd8\xff\x00garbage", "Left").errors)


def test_rejects_low_resolution_and_blank_images():
    tiny = np.full((100, 100, 3), 128, np.uint8)
    assert any("resolution" in e for e in v_of(tiny).errors)
    blank = np.full((800, 800, 3), 128, np.uint8)
    r = v_of(blank)
    assert not r.ok and any("no clear palm" in e for e in r.errors)


@pytest.mark.parametrize("tone", ["light", "medium", "dark"])
@pytest.mark.parametrize("bg", ["white", "grey"])
def test_good_synthetic_hand_passes_every_tone_and_background(tone, bg):
    """Regression for the whole-frame bug: a plain white wall must not make a good photo
    'overexposed' or 'blurry'."""
    img, _ = synthetic_hand(tone, bg=bg)
    r = v_of(img)
    assert r.ok, (r.errors, r.metrics)
    assert not r.errors and r.metrics["hand_fraction"] > 0.12
    assert r.metrics["edge_width_px"] < 5


def test_white_background_alone_does_not_trigger_exposure_errors():
    img, _ = synthetic_hand("medium", bg="white")
    r = v_of(img)
    assert r.metrics["brightness"] < 215          # hand brightness, not the ~240 of the wall
    assert not any("overexposed" in e or "blurry" in e for e in r.errors)


@pytest.mark.parametrize("sigma", [0, 1, 2])
def test_acceptable_softness_passes(sigma):
    assert v_of(synthetic_hand("light", blur=sigma)[0]).ok


@pytest.mark.parametrize("tone", ["light", "dark"])
def test_blurry_hand_rejected(tone):
    r = v_of(synthetic_hand(tone, blur=5)[0])
    assert not r.ok and any("blurry" in e for e in r.errors)


def test_overexposed_and_too_dark_hand_rejected():
    r = v_of(synthetic_hand("light", brightness=1.4)[0])
    assert any("overexposed" in e for e in r.errors), r.metrics
    r = v_of(synthetic_hand("dark", brightness=0.4)[0])
    assert any("too dark" in e for e in r.errors), r.metrics


def test_dark_skin_in_good_light_is_not_called_too_dark():
    r = v_of(synthetic_hand("dark")[0])
    assert r.ok and r.metrics["brightness"] < 90


def test_cut_off_hand_rejected():
    img, _ = synthetic_hand("medium")
    r = v_of(img[250:, 200:].copy())              # fingertips and thumb cropped away
    assert any("cut off" in e for e in r.errors), (r.errors, r.metrics)


def test_exif_rotation_is_honoured(tmp_path):
    from PIL import Image
    img, _ = synthetic_hand("medium")
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    exif = Image.Exif()
    exif[0x0112] = 6                               # "rotate 90 CW to display"
    p = tmp_path / "rot.jpg"
    pil.save(p, exif=exif, quality=95)
    r = validate_upload("rot.jpg", p.read_bytes(), "Left")
    assert r.image.shape[:2] == (img.shape[1], img.shape[0])      # width/height swapped
