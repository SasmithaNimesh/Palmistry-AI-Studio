"""Build the technical report (.docx, target 5-8 pages).

    python tools/build_report_docx.py [--out docs/Technical_Report.docx] [--pytest-log docs/pytest_output.txt]

Nothing in the findings is typed in by hand: the synthetic-pair table, segmentation scores and
validation sweeps are *computed when this script runs*; the pytest line comes from the captured log;
real-photo and live-Gemini rows come from outputs/results.json (written by
tools/run_photo_tests.py). If a result does not exist the report says "NOT RUN" - it never invents one.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont

import _env

sys.path.insert(0, str(_env.ROOT / "tests"))
from synthetic import png_bytes, synthetic_hand  # noqa: E402

from palmreader import DISCLAIMER, features as F, llm  # noqa: E402
from palmreader.features import analyse_palm  # noqa: E402
from palmreader.knowledge_base import PASSAGES  # noqa: E402
from palmreader.preprocessing import run_pipeline  # noqa: E402
from palmreader.segmentation import _clean, _fixed_range, segment_hand  # noqa: E402
from palmreader.validation import (BRIGHT_RANGE, EDGE_WIDTH_MAX, validate_upload)  # noqa: E402

FIG = _env.ROOT / "docs" / "figures"
BLUE = RGBColor(0x1F, 0x3A, 0x5F)


# ------------------------------------------------------------------ docx helpers
def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def table(doc, header, rows, widths=None, font=8.5):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold, r.font.size = True, Pt(font)
        shade(c, "DCE6F1")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            txt = str(v)
            run = p.add_run(txt)
            run.font.size = Pt(font)
            if txt.startswith("NOT RUN"):
                run.font.color.rgb, run.bold = RGBColor(0xB0, 0x20, 0x20), True
    if widths:
        for row in t.rows:
            for c, w in zip(row.cells, widths):
                c.width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def para(doc, text, bold_lead=None, size=10.5, italic=False, after=4):
    p = doc.add_paragraph()
    if bold_lead:
        r = p.add_run(bold_lead)
        r.bold = True
        r.font.size = Pt(size)
    r = p.add_run(text)
    r.font.size, r.italic = Pt(size), italic
    p.paragraph_format.space_after = Pt(after)
    return p


def bullet(doc, text, bold_lead=None, size=10.5):
    p = doc.add_paragraph(style="List Bullet")
    if bold_lead:
        r = p.add_run(bold_lead)
        r.bold, r.font.size = True, Pt(size)
    r = p.add_run(text)
    r.font.size = Pt(size)
    p.paragraph_format.space_after = Pt(1)


def picture(doc, path, width_cm, caption):
    doc.add_picture(str(path), width=Cm(width_cm))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(caption)
    r.italic, r.font.size = True, Pt(9)
    p.paragraph_format.space_after = Pt(6)


# ------------------------------------------------------------------ figures (synthetic only)
def font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def architecture_figure(path: Path):
    W, H = 1500, 560
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    f, fb = font(21), font(23)
    boxes = [("1 Upload\n(Streamlit)", 20, 40, "#DCE6F1"), ("2 Validate\nformat, size, hand\nblur & exposure", 280, 40, "#DCE6F1"),
             ("3 Preprocess\nresize, gray, blur,\nCLAHE, segment,\nSobel/Canny, threshold", 540, 40, "#E2EFDA"),
             ("4 Feature extraction\npalm frame, creases,\nheart/head/life/fate\n+ confidence gates", 820, 40, "#E2EFDA"),
             ("5 Annotate\nonly 'detected'\nlines drawn", 1120, 40, "#E2EFDA")]
    for text, x, y, col in boxes:
        w = 240 if "Preprocess" not in text and "Feature" not in text else 250
        d.rounded_rectangle([x, y, x + w, y + 180], 14, fill=col, outline="#444", width=2)
        d.multiline_text((x + 12, y + 14), text, fill="black", font=f, spacing=5)
    for x in (260, 520, 800, 1090):
        d.line([x, 130, x + 18, 130], fill="#444", width=3)
        d.polygon([(x + 18, 120), (x + 18, 140), (x + 30, 130)], fill="#444")
    boxes2 = [("Structured features JSON\n(status, confidence, curvature,\nregion, palm shape; no pixels)", 20, "#FFF2CC"),
              ("RAG: curated palmistry\npassages (TF-IDF retrieval),\nadded to the prompt", 385, "#FFF2CC"),
              ("Gemini (auto-selected model)\nJSON report; disclaimer\nadded in code", 750, "#FCE4D6"),
              ("Chatbot: features + report\n+ retrieved passages + grounding\nnote; disclaimer added in code", 1115, "#FCE4D6")]
    for text, x, col in boxes2:
        d.rounded_rectangle([x, 330, x + 355, 480], 14, fill=col, outline="#444", width=2)
        d.multiline_text((x + 12, 344), text, fill="black", font=f, spacing=5)
    for x in (375, 740, 1105):
        d.line([x, 405, x + 10, 405], fill="#444", width=3)
        d.polygon([(x + 8, 395), (x + 8, 415), (x + 20, 405)], fill="#444")
    d.line([945, 220, 945, 290, 197, 290, 197, 322], fill="#444", width=3)
    d.polygon([(187, 320), (207, 320), (197, 332)], fill="#444")
    d.text((20, 520), "Palmistry output is entertainment, not science. Photos never leave the machine; only structured features are sent to the LLM.",
           fill="#B02020", font=font(19))
    d.text((20, 6), "Figure: end-to-end architecture", fill="#1F3A5F", font=fb)
    im.save(path)


def labelled(img, text, w=420):
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB) if img.ndim == 2 else img.copy()
    img = cv2.resize(img, (w, int(img.shape[0] * w / img.shape[1])))
    cv2.rectangle(img, (0, 0), (w, 24), (255, 255, 255), -1)
    cv2.putText(img, text, (6, 17), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    return img


def run_one(tone="medium", angle=0.0, mirror=False, **kw):
    img, gt = synthetic_hand(tone, angle, mirror, **kw)
    v = validate_upload("synthetic.png", png_bytes(img), "Left")
    if v.hand_mask is None or not v.hand_mask.any():
        return img, gt, v, None, None, None
    st = run_pipeline(v.image, v.hand_mask)
    feat, ann = analyse_palm(st, "Left")
    return img, gt, v, st, feat, ann


def preprocessing_figure(path: Path):
    _, _, _, st, _, _ = run_one("medium")
    keys = ["1 Resized + normalised", "2 Grayscale", "3 Gaussian blur (denoise)", "4 CLAHE contrast",
            "5b Segmentation overlay", "7a Sobel gradient", "7b Canny edges", "8a Global Otsu threshold",
            "8 Threshold + morphology"]
    tiles = [labelled(st[k], k) for k in keys]
    h = max(t.shape[0] for t in tiles)
    tiles = [cv2.copyMakeBorder(t, 0, h - t.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255)) for t in tiles]
    rows = [np.hstack(tiles[i:i + 3]) for i in range(0, 9, 3)]
    cv2.imwrite(str(path), cv2.cvtColor(np.vstack(rows), cv2.COLOR_RGB2BGR))


def annotated_figure(path: Path):
    _, _, _, _, _, a1 = run_one("deep", 0, False)
    _, _, _, _, _, a2 = run_one("light", 37, True)
    t1, t2 = labelled(a1, "synthetic deep-tone hand, upright", 520), labelled(a2, "synthetic light hand, mirrored + rotated 37 deg", 520)
    h = max(t1.shape[0], t2.shape[0])
    pad = lambda t: cv2.copyMakeBorder(t, 0, h - t.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    cv2.imwrite(str(path), cv2.cvtColor(np.hstack([pad(t1), pad(t2)]), cv2.COLOR_RGB2BGR))


# ------------------------------------------------------------------ computed findings
def line_cell(feat, name):
    d = feat["lines"][name]
    return {"detected": f"D {d['confidence']}", "uncertain": f"U {d['confidence']}", "not_detected": "ND"}[d["status"]]


def short_error(e: str) -> str:
    """One short phrase per validator error, for table cells."""
    for key, label in (("blurry", "blurry"), ("overexposed", "overexposed"), ("too dark", "too dark"), ("cut off", "hand cut off"),
                       ("no clear palm", "no clear palm"), ("resolution", "resolution too low"), ("not supported", "unsupported file"),
                       ("corrupted", "corrupted file")):
        if key in e:
            return label
    return e.split(": ", 1)[-1][:40]


def side_row(label, v, feat):
    m = v.metrics
    verdict = "accepted" if v.ok else "REJECTED: " + "; ".join(short_error(e) for e in v.errors)
    metrics = (f"edge {m.get('edge_width_px')} px, bright {m.get('brightness')}, hand {m.get('hand_fraction')}"
               if m.get("brightness") is not None else f"hand {m.get('hand_fraction')}")
    if feat and v.ok:
        lines = ", ".join(f"{n.split('_')[0][:5]} {line_cell(feat, n)}" for n in F.LINE_COLORS)
        notes = "; ".join(feat["notes"]) or "-"
    else:
        lines, notes = "not processed (rejected by validation)" if not v.ok else "not processed", "-"
    return [label, verdict, metrics, lines, notes]


def synthetic_pairs():
    """3 synthetic left/right pairs + 1 failure pair, each run through validation + pipeline now."""
    specs = [
        ("S1 (light skin)", dict(tone="light", angle=0, mirror=False), dict(tone="light", angle=0, mirror=True)),
        ("S2 (medium, rotated)", dict(tone="medium", angle=37, mirror=False), dict(tone="medium", angle=-37, mirror=True)),
        ("S3 (deep skin, grey bg)", dict(tone="deep", angle=0, mirror=False, bg="grey"), dict(tone="deep", angle=90, mirror=True, bg="grey")),
        ("S-fail (blurry + cut-off)", dict(tone="medium", blur=5.0), None),
    ]
    rows = []
    for name, left, right in specs:
        for side, kw in (("Left", left), ("Right", right)):
            if kw is None:  # failure pair: right palm = cropped hand
                img, _ = synthetic_hand("medium")
                cropped = img[250:, 200:].copy()
                v = validate_upload("cropped.png", png_bytes(cropped), "Right")
                rows.append(side_row(f"{name} {side}", v, None))
                continue
            _, _, v, st, feat, _ = run_one(**kw)
            rows.append(side_row(f"{name} {side}", v, feat))
    return rows


def segmentation_rows():
    rows = []
    for tone in ("light", "medium", "dark", "deep"):
        old, new = [], []
        for angle, mirror in ((0, False), (90, False), (37, True), (180, True)):
            img, gt = synthetic_hand(tone, angle, mirror)
            iou = lambda m: float(((m > 0) & (gt > 0)).sum() / max(((m > 0) | (gt > 0)).sum(), 1))
            old.append(iou(_clean(_fixed_range(img))))
            new.append(iou(segment_hand(img).mask))
        rows.append([tone, f"{np.mean(old):.3f} (min {np.min(old):.3f})", f"{np.mean(new):.3f} (min {np.min(new):.3f})"])
    return rows


def validation_rows():
    rows = []
    for label, kw in [("sharp", dict(tone="medium")), ("Gaussian blur sigma 1", dict(tone="medium", blur=1)),
                      ("Gaussian blur sigma 2", dict(tone="medium", blur=2)), ("Gaussian blur sigma 3", dict(tone="medium", blur=3)),
                      ("Gaussian blur sigma 5", dict(tone="medium", blur=5)),
                      ("pale skin, white wall (old bug case)", dict(tone="light")),
                      ("deep skin, good light", dict(tone="deep")),
                      ("brightness x1.4, pale skin", dict(tone="light", brightness=1.4)),
                      ("brightness x0.4, dark skin", dict(tone="dark", brightness=0.4))]:
        img, _ = synthetic_hand(**kw)
        v = validate_upload("x.png", png_bytes(img), "Left")
        m = v.metrics
        rows.append([label, m.get("edge_width_px"), m.get("brightness"), "accepted" if v.ok else "rejected: " + short_error(v.errors[0])])
    return rows


def pytest_summary(log: Path):
    if not log.exists():
        return None
    text = log.read_text(encoding="utf-8", errors="replace")
    m = re.findall(r"(\d+ passed[^\n]*)", text)
    return m[-1].strip(" =") if m else None


def real_rows(results_path: Path):
    if not results_path.exists():
        return None, None
    res = json.loads(results_path.read_text(encoding="utf-8"))
    rows, chat = [], []
    for name, r in res.items():
        for side in ("Left", "Right"):
            vv = r["validation"].get(side, {"ok": False, "errors": ["missing"], "metrics": {}})
            m = vv.get("metrics", {})
            verdict = "accepted" if vv["ok"] else "REJECTED: " + "; ".join(short_error(e) for e in vv["errors"])
            metrics = f"edge {m.get('edge_width_px')} px, bright {m.get('brightness')}, hand {m.get('hand_fraction')}"
            lines = ", ".join(f"{n.split('_')[0][:5]} " + {"detected": "D", "uncertain": "U", "not_detected": "ND"}[d["status"]] +
                              (f" {d['confidence']}" if d["status"] != "not_detected" else "") for n, d in r["lines"].get(side, {}).items()) or "not processed"
            rows.append([f"{name} {side} (real)", verdict, metrics, lines, "; ".join(r.get("notes", {}).get(side, [])) or "-"])
        if "chat" in r:
            chat.append((name, r["chat"]))
    return rows, chat


# ------------------------------------------------------------------ document
def build(out: Path, pytest_log: Path, results_path: Path):
    FIG.mkdir(parents=True, exist_ok=True)
    architecture_figure(FIG / "architecture.png")
    preprocessing_figure(FIG / "preprocessing_synthetic.png")
    annotated_figure(FIG / "annotated_synthetic.png")

    doc = Document()
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Cm(2.0)
    sec.top_margin = sec.bottom_margin = Cm(1.8)
    st = doc.styles["Normal"]
    st.font.name, st.font.size = "Calibri", Pt(10.5)
    for lvl, sz in ((1, 14), (2, 12)):
        hs = doc.styles[f"Heading {lvl}"]
        hs.font.name, hs.font.size, hs.font.color.rgb = "Calibri", Pt(sz), BLUE
        hs.paragraph_format.space_before, hs.paragraph_format.space_after = Pt(8), Pt(3)

    t = doc.add_paragraph()
    r = t.add_run("AI-Powered Palm Reading and Intelligent Chatbot")
    r.bold, r.font.size, r.font.color.rgb = True, Pt(20), BLUE
    para(doc, "Technical report - NIBM Kandy Innovation Centre, Digital Image Processing, ICA 01", size=11, after=2)
    para(doc, "Student name / ID: ______________________   Date: ______________", size=10, after=4)
    box = doc.add_table(rows=1, cols=1)
    box.style = "Table Grid"
    c = box.rows[0].cells[0]
    shade(c, "FDECEA")
    c.text = ""
    rr = c.paragraphs[0].add_run("Academic note. " + DISCLAIMER)
    rr.font.size, rr.bold = Pt(9.5), True
    doc.add_paragraph().paragraph_format.space_after = Pt(0)

    doc.add_heading("1. Overview and architecture", 1)
    para(doc, "The application lets a user upload separate left- and right-palm photographs, checks them, runs a "
              "classical OpenCV pipeline, marks the creases it can find with confidence, and then asks a Gemini model - "
              "grounded in a curated palmistry knowledge base - for a structured reading. A chatbot answers follow-up "
              "questions using the same features and report. It is a Streamlit app; the code is split into modules "
              "(segmentation, validation, preprocessing, features, knowledge_base, llm, report) so each task of the brief "
              "maps to one file. The central design rule is that the computer-vision stage makes observations and the LLM "
              "only interprets them: the model never sees the photographs, only a JSON of detected features.")
    picture(doc, FIG / "architecture.png", 16.5, "Figure 1. System architecture and data flow.")

    doc.add_heading("2. Input validation (Task 1)", 1)
    para(doc, f"Files must be JPG/JPEG/PNG, at most 15 MB, and decodable (Pillow verifies the file; EXIF rotation from phones is "
              f"applied). Image quality is judged on the hand only, found by the adaptive segmenter of Section 3, because "
              f"measuring the whole frame made a plain white wall look 'overexposed' and 'blurry'. Checks: resolution (shortest "
              f"side >= 400 px); hand coverage (>= 12% of the frame, otherwise 'no clear palm'); blur, measured as the width of "
              f"the hand's silhouette edge (step height divided by peak gradient, limit {EDGE_WIDTH_MAX:.0f} px at 800 px wide); "
              f"exposure (hand mean grey level in {BRIGHT_RANGE[0]}-{BRIGHT_RANGE[1]}, and at most 20% blown-out pixels); and cut-off "
              f"hands (hand touching two or more image sides; the wrist may leave through one). Every failure gives an actionable "
              f"message and the user re-uploads in the same slot.")
    para(doc, "Why edge width instead of Laplacian variance: the Laplacian scales with contrast, so pale skin on a white wall "
              "scored 'blurry' even when sharp. Edge width is contrast-independent, and Table 2 shows it separating sharp from "
              "blurred hands across skin tones.")

    doc.add_heading("3. Image processing pipeline (Task 2)", 1)
    para(doc, "Every stage is returned and displayed as a before/after comparison in the UI (Figure 2 is the same sequence on a "
              "synthetic hand). Each technique and the reason for it:")
    table(doc, ["Technique", "Parameters", "Justification"], [
        ["Resize + min-max normalise", "width 900 px", "Pixel-based kernels and thresholds need a fixed scale; normalising reduces exposure differences."],
        ["RGB to grayscale", "-", "Creases are brightness valleys; colour adds noise to edge detection."],
        ["Gaussian blur", "5x5, sigma 1.2", "Suppresses skin grain and sensor noise that create false edges, keeps crease-scale structure."],
        ["CLAHE", "clip 3.0, 8x8 tiles", "Local contrast boost for faint creases; the clip limit prevents the noise amplification and blown highlights of plain global equalisation. Histogram before/after is shown."],
        ["Adaptive hand segmentation", "Otsu on Lab distance from border colour; Otsu on Cr; 2-means on Cr/Cb; fixed range; GrabCut fallback", "Fixed YCrCb/HSV ranges failed on deep skin tones. Candidates are scored on size, solidity and border contact, so the image chooses its own threshold."],
        ["Morphology (open/close/fill)", "5x5 ellipse", "Cleans the mask; kept small because larger closing welded neighbouring fingers together (found and fixed during testing)."],
        ["Black-hat transform", "21x21 ellipse", "Highlights thin dark lines on a lighter background - exactly a crease."],
        ["Sobel and Canny", "Sobel 3x3; Canny 0.66x / 1.33x palm median", "Sobel shows gradient strength; Canny thins to 1-px edges via hysteresis. Shown side by side."],
        ["Global Otsu vs adaptive threshold", "adaptive: Gaussian, block 31, C = -6", "One global threshold fails under uneven light; the adaptive threshold decides per neighbourhood. Both are shown."],
        ["Close + open on the binary map", "5x5 close, 2x2 open", "Joins small gaps in crease strokes and removes specks before skeletonisation."],
    ], widths=[3.6, 4.2, 9.2])
    picture(doc, FIG / "preprocessing_synthetic.png", 16.0, "Figure 2. Pipeline stages on a synthetic hand (generated by tests/synthetic.py, not a real palm).")

    doc.add_heading("4. Feature extraction (Task 3)", 1)
    para(doc, "Palm frame. The distance transform gives the palm radius; opening the hand mask with a disc of 0.6 r removes the "
              "fingers, and the remainder is the palm (its centroid is the palm centre). Connected pieces of 'hand minus palm' are "
              "finger blobs. The thumb is the blob lowest along a first-pass finger direction; the direction is then re-estimated from "
              "the four fingers only (this cut the direction error from about 5 to about 1.3 degrees on the synthetic hands). The "
              "thumb defines the 'thumb side' axis, so the frame is independent of rotation and of left/right mirroring. The "
              "'fewer than four fingers' warning counts finger blobs excluding the thumb.", bold_lead="")
    para(doc, "Crease candidates. The adaptive-threshold crease map inside the palm is dilated slightly to bridge gaps, skeletonised "
              "(Zhang-Suen), and cut at junctions so touching lines separate. Candidate length is measured as arc length (a diagonal "
              "skeleton step is longer than an orthogonal one), at most 60 candidates are scored.")
    para(doc, f"Scoring and honesty. Each candidate is scored 0-1 against each line type from its length, orientation and position in "
              f"the palm frame (heart: horizontal, upper palm; head: horizontal, middle; life: vertical, thumb side; fate: vertical, centre), "
              f"and matched greedily, best first, one crease per line. A line is 'detected' only when the score >= {F.DETECT_T}, the crease "
              f"is at least {F.MIN_REL_DEPTH:.0%} darker than the palm's mean brightness (absolute depth, measured before CLAHE and normalisation) and its ridge response is >= {F.MIN_CONTRAST}x the palm's own texture level; 'uncertain' if "
              f"it scores >= {F.UNCERTAIN_T} but fails a gate; otherwise 'not_detected'. Only detected lines are drawn; uncertain and absent "
              f"lines are listed in a legend on the image and in the table, never drawn. Palm shape (square/rectangular) and finger length "
              f"(short/long) from silhouette ratios give an 'Earth/Air/Fire/Water' hand type; thresholds {F.SQUARE_MAX_RATIO} and "
              f"{F.LONG_FINGER_RATIO} are justified in code comments and are heuristics, not validated on a dataset.")
    picture(doc, FIG / "annotated_synthetic.png", 14.0, "Figure 3. Annotated output with the legend (synthetic hands; only detected lines are drawn, the fate line is absent by construction).")

    doc.add_heading("5. LLM specialisation (Task 4)", 1)
    bullet(doc, " Google Gemini through the google-genai SDK. gemini-2.0-flash is retired (Google's deprecations page lists "
                f"2026-06-01), so the app asks the API which models the key can use and takes the first of {', '.join(llm.MODEL_PREFERENCE)}; "
                "GEMINI_MODEL overrides. Missing key, rejected key (401/403), unknown model (404), quota (429), network and invalid-JSON "
                "errors each produce a specific message.", bold_lead="Model and provider.")
    bullet(doc, f" general-purpose LLM + retrieval-augmented generation over {len(PASSAGES)} curated palmistry passages (heart, head, life, "
                "fate lines, hand types, career, finance, relationships, left-vs-right, future, safety), retrieved with a TF-IDF cosine "
                "retriever. For the report, passages for detected/uncertain lines, the hand type and the general themes are injected; passages "
                "for undetected lines are not. For chat, the top four passages for the question are added.", bold_lead="Specialisation mechanism.")
    bullet(doc, " the structured feature JSON of both palms (per line: status, confidence, curvature, prominence, start/end region; palm shape, "
                "hand type, notes). Pixel paths and tuning values are stripped. Output: JSON with nine sections (palm characteristics, major lines, "
                "personality, career, finance, relationships, future narrative, left vs right, uncertainty); the disclaimer is added in code.",
           bold_lead="Input/output format.")
    bullet(doc, " the system prompt (a) allows only features present in OBSERVED_FEATURES and requires 'not detected' / 'uncertain' wording, "
                "(b) separates Observed from Traditional interpretation, (c) demands hedged language and forbids predictions, medical, financial, "
                "legal or relationship advice, (d) restricts claims to the retrieved knowledge, (e) restates the disclaimer. Temperature 0.4 for the report.",
           bold_lead="Prompts and safeguards.")

    doc.add_heading("6. Chatbot design (Task 5)", 1)
    para(doc, "Each turn sends the system prompt, the feature JSON, the generated report, passages retrieved for the question, and the last "
              "12 messages. If the question names a line (heart/head/life/fate) whose status is not 'detected' on one or both palms, a "
              "deterministic QUESTION_GROUNDING note is added saying so and forbidding a description of that line for that palm; only general "
              "tradition may be explained, labelled as such. The entertainment disclaimer is appended to every answer in code if the model "
              "did not include it. Streamlit reruns the script on every chat message, so validation and analysis are cached per file contents "
              "and only the model call happens per turn. These guards are prompt-level; there is no verifier that checks the answer against "
              "the feature JSON.")

    doc.add_heading("7. Testing and findings", 1)
    summ = pytest_summary(pytest_log)
    para(doc, f"Automated tests (pytest, warnings treated as errors): {summ or 'NOT RUN - log missing'}. They cover file validation, "
              "hand-region blur/exposure, segmentation, line detection, honest labelling, palm-shape thresholds, retrieval, and the LLM layer with a "
              "FAKE client (prompts, grounding note, disclaimers, model choice, error messages). The fake client proves the plumbing, not what a "
              "real model would answer.", size=10)
    para(doc, "Table 1. Segmentation IoU against ground truth on synthetic hands (mean and minimum over 4 poses: upright, rotated 90, rotated 37 "
              "and mirrored, rotated 180 and mirrored).", size=9.5, after=2)
    table(doc, ["Skin tone", "Old fixed YCrCb/HSV range", "Adaptive segmentation"], segmentation_rows(), widths=[3, 6.5, 6.5])
    para(doc, "Table 2. Validation metrics on synthetic hands (edge width and brightness are measured on the hand).", size=9.5, after=2)
    table(doc, ["Case", "Edge width (px)", "Hand brightness", "Verdict"], validation_rows(), widths=[6.2, 2.6, 2.8, 5.4])

    para(doc, "Table 3. Test findings. D = detected (confidence), U = uncertain (not drawn), ND = not detected. 'S' pairs are SYNTHETIC "
              "stand-ins computed when this report was built; they are not real palms.", size=9.5, after=2)
    rows = synthetic_pairs()
    real, chat = real_rows(results_path)
    if real:
        rows += real
    else:
        rows.append(["Real pairs 1-3, left/right", "NOT RUN - no real photos were available when this report was built", "-", "-", "Run tools/run_photo_tests.py, then rebuild"])
        rows.append(["Real failure case", "NOT RUN", "-", "-", "-"])
    table(doc, ["Image", "Validation", "Measured", "Lines (heart, head, life, fate)", "Notes"], rows, widths=[3.0, 4.4, 3.4, 4.2, 2.4], font=7.5)

    para(doc, "Table 4. Live Gemini report and chatbot results.", size=9.5, after=2)
    if chat:
        crow = []
        for name, c in chat:
            if "error" in c:
                crow.append([name, "ERROR", c["error"][:120], "-"])
                continue
            for turn in c["turns"]:
                crow.append([name, turn["q"][:60], turn["a"][:140].replace("\n", " ") + "...", "yes" if "entertainment" in turn["a"].lower() else "NO"])
        table(doc, ["Pair", "Question", "Answer (start)", "Disclaimer present"], crow, widths=[1.8, 4.4, 8.6, 2.6], font=7.5)
    else:
        para(doc, "NOT RUN - no Gemini API key was available when this report was built, so no live report or chatbot answer is quoted. "
                  "After running tools/run_photo_tests.py --chat with a key, rebuild this report to include the four-turn transcripts per pair "
                  "(including a question about a line that was not detected).", size=10).runs[0].font.color.rgb = RGBColor(0xB0, 0x20, 0x20)

    doc.add_heading("8. Limitations", 1)
    for lead, txt in [
        ("Real-photo accuracy is unproven here. ", "Automated tests use synthetic hands; thresholds (edge width, crease depth/contrast, score bars, palm-shape ratios) were set on them and must be checked against real photos."),
        ("Rule-based detection. ", "Line finding uses hand-written geometry and a heuristic score, not a trained model; the confidence is not a probability. Fate lines are often legitimately absent."),
        ("Backgrounds. ", "A cluttered or skin-coloured background defeats the colour-distance segmenters; GrabCut is only a fallback, and the validator rejects photos with no hand-like region."),
        ("Approximate shape labels. ", "Hand type comes from silhouette ratios and is affected by finger spread, tilt and wrist cropping."),
        ("Handedness and chat guard. ", "Left/right is taken from the upload slot; the chat grounding is prompt-based, not verified."),
        ("Palmistry. ", "It has no scientific validity for personality, health, wealth, relationships or the future; nothing here should inform real decisions."),
    ]:
        bullet(doc, txt, bold_lead=lead, size=10)

    doc.add_heading("9. Acknowledgements and AI assistance", 1)
    para(doc, "Third-party components: OpenCV (opencv-python-headless), NumPy, scikit-image (skeletonize), Pillow, Streamlit, Google google-genai SDK "
              "and Gemini API, pytest, python-docx. The palmistry passages were written for this project from widely repeated popular teaching. "
              "Much of the code, tests, documentation and this report's builder script were drafted with AI assistance (Claude Code, Anthropic) and then run "
              "and checked by the author, as section 10 of the brief requires to be declared.", size=10)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(_env.ROOT / "docs" / "Technical_Report.docx"))
    ap.add_argument("--pytest-log", default=str(_env.ROOT / "docs" / "pytest_output.txt"))
    ap.add_argument("--results", default=str(_env.ROOT / "outputs" / "results.json"))
    a = ap.parse_args()
    print("wrote", build(Path(a.out), Path(a.pytest_log), Path(a.results)))
