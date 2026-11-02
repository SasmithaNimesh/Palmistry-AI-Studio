"""Task 04 + 05: Gemini-backed report generation and grounded chatbot.

Specialisation mechanism: general-purpose LLM (Gemini) + curated palmistry knowledge
base retrieved per request (RAG) + strict system prompt. Input is the structured
feature JSON from the OpenCV stage (path pixels are stripped); output is a fixed
JSON schema so the UI can render sections reliably.
"""
from __future__ import annotations
import copy
import json
import os
import re
from . import DISCLAIMER, DISCLAIMER_MARK, DISCLAIMER_SHORT
from .knowledge_base import Retriever

# gemini-2.0-flash was shut down (Google's deprecations page lists 2026-06-01).
# Model choice: GEMINI_MODEL if set, otherwise the first of these that the key can use
# (checked against client.models.list()). Order = newest fast model first.
MODEL_PREFERENCE = ["gemini-3.6-flash", "gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"]
DEFAULT_MODEL = MODEL_PREFERENCE[0]
_resolved: dict[str, str] = {}   # api key -> model id (avoids a list call on every chat turn)

LINE_NAMES = ["heart_line", "head_line", "life_line", "fate_line"]
SECTIONS = ["palm_characteristics", "major_lines", "personality", "career", "finance",
            "relationships", "future_narrative", "left_vs_right", "uncertainty"]


class LLMError(RuntimeError):
    """Raised with a message that is safe and useful to show to the end user."""


SYSTEM_PROMPT = f"""You are a palmistry-style interpreter inside a university image-processing project.
RULES (never break them):
1. You may only describe palm features that appear in OBSERVED_FEATURES. If a line has status
   "not_detected" say it was not detected; if "uncertain" say it is uncertain. Never invent lines,
   marks, mounts, or colours that are not listed.
2. Keep two layers separate: "Observed" (from the computer-vision data) and "Traditional
   interpretation" (from KNOWLEDGE, phrased as 'palmistry tradition says...').
3. Use hedged language (tends to, traditionally read as). No certainty, no predictions of events,
   no medical, financial, legal or relationship advice, no statements about lifespan or illness.
4. Base interpretations only on KNOWLEDGE passages given to you; do not add outside claims.
5. Always remain consistent with this disclaimer: {DISCLAIMER}
"""

REPORT_INSTRUCTIONS = """Write the reading as JSON with exactly these string keys:
palm_characteristics, major_lines, personality, career, finance, relationships,
future_narrative, left_vs_right, uncertainty.
Each value: 2-5 sentences of Markdown. In major_lines, cover heart, head, life and fate lines for
BOTH palms, labelling each as Observed vs Traditional. future_narrative must say it is symbolic,
non-scientific storytelling. left_vs_right compares the two hands using only the data given.
uncertainty must list every uncertain / not_detected feature and image-quality caveats.
Return only JSON, no code fences."""


def strip_paths(features: dict) -> dict:
    """Copy of the feature dict without pixel paths / tuning values (the LLM never needs them)."""
    f = copy.deepcopy(features)
    for side in f.values():
        for d in side.get("lines", {}).values():
            d.pop("path", None)
            d.pop("ridge_contrast", None)
    return f


# ---------------------------------------------------------------- client / model / errors
def _api_key() -> str | None:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def _model_setting() -> str | None:
    return os.environ.get("GEMINI_MODEL") or None


def _client():
    key = _api_key()
    if not key:
        raise LLMError("No Gemini API key found. Set GEMINI_API_KEY (environment variable or .env file; "
                       "see README) and restart the app. A free key is available at "
                       "https://aistudio.google.com/apikey.")
    from google import genai
    return genai.Client(api_key=key)


def friendly_error(exc: Exception, model: str | None = None) -> LLMError:
    """Translate SDK / network exceptions into one clear, actionable message."""
    if isinstance(exc, LLMError):
        return exc
    code = getattr(exc, "code", None)
    text = str(exc)
    low = text.lower()
    if isinstance(exc, json.JSONDecodeError):
        return LLMError("The model did not return valid JSON for the report. Click 'Generate reading' to retry.")
    if code in (401, 403) or "api key not valid" in low or "api_key_invalid" in low or "permission_denied" in low:
        return LLMError("Gemini rejected the API key (invalid, expired or not allowed for this model). "
                        "Check GEMINI_API_KEY in your .env file.")
    if code == 429 or "resource_exhausted" in low or "quota" in low:
        return LLMError("Gemini quota or rate limit reached. Wait a minute and retry, set GEMINI_MODEL to a "
                        "lighter model (e.g. gemini-3.5-flash-lite), or check your quota in Google AI Studio.")
    if code == 404 or "not found" in low or "is not supported" in low:
        return LLMError(f"Gemini model '{model or _model_setting() or DEFAULT_MODEL}' is not available for your "
                        "key (it may have been retired). Unset GEMINI_MODEL to let the app pick a working one, "
                        "or run `python tools/check_gemini.py` to list the models your key can use.")
    if isinstance(exc, (ConnectionError, TimeoutError)) or "connect" in low or "timed out" in low:
        return LLMError("Could not reach the Gemini API. Check your internet connection and try again.")
    return LLMError(f"Gemini request failed ({type(exc).__name__}): {text[:300]}")


def resolve_model(client=None) -> str:
    """GEMINI_MODEL if set, else the first MODEL_PREFERENCE entry this key can generate with."""
    explicit = _model_setting()
    if explicit:
        return explicit
    key = _api_key() or ""
    if key in _resolved:
        return _resolved[key]
    client = client or _client()
    try:
        avail = {m.name.split("/")[-1] for m in client.models.list()
                 if "generateContent" in (getattr(m, "supported_actions", None) or ["generateContent"])}
    except Exception as e:  # noqa: BLE001 - mapped to a friendly message
        raise friendly_error(e) from e
    for cand in MODEL_PREFERENCE:
        if cand in avail:
            _resolved[key] = cand
            return cand
    raise LLMError("None of the expected Gemini models (" + ", ".join(MODEL_PREFERENCE) + ") is available "
                   "for your key. Set GEMINI_MODEL to a model listed by `python tools/check_gemini.py`.")


def _generate(client, contents, config):
    model = resolve_model(client)
    try:
        return client.models.generate_content(model=model, contents=contents, config=config)
    except Exception as e:  # noqa: BLE001 - mapped to a friendly message
        raise friendly_error(e, model) from e


def with_disclaimer(text: str) -> str:
    """Append the entertainment disclaimer unless already present (enforced in code, not left to the model)."""
    return text if DISCLAIMER_MARK in text.lower() else f"{text.rstrip()}\n\n_{DISCLAIMER_SHORT}_"


def _parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    return json.loads(text)


# ---------------------------------------------------------------- report
def generate_report(features: dict, retriever: Retriever, client=None) -> tuple[dict, list[dict]]:
    """Return (report sections dict, retrieved passages used)."""
    client = client or _client()
    clean = strip_paths(features)
    passages = retriever.for_features(clean)
    prompt = (
        f"OBSERVED_FEATURES (from OpenCV, JSON):\n{json.dumps(clean, indent=1)}\n\n"
        "KNOWLEDGE (curated palmistry passages):\n"
        + "\n".join(f"[{p['id']}] {p['text']}" for p in passages)
        + f"\n\n{REPORT_INSTRUCTIONS}"
    )
    from google.genai import types
    resp = _generate(client, prompt, types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT, temperature=0.4, response_mime_type="application/json"))
    try:
        report = _parse_json(resp.text or "")
    except json.JSONDecodeError as e:
        raise friendly_error(e) from e
    for s in SECTIONS:
        report.setdefault(s, "_Not provided._")
    report["disclaimer"] = DISCLAIMER       # added in code: always present, never model-written
    return report, passages


# ---------------------------------------------------------------- chatbot
class PalmChatbot:
    """Multi-turn chatbot grounded in features + report + per-question retrieval."""

    def __init__(self, features: dict, report: dict, retriever: Retriever, client=None):
        self.features = strip_paths(features)
        self.report = report
        self.retriever = retriever
        self.client = client
        self.history: list[dict] = []   # {"role": "user"|"model", "text": str}

    def _grounding(self, question: str) -> str:
        """Deterministic facts about any line the question names, so the model cannot guess."""
        q = question.lower().replace("-", " ")
        notes = []
        for name in LINE_NAMES:
            word = name.split("_")[0]
            if f"{word} line" in q or f"{word}line" in q:
                per = {side: d["lines"][name]["status"] for side, d in self.features.items()}
                missing = [side for side, st in per.items() if st != "detected"]
                if missing:
                    notes.append(
                        f"QUESTION_GROUNDING: the user asks about the {word} line. Its status is "
                        + ", ".join(f"{side}: {st.replace('_', ' ')}" for side, st in per.items())
                        + f". For the {' and '.join(missing)} palm you must say plainly that it was not "
                        "reliably detected by the image analysis and must NOT describe its shape, length, "
                        "depth or meaning for that palm. You may only explain what palmistry tradition says "
                        "about that line in general, clearly labelled as general tradition.")
        return "\n".join(notes)

    def _context(self, question: str) -> str:
        hits = self.retriever.search(question, k=4)
        kb = "\n".join(f"[{p['id']}] {p['text']}" for p in hits) or "(no matching passages)"
        return (f"OBSERVED_FEATURES:\n{json.dumps(self.features)}\n\n"
                f"GENERATED_REPORT:\n{json.dumps(self.report)}\n\nKNOWLEDGE:\n{kb}\n\n"
                f"{self._grounding(question)}")

    def ask(self, question: str) -> str:
        from google.genai import types
        self.client = self.client or _client()
        sys_prompt = (SYSTEM_PROMPT + "\nYou are now answering follow-up questions. Answer concisely and "
                      "clearly. If asked about something not in OBSERVED_FEATURES, say it was not "
                      "observed instead of guessing. Follow any QUESTION_GROUNDING note exactly.\n\n"
                      + self._context(question))
        contents = [types.Content(role=m["role"], parts=[types.Part(text=m["text"])]) for m in self.history[-12:]]
        contents.append(types.Content(role="user", parts=[types.Part(text=question)]))
        resp = _generate(self.client, contents,
                         types.GenerateContentConfig(system_instruction=sys_prompt, temperature=0.5))
        answer = with_disclaimer((resp.text or "").strip() or "I could not produce an answer; please rephrase.")
        self.history += [{"role": "user", "text": question}, {"role": "model", "text": answer}]
        return answer
