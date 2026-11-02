import React from "react";
import {
  ShieldCheck,
  Zap,
  Hand,
  Brain,
  Sparkles,
  CheckCircle2,
} from "lucide-react";

export const MethodologyView: React.FC = () => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px", maxWidth: "1200px" }}>
      {/* Page Header */}
      <div>
        <div className="badge badge-cyan" style={{ marginBottom: "10px" }}>
          <Sparkles size={12} /> Computer Vision &amp; Digital Image Processing
        </div>
        <h2 style={{ fontSize: "1.8rem", color: "#F8FAFC", marginBottom: "6px" }}>
          Scientific Methodology &amp; Architecture
        </h2>
        <p style={{ color: "#94A3B8", fontSize: "0.92rem", lineHeight: 1.5 }}>
          A transparent overview of how Palmistry AI transforms raw hand photographs into
          reproducible geometric features and grounded cultural readings.
        </p>
      </div>

      {/* 5-Stage Visual Workflow Stepper */}
      <div
        className="glass-panel"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(5, 1fr)",
          gap: "12px",
          padding: "20px",
          textAlign: "center",
        }}
      >
        {[
          { step: "1", title: "Quality Gate", sub: "Edge step & focus check", color: "#38BDF8" },
          { step: "2", title: "Pre-Sharpen", sub: "Unsharp mask enhancement", color: "#818CF8" },
          { step: "3", title: "CLAHE Contrast", sub: "8×8 adaptive histogram", color: "#A78BFA" },
          { step: "4", title: "Crease Morphology", sub: "21×21 Black-Hat filter", color: "#C084FC" },
          { step: "5", title: "Grounded AI", sub: "Gemini RAG interpretation", color: "#34D399" },
        ].map((s, idx) => (
          <div
            key={idx}
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "6px",
              position: "relative",
            }}
          >
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "50%",
                background: `rgba(255, 255, 255, 0.05)`,
                border: `2px solid ${s.color}`,
                color: s.color,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 700,
                fontSize: "0.9rem",
              }}
            >
              {s.step}
            </div>
            <div style={{ fontSize: "0.86rem", fontWeight: 700, color: "#F8FAFC" }}>
              {s.title}
            </div>
            <div style={{ fontSize: "0.72rem", color: "#94A3B8" }}>{s.sub}</div>
          </div>
        ))}
      </div>

      {/* 4 Clean Principle Cards (2x2 Grid) */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        {/* Card 1: Acquisition & Quality Gating */}
        <div className="glass-panel" style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "38px",
                height: "38px",
                borderRadius: "10px",
                background: "rgba(56, 189, 248, 0.15)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <ShieldCheck size={20} color="#38BDF8" />
            </div>
            <div>
              <h3 style={{ fontSize: "1.08rem", color: "#F8FAFC" }}>
                1. Image Quality Gating
              </h3>
              <span style={{ fontSize: "0.75rem", color: "#38BDF8", fontWeight: 600 }}>
                Verification before pipeline execution
              </span>
            </div>
          </div>

          <p style={{ fontSize: "0.85rem", color: "#94A3B8", lineHeight: 1.55 }}>
            To prevent false crease readings, every uploaded image must pass strict automated validation:
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "0.82rem", color: "#CBD5E1" }}>
              <CheckCircle2 size={15} color="#38BDF8" style={{ flexShrink: 0, marginTop: "2px" }} />
              <span>
                <strong>Edge Sharpness:</strong> Evaluates silhouette boundary width (step height / peak gradient). Edge width &gt; 5.0 px flags motion or defocus blur.
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "0.82rem", color: "#CBD5E1" }}>
              <CheckCircle2 size={15} color="#38BDF8" style={{ flexShrink: 0, marginTop: "2px" }} />
              <span>
                <strong>Skin Segmentation &amp; Coverage:</strong> Hand region must occupy at least 12% of the frame to prevent distant shot errors.
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "0.82rem", color: "#CBD5E1" }}>
              <CheckCircle2 size={15} color="#38BDF8" style={{ flexShrink: 0, marginTop: "2px" }} />
              <span>
                <strong>Luminance Bounds:</strong> Mean hand luma must fall within [35, 230] with fewer than 20% blown-out pixels.
              </span>
            </div>
          </div>
        </div>

        {/* Card 2: Pre-Processing & Contrast Enhancement */}
        <div className="glass-panel" style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "38px",
                height: "38px",
                borderRadius: "10px",
                background: "rgba(129, 140, 248, 0.15)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Zap size={20} color="#818CF8" />
            </div>
            <div>
              <h3 style={{ fontSize: "1.08rem", color: "#F8FAFC" }}>
                2. Pre-Processing &amp; CLAHE
              </h3>
              <span style={{ fontSize: "0.75rem", color: "#818CF8", fontWeight: 600 }}>
                Scale-invariance &amp; local contrast adaptation
              </span>
            </div>
          </div>

          <p style={{ fontSize: "0.85rem", color: "#94A3B8", lineHeight: 1.55 }}>
            Digital image processing normalizes geometric dimensions and accentuates valleys:
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "0.82rem", color: "#CBD5E1" }}>
              <CheckCircle2 size={15} color="#818CF8" style={{ flexShrink: 0, marginTop: "2px" }} />
              <span>
                <strong>Unsharp Masking:</strong> Enhances high-frequency edge gradients prior to downscaling using a weighted Gaussian detail mask.
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "0.82rem", color: "#CBD5E1" }}>
              <CheckCircle2 size={15} color="#818CF8" style={{ flexShrink: 0, marginTop: "2px" }} />
              <span>
                <strong>Fixed 900px Scale:</strong> Normalizes structuring element radius across different camera resolutions.
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "0.82rem", color: "#CBD5E1" }}>
              <CheckCircle2 size={15} color="#818CF8" style={{ flexShrink: 0, marginTop: "2px" }} />
              <span>
                <strong>CLAHE Equalization:</strong> Equalizes contrast across 8×8 contextual tiles with a clip limit of 3.0 to avoid noise blowouts.
              </span>
            </div>
          </div>
        </div>

        {/* Card 3: Feature Extraction & Creases */}
        <div className="glass-panel" style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "38px",
                height: "38px",
                borderRadius: "10px",
                background: "rgba(192, 132, 252, 0.15)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Hand size={20} color="#C084FC" />
            </div>
            <div>
              <h3 style={{ fontSize: "1.08rem", color: "#F8FAFC" }}>
                3. Morphological Crease Extraction
              </h3>
              <span style={{ fontSize: "0.75rem", color: "#C084FC", fontWeight: 600 }}>
                Black-Hat filter &amp; morphological closing
              </span>
            </div>
          </div>

          <p style={{ fontSize: "0.85rem", color: "#94A3B8", lineHeight: 1.55 }}>
            Mathematical morphology isolates physical palmar grooves from ambient skin tone:
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "0.82rem", color: "#CBD5E1" }}>
              <CheckCircle2 size={15} color="#C084FC" style={{ flexShrink: 0, marginTop: "2px" }} />
              <span>
                <strong>21×21 Black-Hat Transform:</strong> Computes morphological closing minus original to lift narrow dark crease grooves.
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "0.82rem", color: "#CBD5E1" }}>
              <CheckCircle2 size={15} color="#C084FC" style={{ flexShrink: 0, marginTop: "2px" }} />
              <span>
                <strong>Adaptive Thresholding:</strong> Evaluates local 31×31 neighborhoods, making line tracing immune to uneven cast shadows.
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "0.82rem", color: "#CBD5E1" }}>
              <CheckCircle2 size={15} color="#C084FC" style={{ flexShrink: 0, marginTop: "2px" }} />
              <span>
                <strong>Hand Geometry:</strong> Calculates palm-to-finger length ratio to categorize hand morphology (Earth, Air, Fire, Water).
              </span>
            </div>
          </div>
        </div>

        {/* Card 4: Grounded AI & Multilingual RAG */}
        <div className="glass-panel" style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "38px",
                height: "38px",
                borderRadius: "10px",
                background: "rgba(52, 211, 153, 0.15)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Brain size={20} color="#34D399" />
            </div>
            <div>
              <h3 style={{ fontSize: "1.08rem", color: "#F8FAFC" }}>
                4. Grounded AI Interpretation (RAG)
              </h3>
              <span style={{ fontSize: "0.75rem", color: "#34D399", fontWeight: 600 }}>
                20-passage knowledge base &amp; zero hallucination
              </span>
            </div>
          </div>

          <p style={{ fontSize: "0.85rem", color: "#94A3B8", lineHeight: 1.55 }}>
            Synthesizes cultural palmistry literature without hallucinating missing lines:
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "0.82rem", color: "#CBD5E1" }}>
              <CheckCircle2 size={15} color="#34D399" style={{ flexShrink: 0, marginTop: "2px" }} />
              <span>
                <strong>TF-IDF Retrieval:</strong> Matches detected crease attributes against 20 verified classical palmistry reference texts.
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "0.82rem", color: "#CBD5E1" }}>
              <CheckCircle2 size={15} color="#34D399" style={{ flexShrink: 0, marginTop: "2px" }} />
              <span>
                <strong>Strict Confidence Gating:</strong> If a crease is unconfirmed, Gemini is forbidden from inventing readings.
              </span>
            </div>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "8px", fontSize: "0.82rem", color: "#CBD5E1" }}>
              <CheckCircle2 size={15} color="#34D399" style={{ flexShrink: 0, marginTop: "2px" }} />
              <span>
                <strong>Native Trilingual Output:</strong> Synthesizes reports in authentic English, Sinhala (සිංහල), and Tamil (தமிழ்) scripts.
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Table */}
      <div className="glass-panel" style={{ padding: "20px 24px" }}>
        <h3 style={{ fontSize: "1.05rem", color: "#F8FAFC", marginBottom: "14px" }}>
          Core Algorithmic Formulations
        </h3>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.84rem" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border-glass)", textAlign: "left" }}>
                <th style={{ padding: "8px 12px", color: "#94A3B8" }}>Processing Step</th>
                <th style={{ padding: "8px 12px", color: "#94A3B8" }}>Mathematical Function</th>
                <th style={{ padding: "8px 12px", color: "#94A3B8" }}>Primary Engineering Benefit</th>
              </tr>
            </thead>
            <tbody style={{ color: "#CBD5E1" }}>
              <tr style={{ borderBottom: "1px solid var(--border-glass)" }}>
                <td style={{ padding: "10px 12px", fontWeight: 600 }}>Unsharp Masking</td>
                <td style={{ padding: "10px 12px", fontFamily: "monospace", color: "#38BDF8" }}>
                  I + α·(I - G_σ(I))
                </td>
                <td style={{ padding: "10px 12px" }}>Enhances edge gradient before normalisation</td>
              </tr>
              <tr style={{ borderBottom: "1px solid var(--border-glass)" }}>
                <td style={{ padding: "10px 12px", fontWeight: 600 }}>CLAHE</td>
                <td style={{ padding: "10px 12px", fontFamily: "monospace", color: "#818CF8" }}>
                  ClipLimit = 3.0, Grid = 8×8
                </td>
                <td style={{ padding: "10px 12px" }}>Local contrast enhancement without noise blowout</td>
              </tr>
              <tr style={{ borderBottom: "1px solid var(--border-glass)" }}>
                <td style={{ padding: "10px 12px", fontWeight: 600 }}>Black-Hat Transform</td>
                <td style={{ padding: "10px 12px", fontFamily: "monospace", color: "#C084FC" }}>
                  (I • B_21×21) - I
                </td>
                <td style={{ padding: "10px 12px" }}>Isolates thin dark troughs from skin background</td>
              </tr>
              <tr>
                <td style={{ padding: "10px 12px", fontWeight: 600 }}>Adaptive Threshold</td>
                <td style={{ padding: "10px 12px", fontFamily: "monospace", color: "#34D399" }}>
                  T(x,y) = μ_31×31(x,y) - C
                </td>
                <td style={{ padding: "10px 12px" }}>Binarization immune to variable palm curvature shadows</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
