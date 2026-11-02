"""UI Components and visual renderers for AI Palm Reader."""
from __future__ import annotations
import streamlit as st
from . import DISCLAIMER

def render_hero(on_sample_click=None) -> None:
    """Renders the executive hero banner with 3-step workflow."""
    st.markdown("""
    <div style="background: rgba(18, 25, 44, 0.85); border: 1px solid rgba(139, 92, 246, 0.35); border-radius: 16px; padding: 28px; margin-bottom: 24px;">
        <div style="display: inline-block; background: rgba(139, 92, 246, 0.2); border: 1px solid rgba(139, 92, 246, 0.4); color: #C4B5FD; padding: 4px 12px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px;">
            ✦ Classical Computer Vision & Google Gemini Architecture
        </div>
        <h2 style="font-size: 2.1rem; font-weight: 700; color: #F8FAFC; margin-bottom: 10px;">
            Discover the Patterns Within Your Palm
        </h2>
        <p style="color: #94A3B8; font-size: 1rem; line-height: 1.5; max-width: 820px; margin-bottom: 20px;">
            Experience a rigorous multi-stage Digital Image Processing pipeline that extracts hand geometry, 
            detects palmar creases with mathematical confidence gating, and synthesizes grounded insights via 
            retrieval-augmented Google Gemini intelligence in English, Sinhala, and Tamil.
        </p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 14px;">
            <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 14px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-size: 1.1rem;">🔬</span>
                    <strong style="color: #F8FAFC; font-size: 0.9rem;">1. Scientific Verification</strong>
                </div>
                <div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.4;">
                    Rigorous quality gate measuring silhouette blur, hand-region exposure, and frame coverage before processing begins.
                </div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 14px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-size: 1.1rem;">⚡</span>
                    <strong style="color: #F8FAFC; font-size: 0.9rem;">2. 10-Stage CV Pipeline</strong>
                </div>
                <div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.4;">
                    Multi-scale CLAHE, adaptive Otsu/k-means segmentation, black-hat crease enhancement, and skeleton topology.
                </div>
            </div>
            <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 14px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-size: 1.1rem;">🧠</span>
                    <strong style="color: #F8FAFC; font-size: 0.9rem;">3. RAG Gemini Synthesis</strong>
                </div>
                <div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.4;">
                    Deterministic knowledge retrieval over 20 curated historical passages, grounded strictly in detected anatomical features.
                </div>
            </div>
        </div>
        
        <div style="margin-top: 18px; padding: 10px 14px; background: rgba(139, 92, 246, 0.1); border-left: 3px solid #8B5CF6; border-radius: 6px; font-size: 0.8rem; color: #CBD5E1;">
            <strong>Privacy & Ethics Assurance:</strong> Palm images are processed exclusively in RAM memory and are never written to disk or sent to Google servers. Raw pixels never leave your session. Interpretations are strictly for cultural & entertainment purposes.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_stepper(current_step: int) -> None:
    """Renders the horizontal progress stepper."""
    steps = [
        (1, "Upload & Quality"),
        (2, "CV Processing"),
        (3, "Feature Extraction"),
        (4, "Gemini Reading"),
        (5, "AI Assistant")
    ]
    html = '<div class="stepper-container">'
    for num, label in steps:
        if num < current_step:
            cls = "step-item completed"
            icon = "✓"
        elif num == current_step:
            cls = "step-item active"
            icon = str(num)
        else:
            cls = "step-item"
            icon = str(num)
        html += f"""
        <div class="{cls}">
            <div class="step-num">{icon}</div>
            <span>{label}</span>
        </div>
        """
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_quality_diagnostics(metrics: dict, side: str, ok: bool) -> None:
    """Renders interactive quality scorecard with actual CV metrics."""
    if not metrics:
        return
    
    status_color = "#10B981" if ok else "#EF4444"
    status_text = "PASSED QUALITY GATE" if ok else "ACTION REQUIRED"
    
    edge_width = metrics.get('edge_width_px', 0)
    blur_score = "Sharp" if edge_width < 4.0 else ("Acceptable" if edge_width < 5.0 else "Blurry")
    blur_color = "#10B981" if edge_width < 4.0 else ("#F59E0B" if edge_width < 5.0 else "#EF4444")
    
    brightness = metrics.get('brightness', 0)
    clipped = metrics.get('clipped', 0) * 100
    exp_status = "Balanced" if 50 <= brightness <= 210 and clipped < 10 else "Extreme Light"
    exp_color = "#10B981" if exp_status == "Balanced" else "#F59E0B"
    
    hand_frac = metrics.get('hand_fraction', 0) * 100
    cov_status = "Optimal" if hand_frac >= 15 else "Too Small"
    cov_color = "#10B981" if hand_frac >= 15 else "#EF4444"
    
    st.markdown(f"""
    <div style="background: rgba(16, 21, 37, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 14px; margin-top: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.06); padding-bottom: 8px;">
            <strong style="color: #F8FAFC; font-size: 0.9rem;">{side} Palm Quality Verification</strong>
            <span style="color: {status_color}; font-size: 0.75rem; font-weight: 700; background: rgba(255, 255, 255, 0.05); padding: 3px 8px; border-radius: 6px; border: 1px solid {status_color};">
                {status_text}
            </span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
            <div class="metric-chip">
                <span class="metric-chip-label">Sharpness (Edge):</span>
                <span class="metric-chip-value" style="color: {blur_color};">{edge_width:.2f} px ({blur_score})</span>
            </div>
            <div class="metric-chip">
                <span class="metric-chip-label">Hand Exposure:</span>
                <span class="metric-chip-value" style="color: {exp_color};">{brightness:.1f} / 255 ({exp_status})</span>
            </div>
            <div class="metric-chip">
                <span class="metric-chip-label">Frame Coverage:</span>
                <span class="metric-chip-value" style="color: {cov_color};">{hand_frac:.1f}% ({cov_status})</span>
            </div>
            <div class="metric-chip">
                <span class="metric-chip-label">Segmentation:</span>
                <span class="metric-chip-value">{metrics.get('segmentation', 'adaptive')}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_feature_card(line_name: str, line_data: dict, color_hex: str) -> None:
    """Renders a feature card for a detected palmar line."""
    status = line_data.get("status", "not_detected")
    conf = line_data.get("confidence", 0.0)
    curv = line_data.get("curvature") or "n/a"
    prom = line_data.get("prominence") or "n/a"
    start_r = line_data.get("start_region") or "n/a"
    end_r = line_data.get("end_region") or "n/a"
    
    display_title = line_name.replace("_", " ").title()
    status_cls = f"status-pill status-{status}"
    
    st.markdown(f"""
    <div class="feature-card" style="border-left: 4px solid {color_hex};">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 10px; height: 10px; border-radius: 50%; background: {color_hex}; box-shadow: 0 0 8px {color_hex};"></div>
                <strong style="color: #F8FAFC; font-size: 1rem;">{display_title}</strong>
            </div>
            <span class="{status_cls}">{status.replace('_', ' ')}</span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; font-size: 0.82rem; margin-top: 10px;">
            <div>
                <span style="color: #94A3B8;">Confidence:</span>
                <strong style="color: #F8FAFC; margin-left: 4px;">{conf:.2f} ({int(conf * 100)}%)</strong>
            </div>
            <div>
                <span style="color: #94A3B8;">Curvature:</span>
                <strong style="color: #F8FAFC; margin-left: 4px;">{curv}</strong>
            </div>
            <div>
                <span style="color: #94A3B8;">Prominence:</span>
                <strong style="color: #F8FAFC; margin-left: 4px;">{prom}</strong>
            </div>
            <div>
                <span style="color: #94A3B8;">Trajectory:</span>
                <strong style="color: #F8FAFC; margin-left: 4px;">{start_r} → {end_r}</strong>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_hand_type_card(palm: dict, side: str) -> None:
    """Renders the hand geometry and elemental classification card."""
    htype = palm.get("palmistry_hand_type", "Unknown")
    shape = palm.get("palm_shape", "unknown")
    fingers = palm.get("finger_length", "unknown")
    aspect = palm.get("palm_length_to_width", 0.0)
    f_ratio = palm.get("finger_to_palm_length", 0.0)
    note = palm.get("note", "")
    
    element_colors = {
        "Fire": "#EF4444",
        "Earth": "#10B981",
        "Air": "#22D3EE",
        "Water": "#8B5CF6"
    }
    color = element_colors.get(htype, "#A78BFA")
    
    st.markdown(f"""
    <div style="background: rgba(20, 27, 45, 0.7); border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 14px; padding: 18px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.06); padding-bottom: 10px;">
            <strong style="font-size: 1.05rem; color: #F8FAFC;">🖐 {side} Palm Morphology & Geometry</strong>
            <span style="background: rgba(255, 255, 255, 0.06); color: {color}; border: 1px solid {color}; border-radius: 8px; padding: 4px 10px; font-weight: 700; font-size: 0.85rem;">
                {htype} Hand Type
            </span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; font-size: 0.85rem;">
            <div class="metric-chip">
                <span class="metric-chip-label">Palm Silhouette:</span>
                <span class="metric-chip-value">{shape.capitalize()}</span>
            </div>
            <div class="metric-chip">
                <span class="metric-chip-label">Fingers Silhouette:</span>
                <span class="metric-chip-value">{fingers.capitalize()}</span>
            </div>
            <div class="metric-chip">
                <span class="metric-chip-label">Length / Width:</span>
                <span class="metric-chip-value">{aspect:.2f}</span>
            </div>
            <div class="metric-chip">
                <span class="metric-chip-label">Finger / Palm Ratio:</span>
                <span class="metric-chip-value">{f_ratio:.2f}</span>
            </div>
        </div>
        <div style="margin-top: 10px; font-size: 0.78rem; color: #94A3B8; font-style: italic;">
            Note: {note}
        </div>
    </div>
    """, unsafe_allow_html=True)
