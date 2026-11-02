"""Streamlit front-end: upload -> validate -> process -> annotate -> report -> chatbot.
Redesigned with a luxury dark glassmorphic design system and high-interactivity CV studio.
"""
from __future__ import annotations
import os
from pathlib import Path

import cv2
import streamlit as st

from palmreader import DISCLAIMER
from palmreader.features import LINE_COLORS, analyse_palm
from palmreader.knowledge_base import Retriever
from palmreader.llm import MODEL_PREFERENCE, PalmChatbot, friendly_error, generate_report
from palmreader.preprocessing import COMPARISONS, run_pipeline
from palmreader.report import TITLES, line_rows, report_to_markdown
from palmreader.styles import MASTER_CSS
from palmreader.ui_components import (
    render_feature_card,
    render_hand_type_card,
    render_hero,
    render_quality_diagnostics,
    render_stepper,
)
from palmreader.validation import validate_upload


def _load_dotenv() -> None:
    p = Path(__file__).parent / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))


_load_dotenv()

st.set_page_config(
    page_title="AI-Powered Palm Reading & Analysis",
    page_icon="🖐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Master Luxury Design System
st.markdown(MASTER_CSS, unsafe_allow_html=True)


@st.cache_resource
def get_retriever() -> Retriever:
    return Retriever()


@st.cache_data(show_spinner=False, max_entries=8)
def cached_validation(name: str, data: bytes, side: str):
    return validate_upload(name, data, side)


@st.cache_data(show_spinner=False, max_entries=4)
def cached_analysis(name: str, data: bytes, side: str):
    v = cached_validation(name, data, side)
    stages = run_pipeline(v.image, v.hand_mask)
    feats, ann = analyse_palm(stages, side)
    return stages, feats, ann


def show_comparisons(stages: dict) -> None:
    for comp in COMPARISONS:
        st.markdown(f"**{comp['title']}**")
        cols = st.columns(len(comp["panels"]))
        for i, (col, key) in enumerate(zip(cols, comp["panels"])):
            tag = "Before: " if i == 0 else "After: "
            col.image(stages[key], caption=tag + key.split(" ", 1)[1], width="stretch", clamp=True)
        st.caption(comp["why"])
        st.divider()


# Top Brand Identity & Disclaimer
st.title("🖐 AI-Powered Palm Reading & Chatbot")
st.warning(DISCLAIMER)

# Executive Hero Banner
render_hero()

# Sidebar Navigation & Setup
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <div style="background: rgba(139, 92, 246, 0.2); border: 1px solid #8B5CF6; border-radius: 10px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">
            🖐
        </div>
        <div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.05rem; color: #F8FAFC;">AI PALM PRO</div>
            <div style="font-size: 0.72rem; color: #22D3EE; letter-spacing: 0.05em; font-weight: 600;">CV + GEMINI ENGINE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.header("Setup")
    has_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    st.write("Gemini API key:", "✅ found" if has_key else "❌ missing (set GEMINI_API_KEY in .env)")
    st.write("Model:", os.environ.get("GEMINI_MODEL") or f"auto ({MODEL_PREFERENCE[0]} or next available)")
    st.caption("Images are processed in memory only and are never written to disk.")

    st.markdown("---")
    st.markdown("**⚡ Quick Demo Palms**")
    st.caption("Test the complete pipeline instantly with curated sample photos:")
    
    col_demo1, col_demo2 = st.columns(2)
    with col_demo1:
        if st.button("Sample Pair 1", help="Load pair 1 photos"):
            p_left = Path("photos/pair1_left.jpg")
            p_right = Path("photos/pair1_right.jpg")
            if p_left.exists() and p_right.exists():
                st.session_state["sample_files"] = {
                    "Left": ("pair1_left.jpg", p_left.read_bytes()),
                    "Right": ("pair1_right.jpg", p_right.read_bytes())
                }
                st.rerun()
    with col_demo2:
        if st.button("Sample Pair 2", help="Load pair 2 photos (deep tone)"):
            p_left = Path("photos/pair2_left.jpg")
            p_right = Path("photos/pair2_right.jpg")
            if p_left.exists() and p_right.exists():
                st.session_state["sample_files"] = {
                    "Left": ("pair2_left.jpg", p_left.read_bytes()),
                    "Right": ("pair2_right.jpg", p_right.read_bytes())
                }
                st.rerun()

    if "sample_files" in st.session_state:
        if st.button("Clear loaded sample", type="secondary"):
            del st.session_state["sample_files"]
            st.rerun()

    st.markdown("---")
    if st.button("Reset session", type="secondary"):
        st.session_state.clear()
        st.cache_data.clear()
        st.rerun()

# Determine active step for the Stepper
current_step = 1
if "feats" in st.session_state:
    current_step = 3
if st.session_state.get("report") is not None:
    current_step = 4
if len(st.session_state.get("chat", [])) > 0:
    current_step = 5

render_stepper(current_step)

# Dual-Palm Upload & Real-Time Quality Gate
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
    <div>
        <h3 style="margin: 0; font-size: 1.35rem; color: #F8FAFC;">📤 Palm Capture & Quality Verification</h3>
        <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.88rem;">
            Upload flat, well-lit photographs of both palms against a contrasting background.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

left_col, right_col = st.columns(2)
uploads, files = {}, {}

for side, col in (("Left", left_col), ("Right", right_col)):
    with col:
        st.subheader(f"{side} palm")
        
        # Check if sample files are pre-loaded
        sample_entry = st.session_state.get("sample_files", {}).get(side)
        
        f = st.file_uploader(f"Upload {side.lower()} palm (JPG/JPEG/PNG)", type=None, key=f"up_{side}")
        
        # Resolve active image data
        name, data = None, None
        if f is not None:
            name = f.name
            data = f.getvalue()
        elif sample_entry is not None:
            name, data = sample_entry
            st.info(f"Loaded demo photo: `{name}`")

        if data is not None and name is not None:
            v = cached_validation(name, data, side)
            uploads[side], files[side] = v, (name, data)
            if v.image is not None:
                st.image(cv2.cvtColor(v.image, cv2.COLOR_BGR2RGB), caption=name, width="stretch")
            
            for e in v.errors:
                st.error(e)
            for w in v.warnings:
                st.warning(w)
            if v.ok:
                st.success("Image accepted. " + ", ".join(f"{k}: {val}" for k, val in v.metrics.items()))
                render_quality_diagnostics(v.metrics, side, v.ok)

ready = len(uploads) == 2 and all(v.ok for v in uploads.values())
if len(uploads) == 2 and not ready:
    st.info("Fix the problems above (replace the image using the uploader) to continue.")

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
if st.button("Analyse palms", type="primary", disabled=not ready):
    with st.spinner("Executing 10-stage digital image processing pipeline…"):
        proc, feats, ann = {}, {}, {}
        for s, (name, data) in files.items():
            proc[s], feats[s], ann[s] = cached_analysis(name, data, s)
    st.session_state.update(proc=proc, feats=feats, ann=ann, report=None, bot=None, passages=None, chat=[])

# Main Application Tabs
if "feats" in st.session_state:
    proc, feats, ann = st.session_state.proc, st.session_state.feats, st.session_state.ann
    t1, t2, t3, t4, t5 = st.tabs([
        "1 · Processing",
        "2 · Detected features",
        "3 · Reading",
        "4 · Chatbot",
        "5 · Methodology & Science"
    ])

    # TAB 1: DIGITAL IMAGE PROCESSING LAB
    with t1:
        st.markdown("""
        <div style="margin-bottom: 18px;">
            <h3 style="margin: 0; color: #F8FAFC;">🔬 Computer Vision Processing Laboratory</h3>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.9rem;">
                Each classical image-processing technique is displayed with rigorous mathematical justification and before-and-after visual evidence.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Each technique is shown as before → after so you can see what it does.")
        
        for s in proc:
            st.subheader(f"{s} palm: original vs processed")
            show_comparisons(proc[s])
            
            # Interactive CLAHE Histogram Analysis Section
            if "4h Histogram before/after CLAHE" in proc[s]:
                with st.expander(f"📊 {s} Palm: CLAHE Contrast Intensity Histogram"):
                    col_h1, col_h2 = st.columns([1, 1])
                    with col_h1:
                        st.image(proc[s]["4h Histogram before/after CLAHE"], caption=f"{s} Palm: CLAHE Histogram Shift", width="stretch")
                    with col_h2:
                        st.markdown("""
                        **Contrast Limited Adaptive Histogram Equalization (CLAHE):**
                        - Operates over contextual $8 \\times 8$ pixel tiles.
                        - Prevents noise amplification via a strict **clip limit of 3.0**.
                        - Clips the histogram and redistributes the excess equally across all gray levels.
                        - Notice how the **red curve (after CLAHE)** broadens the dynamic luminance range across the palm crease valleys compared to the **gray curve (before CLAHE)**.
                        """)
            
            with st.expander("All pipeline stages"):
                items = [(k, v) for k, v in proc[s].items() if not k.startswith("_")]
                for i in range(0, len(items), 4):
                    for col, (name, img) in zip(st.columns(4), items[i:i + 4]):
                        col.image(img, caption=name, width="stretch", clamp=True)

    # TAB 2: DETECTED PALM FEATURES
    with t2:
        st.markdown("""
        <div style="margin-bottom: 18px;">
            <h3 style="margin: 0; color: #F8FAFC;">🖐 Anatomical Palm Feature Extraction</h3>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.9rem;">
                Mathematical skeletonization and directional topology determine principal palmar creases with confidence gating.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Computer-vision observations only. A line is drawn ONLY when it was detected with "
                   "confidence; uncertain and not-detected lines are listed in the legend and table but "
                   "never drawn. White circle/arrow = estimated palm centre and finger direction.")
        
        for s in feats:
            c1, c2 = st.columns([1, 1])
            with c1:
                st.image(ann[s], caption=f"{s} palm: annotated", width="stretch")
                
                # Interactive Annotation Legend
                st.markdown("""
                <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-top: 10px; background: rgba(16, 21, 37, 0.6); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.06);">
                    <div style="display: flex; align-items: center; gap: 6px; font-size: 0.8rem;">
                        <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: rgb(230, 57, 70);"></span>
                        <span style="color: #F8FAFC;">Heart Line</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px; font-size: 0.8rem;">
                        <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: rgb(29, 120, 220);"></span>
                        <span style="color: #F8FAFC;">Head Line</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px; font-size: 0.8rem;">
                        <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: rgb(46, 170, 90);"></span>
                        <span style="color: #F8FAFC;">Life Line</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px; font-size: 0.8rem;">
                        <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: rgb(240, 160, 20);"></span>
                        <span style="color: #F8FAFC;">Fate Line</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with c2:
                st.markdown(f"**{s} palm**")
                
                # Render Hand Morphology & Elemental Type Card
                if "palm" in feats[s]:
                    render_hand_type_card(feats[s]["palm"], s)
                
                # Render Individual Line Feature Cards
                for line_k, line_val in feats[s]["lines"].items():
                    rgb = LINE_COLORS.get(line_k, (139, 92, 246))
                    hex_col = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
                    render_feature_card(line_k, line_val, hex_col)
                
                rows = line_rows(feats[s])      # static tables: readable in screenshots and by screen readers
                st.table([{k: v for k, v in r.items() if k not in ("Start", "End")} for r in rows])
                with st.expander("Where each detected line starts and ends"):
                    st.table([{k: r[k] for k in ("Line", "Start", "End")} for r in rows])
                for n in feats[s]["notes"]:
                    st.caption("⚠ " + n)

    # TAB 3: AI PALM READING (GEMINI + RAG)
    with t3:
        st.markdown("""
        <div style="margin-bottom: 18px;">
            <h3 style="margin: 0; color: #F8FAFC;">📜 AI-Powered Palm Reading</h3>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.9rem;">
                Synthesizing computer vision extractions with curated historical palmistry literature via Google Gemini 3.5.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get("report") is None:
            st.markdown("""
            <div class="glass-panel" style="text-align: center; padding: 36px 20px;">
                <div style="font-size: 2.4rem; margin-bottom: 12px;">✨</div>
                <div style="font-size: 1.25rem; font-weight: 600; color: #F8FAFC; margin-bottom: 8px;">
                    Ready to Generate Structured Reading
                </div>
                <div style="max-width: 600px; margin: 0 auto 24px auto; color: #94A3B8; font-size: 0.9rem; line-height: 1.5;">
                    The system will query our 20-passage palmistry corpus using TF-IDF matching, ground the context 
                    strictly in your detected features, and request a comprehensive reading from Google Gemini.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Generate reading with Gemini", type="primary"):
                try:
                    with st.spinner("Connecting to Google Gemini and generating structured reading…"):
                        report, passages = generate_report(feats, get_retriever())
                    st.session_state.report, st.session_state.passages = report, passages
                    st.session_state.bot = PalmChatbot(feats, report, get_retriever())
                    st.rerun()
                except Exception as e:  # missing key / bad model / quota / network / bad JSON
                    st.error(f"Could not generate the report: {friendly_error(e)}")

        if st.session_state.get("report"):
            r = st.session_state.report
            
            # Executive Report Header Card
            st.markdown("""
            <div class="glass-panel-cyan" style="padding: 22px; margin-bottom: 24px; border-radius: 14px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <div style="font-size: 0.75rem; text-transform: uppercase; color: #22D3EE; font-weight: 700; letter-spacing: 0.08em;">
                            EXECUTIVE REPORT // PALMISTRY INTELLIGENCE
                        </div>
                        <div style="font-size: 1.35rem; font-weight: 700; color: #F8FAFC; margin-top: 4px;">
                            Bilateral Palm Feature & Symbolic Reading
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <span style="background: rgba(34, 211, 238, 0.15); border: 1px solid rgba(34, 211, 238, 0.35); color: #22D3EE; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;">
                            Gemini Grounded
                        </span>
                        <span style="background: rgba(139, 92, 246, 0.15); border: 1px solid rgba(139, 92, 246, 0.35); color: #A78BFA; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;">
                            RAG Verified
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Render Each Report Section in Styled Cards
            for k, t in TITLES.items():
                content = r.get(k, "")
                st.markdown(f"""
                <div class="report-section">
                    <div class="report-section-header">
                        <span>✦</span>
                        <span>{t}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"#### {t}")
                st.markdown(content)
            
            st.info(r.get("disclaimer", DISCLAIMER))
            
            col_d1, col_d2 = st.columns([1, 1])
            with col_d1:
                st.download_button(
                    "Download report (Markdown)",
                    report_to_markdown(r, feats),
                    file_name="palm_reading_report.md",
                    mime="text/markdown",
                    type="primary"
                )
            
            with st.expander("Knowledge passages retrieved for this reading (RAG)"):
                st.markdown("""
                *The following historical and traditional passages were retrieved from our curated palmistry corpus 
                and injected into the Gemini context prompt to ensure strictly grounded interpretations:*
                """)
                for p in st.session_state.passages:
                    st.markdown(f"- **[{p['id']}]** {p['text']}")

    # TAB 4: INTERACTIVE GEMINI CHATBOT
    with t4:
        st.markdown("""
        <div style="margin-bottom: 18px;">
            <h3 style="margin: 0; color: #F8FAFC;">💬 Interactive AI Palm Assistant</h3>
            <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.9rem;">
                Engage in grounded dialogue regarding your palm lines, computer vision observations, and traditional symbolism.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        bot = st.session_state.get("bot")
        if bot is None:
            st.info("Generate the reading first; the chatbot uses it as context.")
        else:
            # Interactive Quick Question Prompts
            st.markdown("<p style='font-size: 0.85rem; color: #94A3B8; margin-bottom: 6px;'>Suggested inquiries:</p>", unsafe_allow_html=True)
            col_q1, col_q2, col_q3 = st.columns(3)
            
            q_to_ask = None
            with col_q1:
                if st.button("❤️ Explain my Heart Line", use_container_width=True):
                    q_to_ask = "What does my heart line traditionally represent?"
            with col_q2:
                if st.button("⚖️ Compare Left & Right Palms", use_container_width=True):
                    q_to_ask = "What differences are visible between my left and right palms?"
            with col_q3:
                if st.button("💼 Career & Ambition Themes", use_container_width=True):
                    q_to_ask = "What does palmistry say about my career?"

            # Display Chat History
            for m in st.session_state.chat:
                with st.chat_message("user" if m["role"] == "user" else "assistant"):
                    st.markdown(m["text"])
            
            st.caption(DISCLAIMER)
            
            q = st.chat_input("Ask about your palms, e.g. 'What does my heart line represent?'")
            if q_to_ask:
                q = q_to_ask
                
            if q:
                st.session_state.chat.append({"role": "user", "text": q})
                try:
                    a = bot.ask(q)
                except Exception as e:
                    a = f"Sorry, I could not answer: {friendly_error(e)}"
                st.session_state.chat.append({"role": "model", "text": a})
                st.rerun()

    # TAB 5: METHODOLOGY & SCIENCE
    with t5:
        st.subheader("📖 Scientific Methodology & Architecture")
        st.caption("Transparent explanation of image processing mathematics, computer vision algorithms, and LLM grounding.")
        
        with st.expander("1. Digital Image Processing Pipeline", expanded=True):
            st.markdown("""
            - **Geometric & Intensity Normalization:** The application standardizes input resolution to a fixed width of 900 px and applies min-max intensity normalisation.
            - **Luminance Extraction:** Grayscale conversion uses standard ITU-R BT.601 luma weighting (Y = 0.299R + 0.587G + 0.114B).
            - **Gaussian Denoising:** High-frequency sensor grain is suppressed with a 5x5 Gaussian kernel (sigma = 1.2).
            - **CLAHE:** Contrast Limited Adaptive Histogram Equalization with a clip limit of 3.0 and 8x8 grid tiles amplifies faint crease valleys without saturating skin regions.
            - **Morphological Filtering:** Black-hat filtering extracts dark valleys, followed by adaptive Gaussian neighborhood thresholding (31x31, C = -6) and morphological closing/opening.
            """)
        
        with st.expander("2. Hand Segmentation & Fast Distance Transform", expanded=True):
            st.markdown("""
            - **Adaptive Segmentation:** Hand segmentation adapts to multiple skin tones using an ensemble of CIE-Lab Euclidean background distance, Chroma-Cr Otsu, and Cr/Cb 2-means clustering, with GrabCut as an edge fallback.
            - **Fast O(pixels) Disc Opening:** Palm center identification uses a distance transform maximum smoothed by the centroid of an opened palm mask. Rather than using a sluggish ~280 px morphological kernel, the disc opening is computed in O(pixels) via dual distance transforms, accelerating runtime by 8x.
            """)
        
        with st.expander("3. RAG Architecture & Grounded Generative AI", expanded=True):
            st.markdown("""
            - **Structured Inputs:** The LLM receives structured numerical and qualitative features only (curvature, prominence, status, hand shape).
            - **Zero Pixel Uploads:** Raw pixel images are never transmitted to Google Gemini.
            - **TF-IDF Knowledge Matching:** A 20-passage historical palmistry corpus is queried using TF-IDF cosine similarity.
            - **Strict Anti-Hallucination:** Strict system prompts forbid inventing undetected features.
            - **Programmatic Disclaimers:** Ethical disclaimers are appended programmatically in Python code, independent of model memory.
            """)
