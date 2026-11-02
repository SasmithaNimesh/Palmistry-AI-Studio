import React from "react";
import {
  Sparkles,
  ArrowRight,
  Cpu,
  Layers,
  BrainCircuit,
  UploadCloud,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
} from "lucide-react";
import type { PalmSlot, AnalysisResult } from "../api";

interface DashboardViewProps {
  onStartAnalysis: () => void;
  onLoadSample: (pair: string) => void;
  leftPalm: PalmSlot | null;
  rightPalm: PalmSlot | null;
  analysis: AnalysisResult | null;
  hasReading: boolean;
  onNavigate: (tab: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  onStartAnalysis,
  onLoadSample,
  leftPalm,
  rightPalm,
  analysis,
  hasReading,
  onNavigate,
}) => {
  return (
    <div>
      {/* Hero Card */}
      <div
        className="glass-panel"
        style={{
          position: "relative",
          overflow: "hidden",
          padding: "36px 40px",
          marginBottom: "28px",
          borderColor: "rgba(139, 92, 246, 0.4)",
          background:
            "radial-gradient(circle at 85% 20%, rgba(139, 92, 246, 0.18) 0%, transparent 60%), rgba(18, 25, 44, 0.8)",
        }}
      >
        <div style={{ maxWidth: "750px" }}>
          <div className="badge badge-purple" style={{ marginBottom: "14px" }}>
            <Sparkles size={12} /> Next-Gen Computer Vision & Gemini 3.5 Studio
          </div>
          <h1
            className="text-gradient"
            style={{
              fontSize: "2.4rem",
              fontWeight: 700,
              lineHeight: 1.15,
              marginBottom: "12px",
            }}
          >
            Discover the Patterns Within Your Palm
          </h1>
          <p
            style={{
              color: "#94A3B8",
              fontSize: "1.05rem",
              lineHeight: 1.55,
              marginBottom: "24px",
            }}
          >
            A high-precision image processing laboratory coupled with Google Gemini
            RAG to decode palmar morphology, detect principal creases with
            confidence gating, and synthesize grounded insights in English, Sinhala,
            and Tamil.
          </p>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "14px",
              flexWrap: "wrap",
            }}
          >
            <button className="btn-primary" onClick={onStartAnalysis}>
              <span>Start Palm Analysis</span>
              <ArrowRight size={16} />
            </button>

            <button
              className="btn-secondary"
              onClick={() => onLoadSample("pair1")}
            >
              <Cpu size={16} color="#22D3EE" />
              <span>⚡ Load Demo Palm (Pair 1)</span>
            </button>
          </div>
        </div>

        {/* Decorative Floating Emblem */}
        <div
          style={{
            position: "absolute",
            right: "40px",
            top: "50%",
            transform: "translateY(-50%)",
            width: "160px",
            height: "160px",
            borderRadius: "50%",
            background:
              "radial-gradient(circle, rgba(139, 92, 246, 0.25) 0%, rgba(34, 211, 238, 0.1) 60%, transparent 80%)",
            border: "1px solid rgba(139, 92, 246, 0.3)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "4.5rem",
            boxShadow: "0 0 50px rgba(139, 92, 246, 0.25)",
            pointerEvents: "none",
          }}
        >
          🖐
        </div>
      </div>

      {/* Analysis Session Status Radar */}
      <h3
        style={{
          fontSize: "1.2rem",
          color: "#F8FAFC",
          marginBottom: "16px",
          display: "flex",
          alignItems: "center",
          gap: "8px",
        }}
      >
        <Layers size={18} color="#22D3EE" /> Active Session Overview
      </h3>

      <div className="grid-4" style={{ marginBottom: "28px" }}>
        {/* Left Palm Card */}
        <div
          className="glass-panel"
          style={{ padding: "18px", cursor: "pointer" }}
          onClick={() => onNavigate("upload")}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "10px",
            }}
          >
            <span
              style={{
                fontSize: "0.85rem",
                color: "#94A3B8",
                fontWeight: 600,
              }}
            >
              Left Palm
            </span>
            {leftPalm?.ok ? (
              <span className="badge badge-emerald">
                <CheckCircle2 size={12} /> Accepted
              </span>
            ) : (
              <span className="badge badge-amber">
                <AlertCircle size={12} /> Pending
              </span>
            )}
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              marginTop: "8px",
            }}
          >
            {leftPalm?.preview_url ? (
              <img
                src={leftPalm.preview_url}
                alt="Left palm thumbnail"
                style={{
                  width: "50px",
                  height: "50px",
                  objectFit: "cover",
                  borderRadius: "8px",
                  border: "1px solid var(--border-glass)",
                }}
              />
            ) : (
              <div
                style={{
                  width: "50px",
                  height: "50px",
                  borderRadius: "8px",
                  background: "rgba(255, 255, 255, 0.04)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#64748B",
                }}
              >
                <UploadCloud size={20} />
              </div>
            )}
            <div>
              <div
                style={{
                  fontSize: "0.85rem",
                  fontWeight: 600,
                  color: "#F8FAFC",
                }}
              >
                {leftPalm?.name || "No image"}
              </div>
              <div style={{ fontSize: "0.75rem", color: "#64748B" }}>
                {leftPalm?.metrics
                  ? `${leftPalm.metrics.width}×${leftPalm.metrics.height} px`
                  : "Click to upload"}
              </div>
            </div>
          </div>
        </div>

        {/* Right Palm Card */}
        <div
          className="glass-panel"
          style={{ padding: "18px", cursor: "pointer" }}
          onClick={() => onNavigate("upload")}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "10px",
            }}
          >
            <span
              style={{
                fontSize: "0.85rem",
                color: "#94A3B8",
                fontWeight: 600,
              }}
            >
              Right Palm
            </span>
            {rightPalm?.ok ? (
              <span className="badge badge-emerald">
                <CheckCircle2 size={12} /> Accepted
              </span>
            ) : (
              <span className="badge badge-amber">
                <AlertCircle size={12} /> Pending
              </span>
            )}
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              marginTop: "8px",
            }}
          >
            {rightPalm?.preview_url ? (
              <img
                src={rightPalm.preview_url}
                alt="Right palm thumbnail"
                style={{
                  width: "50px",
                  height: "50px",
                  objectFit: "cover",
                  borderRadius: "8px",
                  border: "1px solid var(--border-glass)",
                }}
              />
            ) : (
              <div
                style={{
                  width: "50px",
                  height: "50px",
                  borderRadius: "8px",
                  background: "rgba(255, 255, 255, 0.04)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#64748B",
                }}
              >
                <UploadCloud size={20} />
              </div>
            )}
            <div>
              <div
                style={{
                  fontSize: "0.85rem",
                  fontWeight: 600,
                  color: "#F8FAFC",
                }}
              >
                {rightPalm?.name || "No image"}
              </div>
              <div style={{ fontSize: "0.75rem", color: "#64748B" }}>
                {rightPalm?.metrics
                  ? `${rightPalm.metrics.width}×${rightPalm.metrics.height} px`
                  : "Click to upload"}
              </div>
            </div>
          </div>
        </div>

        {/* CV Pipeline Status */}
        <div
          className="glass-panel"
          style={{ padding: "18px", cursor: "pointer" }}
          onClick={() => onNavigate("cvlab")}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "10px",
            }}
          >
            <span
              style={{
                fontSize: "0.85rem",
                color: "#94A3B8",
                fontWeight: 600,
              }}
            >
              CV Pipeline
            </span>
            {analysis ? (
              <span className="badge badge-emerald">Ready</span>
            ) : (
              <span className="badge badge-purple">Idle</span>
            )}
          </div>
          <div style={{ marginTop: "10px" }}>
            <div
              style={{
                fontSize: "1.1rem",
                fontWeight: 700,
                color: "#F8FAFC",
              }}
            >
              {analysis ? "10 Stages Processed" : "Awaiting Palms"}
            </div>
            <div style={{ fontSize: "0.75rem", color: "#64748B", marginTop: "4px" }}>
              CLAHE, Otsu, Sobel, Canny & Skeleton
            </div>
          </div>
        </div>

        {/* AI Reading Status */}
        <div
          className="glass-panel"
          style={{ padding: "18px", cursor: "pointer" }}
          onClick={() => onNavigate("reading")}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "10px",
            }}
          >
            <span
              style={{
                fontSize: "0.85rem",
                color: "#94A3B8",
                fontWeight: 600,
              }}
            >
              AI Reading
            </span>
            {hasReading ? (
              <span className="badge badge-cyan">Generated</span>
            ) : (
              <span className="badge badge-purple">Ready to Run</span>
            )}
          </div>
          <div style={{ marginTop: "10px" }}>
            <div
              style={{
                fontSize: "1.1rem",
                fontWeight: 700,
                color: "#F8FAFC",
              }}
            >
              {hasReading ? "Multilingual Ready" : "Gemini RAG"}
            </div>
            <div style={{ fontSize: "0.75rem", color: "#64748B", marginTop: "4px" }}>
              English • සිංහල • தமிழ்
            </div>
          </div>
        </div>
      </div>

      {/* 3-Step Workflow Cards */}
      <h3
        style={{
          fontSize: "1.2rem",
          color: "#F8FAFC",
          marginBottom: "16px",
          display: "flex",
          alignItems: "center",
          gap: "8px",
        }}
      >
        <BrainCircuit size={18} color="#8B5CF6" /> The 3-Step Scientific Workflow
      </h3>

      <div className="grid-3" style={{ marginBottom: "28px" }}>
        <div className="glass-panel" style={{ padding: "22px" }}>
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "rgba(34, 211, 238, 0.15)",
              border: "1px solid rgba(34, 211, 238, 0.3)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#22D3EE",
              fontWeight: 700,
              marginBottom: "14px",
            }}
          >
            1
          </div>
          <h4 style={{ color: "#F8FAFC", fontSize: "1.05rem", marginBottom: "8px" }}>
            Quality Verification Gate
          </h4>
          <p style={{ color: "#94A3B8", fontSize: "0.88rem", lineHeight: 1.5 }}>
            Validates silhouette edge sharpness, hand-region exposure, and frame
            coverage before processing begins. Blur and bad lighting are caught
            instantly.
          </p>
        </div>

        <div className="glass-panel" style={{ padding: "22px" }}>
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "rgba(139, 92, 246, 0.15)",
              border: "1px solid rgba(139, 92, 246, 0.3)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#A78BFA",
              fontWeight: 700,
              marginBottom: "14px",
            }}
          >
            2
          </div>
          <h4 style={{ color: "#F8FAFC", fontSize: "1.05rem", marginBottom: "8px" }}>
            10-Stage CV Pipeline
          </h4>
          <p style={{ color: "#94A3B8", fontSize: "0.88rem", lineHeight: 1.5 }}>
            Transforms palms through CLAHE contrast equalisation, adaptive skin
            segmentation, black-hat crease enhancement, and skeleton topology
            analysis.
          </p>
        </div>

        <div className="glass-panel" style={{ padding: "22px" }}>
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              background: "rgba(16, 185, 129, 0.15)",
              border: "1px solid rgba(16, 185, 129, 0.3)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#34D399",
              fontWeight: 700,
              marginBottom: "14px",
            }}
          >
            3
          </div>
          <h4 style={{ color: "#F8FAFC", fontSize: "1.05rem", marginBottom: "8px" }}>
            Multilingual RAG Gemini
          </h4>
          <p style={{ color: "#94A3B8", fontSize: "0.88rem", lineHeight: 1.5 }}>
            Grounds interpretations strictly in extracted anatomical features and 20
            curated historical palmistry passages, providing readings in English,
            Sinhala, or Tamil.
          </p>
        </div>
      </div>

      {/* Mandatory Ethical Disclaimer Banner */}
      <div
        className="glass-panel"
        style={{
          borderLeft: "4px solid #8B5CF6",
          padding: "18px 24px",
          display: "flex",
          gap: "16px",
          alignItems: "center",
        }}
      >
        <HelpCircle size={28} color="#A78BFA" style={{ flexShrink: 0 }} />
        <div style={{ fontSize: "0.85rem", color: "#CBD5E1", lineHeight: 1.5 }}>
          <strong style={{ color: "#F8FAFC" }}>Cultural & Entertainment Practice: </strong>
          Palmistry is a cultural tradition, not a scientifically validated method for
          predicting personality, health, wealth, relationships, or future events.
          Never use this application for medical, financial, employment, or life
          consequential decisions.
        </div>
      </div>
    </div>
  );
};
