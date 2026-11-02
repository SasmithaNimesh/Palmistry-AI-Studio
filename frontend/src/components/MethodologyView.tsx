import React from "react";
import { Cpu, Layers, Brain, Shield } from "lucide-react";

export const MethodologyView: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: "24px" }}>
        <h2 style={{ fontSize: "1.6rem", color: "#F8FAFC", marginBottom: "4px" }}>
          Scientific Methodology & Architecture
        </h2>
        <p style={{ color: "#94A3B8", fontSize: "0.9rem" }}>
          Mathematical formulation of digital image processing, computer vision
          heuristics, and RAG grounding.
        </p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        {/* Stage 1: DIP */}
        <div className="glass-panel">
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              marginBottom: "14px",
            }}
          >
            <Cpu size={22} color="#22D3EE" />
            <h3 style={{ fontSize: "1.2rem", color: "#F8FAFC" }}>
              1. Digital Image Processing Pipeline
            </h3>
          </div>
          <div
            style={{
              fontSize: "0.9rem",
              color: "#CBD5E1",
              lineHeight: 1.65,
              display: "flex",
              flexDirection: "column",
              gap: "10px",
            }}
          >
            <p>
              <strong>Geometric & Intensity Normalization:</strong> Input
              photographs are scaled to a fixed width of 900 px (using area
              interpolation for downscaling or bicubic for upscaling) to ensure all
              morphological structuring elements operate at scale-invariant pixel
              metrics. Min-max normalization maps intensity ranges to [0, 255].
            </p>
            <p>
              <strong>Luminance Conversion:</strong> Grayscale conversion uses standard
              ITU-R BT.601 luma weighting (Y = 0.299R + 0.587G + 0.114B), which
              preserves the spectral sensitivity where skin crease valleys appear as
              dark troughs.
            </p>
            <p>
              <strong>Noise Suppression:</strong> A 5×5 Gaussian kernel with standard
              deviation σ = 1.2 suppresses fine skin pores, epidermal texture, and
              sensor photon noise while retaining crease structural boundaries.
            </p>
            <p>
              <strong>CLAHE (Contrast Limited Adaptive Histogram Equalization):</strong>{" "}
              Local contrast is enhanced across 8×8 contextual grid tiles with an
              enforced clip limit of 3.0. Faint creases gain prominence without
              amplifying noise in homogeneous hand regions.
            </p>
            <p>
              <strong>Crease Enhancement via Black-Hat Transform:</strong> A 21×21
              elliptical structuring element computes the morphological black-hat
              transform (closing minus original), isolating narrow dark features
              smaller than the structuring element.
            </p>
          </div>
        </div>

        {/* Stage 2: Hand Segmentation & Geometry */}
        <div className="glass-panel">
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              marginBottom: "14px",
            }}
          >
            <Layers size={22} color="#8B5CF6" />
            <h3 style={{ fontSize: "1.2rem", color: "#F8FAFC" }}>
              2. Adaptive Segmentation & Fast Disc Opening
            </h3>
          </div>
          <div
            style={{
              fontSize: "0.9rem",
              color: "#CBD5E1",
              lineHeight: 1.65,
              display: "flex",
              flexDirection: "column",
              gap: "10px",
            }}
          >
            <p>
              <strong>Adaptive Hand Segmentation:</strong> Evaluates four candidate
              methods: CIE-Lab background distance (Otsu threshold), Chroma-Cr Otsu,
              Cr/Cb 2-means clustering, and fixed range. The optimal candidate is chosen
              by a specialized score function (evaluating area, centrality, and compactness),
              falling back to GrabCut if contrast is low.
            </p>
            <p>
              <strong>Fast O(pixels) Disc Opening:</strong> To isolate the palm from the
              fingers without running a sluggish 280 px morphological kernel, the disc
              opening is computed via two Euclidean distance transforms (erosion of core
              followed by dilation). This achieves an 8× runtime acceleration while
              yielding identical mathematical results.
            </p>
            <p>
              <strong>Hand Shape Ratios:</strong> Palm length-to-width ratio and finger
              length ratios are extracted from the silhouette moments to classify the
              morphology into Earth, Air, Fire, or Water hand types.
            </p>
          </div>
        </div>

        {/* Stage 3: RAG & Gemini */}
        <div className="glass-panel">
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              marginBottom: "14px",
            }}
          >
            <Brain size={22} color="#10B981" />
            <h3 style={{ fontSize: "1.2rem", color: "#F8FAFC" }}>
              3. Retrieval-Augmented Generation (RAG) Architecture
            </h3>
          </div>
          <div
            style={{
              fontSize: "0.9rem",
              color: "#CBD5E1",
              lineHeight: 1.65,
              display: "flex",
              flexDirection: "column",
              gap: "10px",
            }}
          >
            <p>
              <strong>Deterministic Grounding:</strong> Google Gemini 3.5 receives
              strictly structured JSON data containing line status, confidence,
              curvature, and prominence. Pixel coordinates and paths are stripped. Raw
              images are never uploaded to Google servers.
            </p>
            <p>
              <strong>TF-IDF Knowledge Matching:</strong> A 20-passage curated
              palmistry corpus is queried using TF-IDF cosine similarity. Only passages
              directly pertinent to the detected features are injected into the system
              prompt.
            </p>
            <p>
              <strong>Strict Anti-Hallucination Constraints:</strong> System prompts
              strictly forbid describing features marked as uncertain or not detected. If
              a user queries an absent line in the chatbot, a deterministic question
              grounding note informs the model of its absence.
            </p>
          </div>
        </div>

        {/* Stage 4: Ethics & Privacy */}
        <div className="glass-panel" style={{ borderLeft: "4px solid #F59E0B" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              marginBottom: "14px",
            }}
          >
            <Shield size={22} color="#F59E0B" />
            <h3 style={{ fontSize: "1.2rem", color: "#F8FAFC" }}>
              4. Ethics, Transparency & Privacy Policy
            </h3>
          </div>
          <div
            style={{
              fontSize: "0.9rem",
              color: "#CBD5E1",
              lineHeight: 1.65,
            }}
          >
            <p style={{ marginBottom: "10px" }}>
              <strong>In-Memory Privacy Shield:</strong> Uploaded palm photos are held
              strictly in ephemeral RAM during the active session. They are never written
              to disk or stored in external databases.
            </p>
            <p>
              <strong>Cultural Practice Disclaimer:</strong> Palmistry is an ancient
              cultural tradition and form of entertainment. It has no empirical validity
              in diagnosing medical health, predicting financial futures, or assessing
              psychological traits. All generated reports and chatbot responses include
              mandatory disclaimers appended programmatically.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
