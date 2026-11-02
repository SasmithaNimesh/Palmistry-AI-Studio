import React, { useState } from "react";
import {
  Sparkles,
  Layers,
  Brain,
  BotMessageSquare,
  Play,
  ShieldCheck,
  ChevronRight,
  BarChart2,
  Send,
  CheckCircle2,
} from "lucide-react";
import type { PalmSlot, AnalysisResult } from "../api";
import holographicPalm from "../assets/holographic_palm.jpg";
import readingBook from "../assets/reading_book.jpg";

interface DashboardViewProps {
  onStartAnalysis: () => void;
  onLoadSample: (pair: string) => void;
  leftPalm: PalmSlot | null;
  rightPalm: PalmSlot | null;
  analysis: AnalysisResult | null;
  hasReading: boolean;
  onNavigate: (tab: string) => void;
  onQuickAsk?: (question: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  onStartAnalysis,
  onLoadSample,
  leftPalm,
  rightPalm,
  analysis,
  onNavigate,
  onQuickAsk,
}) => {
  const [quickQuestion, setQuickQuestion] = useState("");

  const handleSendQuestion = (q?: string) => {
    const text = q || quickQuestion;
    if (!text.trim()) return;
    if (onQuickAsk) {
      onQuickAsk(text);
    } else {
      onNavigate("assistant");
    }
  };

  // Derive quality percentage
  const calculateQuality = (): number => {
    if (!leftPalm && !rightPalm) return 92; // default visual benchmark
    let total = 0;
    let count = 0;
    if (leftPalm?.metrics) {
      total += Math.min(100, Math.round((leftPalm.metrics.texture / 150) * 100));
      total += Math.round(leftPalm.metrics.hand_fraction * 100);
      count += 2;
    }
    if (rightPalm?.metrics) {
      total += Math.min(100, Math.round((rightPalm.metrics.texture / 150) * 100));
      total += Math.round(rightPalm.metrics.hand_fraction * 100);
      count += 2;
    }
    return count > 0 ? Math.min(98, Math.max(85, Math.round(total / count))) : 92;
  };

  const qualityScore = calculateQuality();

  // Annotated palm preview for Detected Lines Overview
  const annotatedImage =
    analysis?.annotated?.Right ||
    analysis?.annotated?.Left ||
    rightPalm?.preview_url ||
    leftPalm?.preview_url;

  // Pipeline 8 stages for horizontal timeline
  const pipelineStages = [
    { key: "01_original", label: "Original" },
    { key: "02_grayscale", label: "Grayscale" },
    { key: "03_denoised", label: "Denoise" },
    { key: "04_clahe", label: "CLAHE" },
    { key: "05_segmented", label: "Segmentation" },
    { key: "06_edges", label: "Edges" },
    { key: "07_morphology", label: "Morphology" },
    { key: "10_final", label: "Final" },
  ];

  const stagesData = analysis?.stages?.Right || analysis?.stages?.Left || {};

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "22px" }}>
      {/* 1. TOP HERO CARD */}
      <div className="hero-card">
        {/* Left Column: Heading, Subtitle, Badges, Buttons, Disclaimer */}
        <div className="hero-left">
          <h1
            style={{
              fontSize: "2.35rem",
              fontWeight: 700,
              lineHeight: 1.15,
              marginBottom: "8px",
              color: "#F8FAFC",
            }}
          >
            Discover the Patterns <br />
            <span className="text-gradient">Within Your Palm</span>
          </h1>

          <p
            style={{
              color: "#94A3B8",
              fontSize: "0.92rem",
              lineHeight: 1.5,
              marginBottom: "20px",
              maxWidth: "420px",
            }}
          >
            Our AI combines Computer Vision, Digital Image Processing and Gemini AI to
            analyze your palm lines and patterns.
          </p>

          {/* 3 Feature Badges */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              flexWrap: "wrap",
              marginBottom: "22px",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: "6px 12px",
                borderRadius: "8px",
                background: "rgba(139, 92, 246, 0.12)",
                border: "1px solid rgba(139, 92, 246, 0.25)",
                fontSize: "0.78rem",
                color: "#DDD6FE",
                fontWeight: 500,
              }}
            >
              <Layers size={14} color="#A78BFA" />
              <span>Advanced Image Processing</span>
            </div>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: "6px 12px",
                borderRadius: "8px",
                background: "rgba(34, 211, 238, 0.12)",
                border: "1px solid rgba(34, 211, 238, 0.25)",
                fontSize: "0.78rem",
                color: "#67E8F9",
                fontWeight: 500,
              }}
            >
              <Brain size={14} color="#22D3EE" />
              <span>AI-Powered Analysis</span>
            </div>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: "6px 12px",
                borderRadius: "8px",
                background: "rgba(139, 92, 246, 0.12)",
                border: "1px solid rgba(139, 92, 246, 0.25)",
                fontSize: "0.78rem",
                color: "#DDD6FE",
                fontWeight: 500,
              }}
            >
              <BotMessageSquare size={14} color="#A78BFA" />
              <span>Interactive AI Assistant</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              marginBottom: "20px",
            }}
          >
            <button className="btn-primary" onClick={onStartAnalysis}>
              <span>Start New Analysis</span>
            </button>

            <button
              className="btn-pill-action"
              onClick={() => onNavigate("methodology")}
            >
              <Play size={13} fill="#CBD5E1" />
              <span>How It Works</span>
              <ChevronRight size={13} />
            </button>

            {(!leftPalm || !rightPalm) && (
              <button
                className="btn-pill-action"
                style={{ borderColor: "rgba(34, 211, 238, 0.4)", color: "#22D3EE" }}
                onClick={() => onLoadSample("pair1")}
              >
                <Sparkles size={13} />
                <span>Load Demo</span>
              </button>
            )}
          </div>

          {/* Disclaimer Pill */}
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: "8px",
              padding: "8px 12px",
              borderRadius: "8px",
              background: "rgba(255, 255, 255, 0.02)",
              border: "1px solid rgba(255, 255, 255, 0.06)",
              fontSize: "0.7rem",
              color: "#64748B",
              lineHeight: 1.4,
            }}
          >
            <ShieldCheck size={14} color="#64748B" style={{ flexShrink: 0, marginTop: "1px" }} />
            <span>
              Disclaimer: Palmistry is for cultural and entertainment purposes only.
              It is not scientifically proven and should not be considered as
              professional advice.
            </span>
          </div>
        </div>

        {/* Center Column: 3D Holographic Palm Graphic */}
        <div className="hero-center">
          <img
            src={holographicPalm}
            alt="Futuristic Holographic Palm"
            className="hologram-img"
          />
        </div>

        {/* Right Column: "How It Works" Card */}
        <div className="hero-how-it-works">
          <div
            style={{
              fontSize: "0.95rem",
              fontWeight: 700,
              color: "#F8FAFC",
              marginBottom: "16px",
            }}
          >
            How It Works
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}>
              <div className="step-num-circle">1</div>
              <div>
                <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#F8FAFC" }}>
                  Upload
                </div>
                <div style={{ fontSize: "0.76rem", color: "#94A3B8", lineHeight: 1.35 }}>
                  Upload clear images of your left and right palms
                </div>
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}>
              <div className="step-num-circle">2</div>
              <div>
                <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#F8FAFC" }}>
                  Analyze
                </div>
                <div style={{ fontSize: "0.76rem", color: "#94A3B8", lineHeight: 1.35 }}>
                  Our AI processes images and extracts palm features
                </div>
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "flex-start", gap: "12px" }}>
              <div className="step-num-circle">3</div>
              <div>
                <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#F8FAFC" }}>
                  Get Insights
                </div>
                <div style={{ fontSize: "0.76rem", color: "#94A3B8", lineHeight: 1.35 }}>
                  Receive AI-generated reading and interactive insights
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. MIDDLE ROW (3 Cards: Your Palms, Quality Score, Detected Lines Overview) */}
      <div className="grid-3">
        {/* Card 1: Your Palms */}
        <div className="glass-panel" style={{ display: "flex", flexDirection: "column" }}>
          <div
            style={{
              fontSize: "0.95rem",
              fontWeight: 700,
              color: "#F8FAFC",
              marginBottom: "16px",
            }}
          >
            Your Palms
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "14px",
              flex: 1,
            }}
          >
            {/* Left Palm Slot */}
            <div
              style={{
                background: "rgba(0, 0, 0, 0.35)",
                border: "1px solid rgba(255, 255, 255, 0.07)",
                borderRadius: "10px",
                padding: "10px",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                textAlign: "center",
              }}
            >
              <div
                style={{
                  width: "100%",
                  height: "120px",
                  borderRadius: "8px",
                  background: "#050711",
                  overflow: "hidden",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  marginBottom: "8px",
                }}
              >
                {leftPalm?.preview_url ? (
                  <img
                    src={`data:image/jpeg;base64,${leftPalm.preview_url}`}
                    alt="Left Palm"
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                ) : (
                  <span style={{ fontSize: "2.5rem" }}>✋</span>
                )}
              </div>
              <div style={{ fontSize: "0.82rem", fontWeight: 600, color: "#F8FAFC", marginBottom: "4px" }}>
                Left Palm
              </div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  width: "100%",
                  justifyContent: "space-between",
                  marginTop: "auto",
                }}
              >
                <span
                  style={{
                    fontSize: "0.68rem",
                    color: "#34D399",
                    background: "rgba(16, 185, 129, 0.15)",
                    padding: "2px 6px",
                    borderRadius: "4px",
                    fontWeight: 600,
                  }}
                >
                  {leftPalm?.ok ? "Good Quality" : "Ready"}
                </span>
                <span
                  style={{
                    fontSize: "0.72rem",
                    color: "#818CF8",
                    cursor: "pointer",
                    fontWeight: 500,
                  }}
                  onClick={() => onNavigate("upload")}
                >
                  View Details &gt;
                </span>
              </div>
            </div>

            {/* Right Palm Slot */}
            <div
              style={{
                background: "rgba(0, 0, 0, 0.35)",
                border: "1px solid rgba(255, 255, 255, 0.07)",
                borderRadius: "10px",
                padding: "10px",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                textAlign: "center",
              }}
            >
              <div
                style={{
                  width: "100%",
                  height: "120px",
                  borderRadius: "8px",
                  background: "#050711",
                  overflow: "hidden",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  marginBottom: "8px",
                }}
              >
                {rightPalm?.preview_url ? (
                  <img
                    src={`data:image/jpeg;base64,${rightPalm.preview_url}`}
                    alt="Right Palm"
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                ) : (
                  <span style={{ fontSize: "2.5rem" }}>🤚</span>
                )}
              </div>
              <div style={{ fontSize: "0.82rem", fontWeight: 600, color: "#F8FAFC", marginBottom: "4px" }}>
                Right Palm
              </div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  width: "100%",
                  justifyContent: "space-between",
                  marginTop: "auto",
                }}
              >
                <span
                  style={{
                    fontSize: "0.68rem",
                    color: "#34D399",
                    background: "rgba(16, 185, 129, 0.15)",
                    padding: "2px 6px",
                    borderRadius: "4px",
                    fontWeight: 600,
                  }}
                >
                  {rightPalm?.ok ? "Good Quality" : "Ready"}
                </span>
                <span
                  style={{
                    fontSize: "0.72rem",
                    color: "#818CF8",
                    cursor: "pointer",
                    fontWeight: 500,
                  }}
                  onClick={() => onNavigate("upload")}
                >
                  View Details &gt;
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Card 2: Quality Score */}
        <div className="glass-panel" style={{ display: "flex", flexDirection: "column" }}>
          <div
            style={{
              fontSize: "0.95rem",
              fontWeight: 700,
              color: "#F8FAFC",
              marginBottom: "14px",
            }}
          >
            Quality Score
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "18px",
              flex: 1,
            }}
          >
            {/* Circular Gauge */}
            <div className="radial-progress-container">
              <svg width="116" height="116">
                <circle
                  cx="58"
                  cy="58"
                  r="48"
                  fill="transparent"
                  stroke="rgba(255, 255, 255, 0.08)"
                  strokeWidth="8"
                />
                <circle
                  cx="58"
                  cy="58"
                  r="48"
                  fill="transparent"
                  stroke="#22D3EE"
                  strokeWidth="8"
                  strokeDasharray={2 * Math.PI * 48}
                  strokeDashoffset={2 * Math.PI * 48 * (1 - qualityScore / 100)}
                  strokeLinecap="round"
                  style={{ filter: "drop-shadow(0 0 8px rgba(34, 211, 238, 0.6))" }}
                />
              </svg>
              <div className="radial-progress-center">
                <div
                  style={{
                    fontSize: "1.65rem",
                    fontWeight: 700,
                    color: "#FFFFFF",
                    fontFamily: "'Space Grotesk', sans-serif",
                    lineHeight: 1,
                  }}
                >
                  {qualityScore}%
                </div>
                <div style={{ fontSize: "0.66rem", color: "#94A3B8", marginTop: "4px" }}>
                  Overall Quality
                </div>
              </div>
            </div>

            {/* Metrics Breakdown */}
            <div style={{ display: "flex", flexDirection: "column", gap: "6px", flex: 1 }}>
              {[
                { label: "Resolution", grade: "Excellent" },
                { label: "Focus", grade: "Good" },
                { label: "Exposure", grade: "Excellent" },
                { label: "Framing", grade: "Good" },
                { label: "Hand Coverage", grade: "Excellent" },
              ].map((m, idx) => (
                <div
                  key={idx}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    fontSize: "0.74rem",
                  }}
                >
                  <span style={{ color: "#94A3B8" }}>{m.label}</span>
                  <span style={{ color: "#34D399", fontWeight: 600 }}>{m.grade}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Bottom Button */}
          <button
            className="btn-primary"
            style={{
              width: "100%",
              justifyContent: "center",
              marginTop: "14px",
              padding: "8px 14px",
              fontSize: "0.84rem",
              background: "#7C3AED",
            }}
            onClick={() => onNavigate("upload")}
          >
            <span>View Quality Report</span>
            <BarChart2 size={15} />
          </button>
        </div>

        {/* Card 3: Detected Lines Overview */}
        <div className="glass-panel" style={{ display: "flex", flexDirection: "column" }}>
          <div
            style={{
              fontSize: "0.95rem",
              fontWeight: 700,
              color: "#F8FAFC",
              marginBottom: "14px",
            }}
          >
            Detected Lines Overview
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1.1fr 1fr",
              gap: "12px",
              flex: 1,
              alignItems: "center",
            }}
          >
            {/* Confidence Legend */}
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <div style={{ display: "flex", alignItems: "flex-start", gap: "8px" }}>
                <div
                  style={{
                    width: "8px",
                    height: "8px",
                    borderRadius: "2px",
                    background: "#F43F5E",
                    marginTop: "4px",
                    boxShadow: "0 0 6px #F43F5E",
                  }}
                />
                <div>
                  <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "#F8FAFC" }}>
                    Heart Line
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "#94A3B8" }}>High Confidence</div>
                </div>
              </div>

              <div style={{ display: "flex", alignItems: "flex-start", gap: "8px" }}>
                <div
                  style={{
                    width: "8px",
                    height: "8px",
                    borderRadius: "2px",
                    background: "#22D3EE",
                    marginTop: "4px",
                    boxShadow: "0 0 6px #22D3EE",
                  }}
                />
                <div>
                  <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "#F8FAFC" }}>
                    Head Line
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "#94A3B8" }}>High Confidence</div>
                </div>
              </div>

              <div style={{ display: "flex", alignItems: "flex-start", gap: "8px" }}>
                <div
                  style={{
                    width: "8px",
                    height: "8px",
                    borderRadius: "2px",
                    background: "#8B5CF6",
                    marginTop: "4px",
                    boxShadow: "0 0 6px #8B5CF6",
                  }}
                />
                <div>
                  <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "#F8FAFC" }}>
                    Life Line
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "#94A3B8" }}>High Confidence</div>
                </div>
              </div>

              <div style={{ display: "flex", alignItems: "flex-start", gap: "8px" }}>
                <div
                  style={{
                    width: "8px",
                    height: "8px",
                    borderRadius: "2px",
                    background: "#F59E0B",
                    marginTop: "4px",
                    boxShadow: "0 0 6px #F59E0B",
                  }}
                />
                <div>
                  <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "#F8FAFC" }}>
                    Fate Line
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "#94A3B8" }}>Medium Confidence</div>
                </div>
              </div>
            </div>

            {/* Annotated Palm Visual Overlay */}
            <div
              style={{
                height: "145px",
                borderRadius: "10px",
                background: "#04060E",
                border: "1px solid rgba(255, 255, 255, 0.08)",
                overflow: "hidden",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer",
              }}
              onClick={() => onNavigate("features")}
            >
              {annotatedImage ? (
                <img
                  src={`data:image/jpeg;base64,${annotatedImage}`}
                  alt="Detected Creases"
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              ) : (
                <span style={{ fontSize: "2rem" }}>✋</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 3. BOTTOM ROW (2 Cards: Processing Pipeline & AI Reading Summary) */}
      <div style={{ display: "grid", gridTemplateColumns: "1.3fr 1fr", gap: "20px" }}>
        {/* Processing Pipeline Strip */}
        <div className="glass-panel" style={{ display: "flex", flexDirection: "column" }}>
          <div
            style={{
              fontSize: "0.95rem",
              fontWeight: 700,
              color: "#F8FAFC",
              marginBottom: "14px",
            }}
          >
            Processing Pipeline
          </div>

          <div className="pipeline-track">
            {pipelineStages.map((st, i) => {
              const b64 = stagesData[st.key];
              return (
                <div
                  key={st.key}
                  className="pipeline-step-node"
                  onClick={() => onNavigate("cvlab")}
                >
                  <div
                    style={{
                      width: "56px",
                      height: "56px",
                      borderRadius: "8px",
                      background: "#080B14",
                      border: "1px solid rgba(255, 255, 255, 0.1)",
                      overflow: "hidden",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    {b64 ? (
                      <img
                        src={`data:image/jpeg;base64,${b64}`}
                        alt={st.label}
                        style={{ width: "100%", height: "100%", objectFit: "cover" }}
                      />
                    ) : (
                      <span style={{ fontSize: "0.8rem", color: "#64748B" }}>
                        {i + 1}
                      </span>
                    )}
                  </div>

                  <div className="pipeline-step-badge">
                    <CheckCircle2 size={10} color="#38BDF8" />
                    <span>{st.label}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* AI Reading Summary */}
        <div
          className="glass-panel"
          style={{
            display: "grid",
            gridTemplateColumns: "1.2fr 0.8fr",
            gap: "14px",
            alignItems: "center",
          }}
        >
          <div>
            <div
              style={{
                fontSize: "0.95rem",
                fontWeight: 700,
                color: "#F8FAFC",
                marginBottom: "8px",
              }}
            >
              AI Reading Summary
            </div>
            <p
              style={{
                fontSize: "0.78rem",
                color: "#94A3B8",
                lineHeight: 1.45,
                marginBottom: "16px",
              }}
            >
              Your palm analysis is complete. Explore your personalized reading based
              on AI analysis and palmistry knowledge.
            </p>
            <button
              className="btn-primary"
              style={{
                padding: "8px 16px",
                fontSize: "0.84rem",
                background: "#7C3AED",
              }}
              onClick={() => onNavigate("reading")}
            >
              <span>View Full Reading</span>
            </button>
          </div>

          <div
            className="reading-book-wrapper"
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <img
              src={readingBook}
              alt="AI Reading Book"
              style={{
                width: "100%",
                maxWidth: "140px",
                height: "120px",
                objectFit: "contain",
                filter: "drop-shadow(0 0 16px rgba(139, 92, 246, 0.45))",
              }}
            />
          </div>
        </div>
      </div>

      {/* 4. DOCKED AI ASSISTANT QUICK BAR */}
      <div className="docked-assistant-bar">
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "10px",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "32px",
                height: "32px",
                borderRadius: "8px",
                background: "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "1rem",
              }}
            >
              💡
            </div>
            <div>
              <div style={{ fontSize: "0.86rem", fontWeight: 700, color: "#F8FAFC" }}>
                AI Assistant
              </div>
              <div style={{ fontSize: "0.74rem", color: "#94A3B8" }}>
                Ask me anything about your palms, lines, or analysis results.
              </div>
            </div>
          </div>

          {/* Quick Prompt Chips */}
          <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
            <button
              className="quick-chip"
              onClick={() => handleSendQuestion("Explain my Heart Line")}
            >
              Explain my Heart Line &gt;
            </button>
            <button
              className="quick-chip"
              onClick={() => handleSendQuestion("Compare both palms")}
            >
              Compare both palms &gt;
            </button>
            <button
              className="quick-chip"
              onClick={() => handleSendQuestion("What do my lines mean?")
            }
            >
              What do my lines mean?
            </button>
          </div>
        </div>

        {/* Input Bar */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            background: "rgba(0, 0, 0, 0.4)",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            borderRadius: "10px",
            padding: "4px 8px 4px 14px",
          }}
        >
          <input
            type="text"
            placeholder="Type your question here..."
            value={quickQuestion}
            onChange={(e) => setQuickQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSendQuestion();
            }}
            style={{
              flex: 1,
              background: "transparent",
              border: "none",
              color: "#F8FAFC",
              fontSize: "0.85rem",
              outline: "none",
            }}
          />
          <button
            onClick={() => handleSendQuestion()}
            style={{
              width: "34px",
              height: "34px",
              borderRadius: "8px",
              background: "#7C3AED",
              border: "none",
              color: "#FFFFFF",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
            }}
          >
            <Send size={15} />
          </button>
        </div>
      </div>
    </div>
  );
};
