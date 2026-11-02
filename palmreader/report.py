"""Plain-text/Markdown rendering of the reading (UI download, tests, tools)."""
from __future__ import annotations
from . import DISCLAIMER

TITLES = {"palm_characteristics": "Palm characteristics", "major_lines": "Major lines",
          "personality": "Personality themes", "career": "Career themes",
          "finance": "Financial themes", "relationships": "Relationships & emotions",
          "future_narrative": "Future narrative (non-scientific)",
          "left_vs_right": "Left vs right comparison", "uncertainty": "Uncertainty & limits"}


def line_rows(feat: dict) -> list[dict]:
    rows = []
    for n, d in feat["lines"].items():
        rows.append({"Line": n.replace("_", " ").title(), "Status": d["status"].replace("_", " "),
                     "Confidence": d["confidence"], "Curvature": d["curvature"] or "n/a",
                     "Prominence": d["prominence"] or "n/a", "Start": d["start_region"] or "n/a",
                     "End": d["end_region"] or "n/a"})
    return rows


def report_to_markdown(report: dict, feats: dict) -> str:
    out = ["# AI Palm Reading Report", "", f"> **{DISCLAIMER}**", "", "## Observed (computer vision)"]
    for side, f in feats.items():
        out += ["", f"### {side} palm"]
        if "palm" in f:
            p = f["palm"]
            out.append(f"Palm shape: {p['palm_shape']}, fingers: {p['finger_length']}, "
                       f"hand type: {p['palmistry_hand_type']} ({p['note']}).")
        out += ["", "| Line | Status | Confidence | Curvature | Prominence |", "|---|---|---|---|---|"]
        out += [f"| {r['Line']} | {r['Status']} | {r['Confidence']} | {r['Curvature']} | {r['Prominence']} |"
                for r in line_rows(f)]
        out += [f"- Note: {n}" for n in f["notes"]]
    out += ["", "## Interpretation (LLM + palmistry knowledge base)"]
    for k, t in TITLES.items():
        out += ["", f"### {t}", report.get(k, "")]
    out += ["", "---", f"**{report.get('disclaimer', DISCLAIMER)}**"]
    return "\n".join(out)
