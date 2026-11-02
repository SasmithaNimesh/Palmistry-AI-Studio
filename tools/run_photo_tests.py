"""Run the full flow on your real, consented palm photos and save evidence.

Put photos in ./photos named  <pair>_left.jpg / <pair>_right.jpg  (png/jpeg also fine), e.g.
    photos/pair1_left.jpg  photos/pair1_right.jpg
    photos/pair2_left.jpg  photos/pair2_right.jpg
    photos/pair3_left.jpg  photos/pair3_right.jpg
    photos/bad_left.jpg    photos/bad_right.jpg      <- a deliberately blurry / dark / cropped pair

    python tools/run_photo_tests.py                 # validation + processing + annotation only
    python tools/run_photo_tests.py --chat          # also report + 4 chatbot turns (needs GEMINI_API_KEY)

Everything is written to ./outputs (git-ignored): annotated images, before/after strips, features
JSON, report, chat transcript and results.json (read by tools/build_report_docx.py). Nothing is
uploaded except, with --chat, the structured feature JSON (never the images) sent to Gemini.
"""
import argparse
import json
import re
from pathlib import Path

import cv2
import numpy as np

import _env
_env.load_dotenv()

from palmreader.features import analyse_palm  # noqa: E402
from palmreader.knowledge_base import Retriever  # noqa: E402
from palmreader.llm import PalmChatbot, friendly_error, generate_report  # noqa: E402
from palmreader.preprocessing import COMPARISONS, run_pipeline  # noqa: E402
from palmreader.report import report_to_markdown  # noqa: E402
from palmreader.validation import validate_upload  # noqa: E402

QUESTIONS = ["What does my heart line traditionally represent?",
             "What differences are visible between my left and right palms?",
             "What does palmistry say about my career?"]
TUNING_KEYS = ("status", "confidence", "curvature", "prominence", "ridge_contrast", "crease_depth")


def find_pairs(folder: Path) -> dict[str, dict[str, Path]]:
    pairs: dict[str, dict[str, Path]] = {}
    for p in sorted(folder.iterdir()):
        m = re.match(r"(.+)_(left|right)\.(jpg|jpeg|png)$", p.name, re.I)
        if m:
            pairs.setdefault(m.group(1), {})[m.group(2).capitalize()] = p
    return pairs


def strip_image(stages: dict, keys: list[str], height: int = 360) -> np.ndarray:
    tiles = []
    for k in keys:
        im = stages[k]
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB) if im.ndim == 2 else im.copy()
        im = cv2.resize(im, (int(im.shape[1] * height / im.shape[0]), height))
        cv2.putText(im, k.split(" ", 1)[1][:34], (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 0), 2)
        tiles.append(im)
    return np.hstack(tiles)


def chat_questions(feats: dict) -> tuple[list[str], str | None]:
    """The 3 standard questions + one about a line that was NOT reliably detected (if any)."""
    missing = next((n for n in ("fate_line", "life_line", "head_line", "heart_line")
                    if any(f["lines"][n]["status"] != "detected" for f in feats.values())), None)
    last = (f"Tell me about my {missing.replace('_', ' ')}." if missing
            else "Can you explain my life line in more detail?")
    return QUESTIONS + [last], missing


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--photos", default=str(_env.ROOT / "photos"))
    ap.add_argument("--out", default=str(_env.ROOT / "outputs"))
    ap.add_argument("--chat", action="store_true", help="also generate the report and run chatbot turns")
    args = ap.parse_args()
    photos, out = Path(args.photos), Path(args.out)
    if not photos.exists():
        print(f"No photos folder at {photos}. Create it and add <pair>_left.jpg / <pair>_right.jpg files.")
        return 1
    pairs = find_pairs(photos)
    if not pairs:
        print(f"No files named <pair>_left.jpg / <pair>_right.jpg found in {photos}.")
        return 1
    out.mkdir(exist_ok=True)
    results = {}
    for name, sides in pairs.items():
        print(f"\n=== {name} ===")
        res = {"validation": {}, "lines": {}, "palm": {}, "processed": False}
        accepted = {}
        for side in ("Left", "Right"):
            if side not in sides:
                res["validation"][side] = {"ok": False, "errors": [f"{side} file missing"], "warnings": [], "metrics": {}}
                continue
            v = validate_upload(sides[side].name, sides[side].read_bytes(), side)
            res["validation"][side] = {"ok": v.ok, "errors": v.errors, "warnings": v.warnings, "metrics": v.metrics}
            print(f"{side}: {'OK' if v.ok else 'REJECTED'}", v.metrics, *v.errors, *v.warnings, sep="\n   ")
            if v.ok:
                accepted[side] = v
        if len(accepted) == 2:
            feats = {}
            for side, v in accepted.items():
                stages = run_pipeline(v.image, v.hand_mask)
                feats[side], ann = analyse_palm(stages, side)
                tag = f"{name}_{side.lower()}"
                cv2.imwrite(str(out / f"{tag}_annotated.png"), cv2.cvtColor(ann, cv2.COLOR_RGB2BGR))
                for i, comp in enumerate(COMPARISONS):
                    cv2.imwrite(str(out / f"{tag}_cmp{i + 1}.png"),
                                cv2.cvtColor(strip_image(stages, comp["panels"]), cv2.COLOR_RGB2BGR))
                res["lines"][side] = {n: {k: d[k] for k in TUNING_KEYS} for n, d in feats[side]["lines"].items()}
                res["palm"][side] = feats[side].get("palm")
                res.setdefault("notes", {})[side] = feats[side]["notes"]
                print(f"{side} lines:", {n: (d["status"], d["confidence"], d["ridge_contrast"], d["crease_depth"])
                                         for n, d in feats[side]["lines"].items()}, feats[side]["notes"])
            res["processed"] = True
            slim = {s: {**f, "lines": {n: {k: v for k, v in d.items() if k != "path"} for n, d in f["lines"].items()}}
                    for s, f in feats.items()}
            (out / f"{name}_features.json").write_text(json.dumps(slim, indent=1), encoding="utf-8")
            if args.chat:
                try:
                    report, _ = generate_report(feats, Retriever())
                    (out / f"{name}_report.md").write_text(report_to_markdown(report, feats), encoding="utf-8")
                    bot = PalmChatbot(feats, report, Retriever())
                    qs, missing = chat_questions(feats)
                    transcript = []
                    for q in qs:
                        a = bot.ask(q)
                        transcript.append({"q": q, "a": a})
                        print(f"\nQ: {q}\nA: {a}")
                    res["chat"] = {"asked_about_not_detected": missing, "turns": transcript}
                    (out / f"{name}_chat.json").write_text(json.dumps(transcript, indent=1), encoding="utf-8")
                except Exception as e:  # noqa: BLE001
                    res["chat"] = {"error": str(friendly_error(e))}
                    print("LLM step failed:", friendly_error(e))
        results[name] = res
    (out / "results.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(f"\nSaved evidence to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
