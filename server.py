"""FastAPI backend exposing the complete palmreader computer vision & Gemini RAG engine."""
from __future__ import annotations
import base64
import copy
import io
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
from pydantic import BaseModel

def _load_dotenv() -> None:
    p = Path(__file__).parent / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))

_load_dotenv()

from palmreader import DISCLAIMER, DISCLAIMER_SHORT
from palmreader.features import LINE_COLORS, analyse_palm
from palmreader.knowledge_base import Retriever
from palmreader.llm import (
    DEFAULT_MODEL,
    MODEL_PREFERENCE,
    PalmChatbot,
    _client,
    friendly_error,
    generate_report,
    resolve_model,
)
from palmreader.preprocessing import COMPARISONS, run_pipeline
from palmreader.report import TITLES, line_rows, report_to_markdown
from palmreader.validation import validate_upload

app = FastAPI(title="Palmistry AI Engine API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_retriever = Retriever()


def _mat_to_base64(img: np.ndarray, format: str = ".jpg") -> str:
    """Encode OpenCV BGR or RGB array to base64 Data URL."""
    if img is None or img.size == 0:
        return ""
    if img.ndim == 2:
        success, buf = cv2.imencode(format, img)
    else:
        # cv2.imencode expects BGR
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) if img.shape[2] == 3 else img
        success, buf = cv2.imencode(format, bgr)
    if not success:
        return ""
    b64 = base64.b64encode(buf.tobytes()).decode("utf-8")
    mime = "image/jpeg" if format in (".jpg", ".jpeg") else "image/png"
    return f"data:{mime};base64,{b64}"


@app.get("/api/status")
def get_status():
    has_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    active_model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
    if has_key:
        try:
            client = _client()
            active_model = resolve_model(client)
        except Exception:
            pass
    return {
        "has_key": has_key,
        "model": active_model,
        "preferred_models": MODEL_PREFERENCE,
        "privacy": "In-Memory RAM Shield (Images never stored or sent to Google)",
        "disclaimer": DISCLAIMER,
    }


@app.get("/api/sample/{pair_name}")
def get_sample(pair_name: str):
    base_path = Path("photos")
    left_path = base_path / f"{pair_name}_left.jpg"
    right_path = base_path / f"{pair_name}_right.jpg"
    
    if not left_path.exists() or not right_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample pair '{pair_name}' not found")
        
    left_bytes = left_path.read_bytes()
    right_bytes = right_path.read_bytes()
    
    v_left = validate_upload(left_path.name, left_bytes, "Left")
    v_right = validate_upload(right_path.name, right_bytes, "Right")
    
    return {
        "pair": pair_name,
        "left": {
            "name": left_path.name,
            "b64": _mat_to_base64(cv2.cvtColor(v_left.image, cv2.COLOR_BGR2RGB)) if v_left.image is not None else "",
            "raw_b64": base64.b64encode(left_bytes).decode("utf-8"),
            "ok": v_left.ok,
            "metrics": v_left.metrics,
            "errors": v_left.errors,
            "warnings": v_left.warnings,
        },
        "right": {
            "name": right_path.name,
            "b64": _mat_to_base64(cv2.cvtColor(v_right.image, cv2.COLOR_BGR2RGB)) if v_right.image is not None else "",
            "raw_b64": base64.b64encode(right_bytes).decode("utf-8"),
            "ok": v_right.ok,
            "metrics": v_right.metrics,
            "errors": v_right.errors,
            "warnings": v_right.warnings,
        }
    }


@app.post("/api/validate")
async def validate_image(side: str = Form(...), file: UploadFile = File(...)):
    content = await file.read()
    v = validate_upload(file.filename or "uploaded.jpg", content, side)
    
    b64 = ""
    if v.image is not None:
        rgb = cv2.cvtColor(v.image, cv2.COLOR_BGR2RGB)
        b64 = _mat_to_base64(rgb)
        
    return {
        "side": side,
        "name": file.filename,
        "ok": v.ok,
        "metrics": v.metrics,
        "errors": v.errors,
        "warnings": v.warnings,
        "preview_url": b64,
        "raw_b64": base64.b64encode(content).decode("utf-8")
    }


class AnalysisPayload(BaseModel):
    left_name: str
    left_b64: str
    right_name: str
    right_b64: str


@app.post("/api/analyze")
def analyze_palms(payload: AnalysisPayload):
    try:
        left_bytes = base64.b64decode(payload.left_b64)
        right_bytes = base64.b64decode(payload.right_b64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Base64 decode failed: {e}")
        
    v_left = validate_upload(payload.left_name, left_bytes, "Left")
    v_right = validate_upload(payload.right_name, right_bytes, "Right")
    
    if not v_left.ok or not v_right.ok:
        raise HTTPException(
            status_code=400,
            detail=f"Validation failed: Left errors={v_left.errors}, Right errors={v_right.errors}"
        )
        
    stages_left = run_pipeline(v_left.image, v_left.hand_mask)
    feats_left, ann_left = analyse_palm(stages_left, "Left")
    
    stages_right = run_pipeline(v_right.image, v_right.hand_mask)
    feats_right, ann_right = analyse_palm(stages_right, "Right")
    
    # Process stage previews into base64
    def serialize_stages(stages):
        res = {}
        for k, img in stages.items():
            if not k.startswith("_"):
                res[k] = _mat_to_base64(img)
        return res
        
    return {
        "stages": {
            "Left": serialize_stages(stages_left),
            "Right": serialize_stages(stages_right)
        },
        "annotated": {
            "Left": _mat_to_base64(ann_left),
            "Right": _mat_to_base64(ann_right)
        },
        "features": {
            "Left": feats_left,
            "Right": feats_right
        },
        "metrics": {
            "Left": v_left.metrics,
            "Right": v_right.metrics
        },
        "comparisons": COMPARISONS
    }


class ReadingRequest(BaseModel):
    features: Dict[str, Any]
    language: str = "en"  # en, si, ta


_cached_readings: Dict[str, Dict[str, Any]] = {}


@app.post("/api/generate-reading")
def generate_reading(req: ReadingRequest):
    lang = req.language.lower()
    feats = req.features
    
    # Check if we have an English reading generated first
    en_key = json.dumps(feats, sort_keys=True)
    if en_key not in _cached_readings:
        try:
            report_en, passages = generate_report(feats, _retriever)
            _cached_readings[en_key] = {
                "en": report_en,
                "passages": passages
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=friendly_error(e).args[0])
            
    cached = _cached_readings[en_key]
    report_en = cached["en"]
    passages = cached["passages"]
    
    if lang == "en":
        return {
            "language": "en",
            "report": report_en,
            "passages": passages,
            "titles": TITLES,
            "disclaimer": report_en.get("disclaimer", DISCLAIMER)
        }
        
    # If Sinhala or Tamil requested, check if already translated
    if lang in cached:
        return {
            "language": lang,
            "report": cached[lang],
            "passages": passages,
            "titles": TITLES,
            "disclaimer": cached[lang].get("disclaimer", DISCLAIMER)
        }
        
    # Translate report sections via Gemini
    try:
        client = _client()
        model = resolve_model(client)
        
        target_lang_name = "natural, fluent Sinhala (සිංහල)" if lang == "si" else "natural, fluent Tamil (தமிழ்)"
        prompt = f"""You are a professional literary translator. 
Translate the following palmistry reading report JSON values into {target_lang_name}.
RULES:
1. Retain the EXACT same JSON keys: palm_characteristics, major_lines, personality, career, finance, relationships, future_narrative, left_vs_right, uncertainty, disclaimer.
2. Translate all Markdown text values accurately and elegantly into proper {target_lang_name} script.
3. Return ONLY valid JSON, with no code fences or commentary.

JSON TO TRANSLATE:
{json.dumps(report_en, ensure_ascii=False)}
"""
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("\n", 1)[0]
        translated_report = json.loads(text)
        cached[lang] = translated_report
        
        return {
            "language": lang,
            "report": translated_report,
            "passages": passages,
            "titles": TITLES,
            "disclaimer": translated_report.get("disclaimer", DISCLAIMER)
        }
    except Exception as e:
        # Fallback to English if translation fails
        return {
            "language": "en",
            "report": report_en,
            "passages": passages,
            "titles": TITLES,
            "disclaimer": report_en.get("disclaimer", DISCLAIMER),
            "translation_error": str(e)
        }


class ChatRequest(BaseModel):
    query: str
    features: Dict[str, Any]
    report: Dict[str, Any]
    language: str = "en"
    history: List[Dict[str, str]] = []


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    bot = PalmChatbot(req.features, req.report, _retriever)
    
    # Load history into bot
    for m in req.history[-10:]:
        bot.history.append({"role": m["role"], "text": m["text"]})
        
    try:
        reply = bot.ask(req.query)
        
        # If user asked in Sinhala or Tamil or requested that language, translate response
        if req.language in ("si", "ta"):
            client = _client()
            model = resolve_model(client)
            lang_label = "Sinhala (සිංහල)" if req.language == "si" else "Tamil (தமிழ்)"
            t_prompt = f"Translate this palmistry chatbot response into natural {lang_label}. Preserve markdown formatting and the closing disclaimer:\n\n{reply}"
            r = client.models.generate_content(model=model, contents=t_prompt)
            reply = r.text.strip()
            
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=friendly_error(e).args[0])


@app.post("/api/export-markdown")
def export_markdown(req: ReadingRequest):
    feats = req.features
    report = req.report
    md = report_to_markdown(report, feats)
    return {"markdown": md}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
