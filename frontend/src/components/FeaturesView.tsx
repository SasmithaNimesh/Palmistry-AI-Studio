import React, { useState } from "react";
import { HandMetal } from "lucide-react";
import type { AnalysisResult } from "../api";

interface FeaturesViewProps {
  analysis: AnalysisResult | null;
  onNavigateToUpload: () => void;
}

export const FeaturesView: React.FC<FeaturesViewProps> = ({
  analysis,
  onNavigateToUpload,
}) => {
  const [side, setSide] = useState<"Left" | "Right">("Left");

  if (!analysis) {
    return (
      <div className="glass-panel" style={{ textAlign: "center", padding: "60px 20px" }}>
        <HandMetal size={48} color="#8B5CF6" style={{ marginBottom: "16px" }} />
        <h2 style={{ fontSize: "1.4rem", color: "#F8FAFC", marginBottom: "8px" }}>
          No Features Detected Yet
        </h2>
        <p style={{ color: "#94A3B8", maxWidth: "500px", margin: "0 auto 24px auto" }}>
          Run the palm analysis pipeline to view extracted anatomical creases,
          orientations, and geometric shape classification.
        </p>
        <button className="btn-primary" onClick={onNavigateToUpload}>
          Upload Palms
        </button>
      </div>
    );
  }

  const feat = analysis.features[side];
  const palm = feat.palm;
  const lines = feat.lines;
  const annImg = analysis.annotated[side];

  const lineColors: Record<string, string> = {
    heart_line: "#E63946",
    head_line: "#1D78DC",
    life_line: "#2EAA5A",
    fate_line: "#F0A014",
  };

  const elementEmblems: Record<string, { color: string; label: string; desc: string }> = {
    Fire: {
      color: "#EF4444",
      label: "Fire Hand",
      desc: "Long rectangular palm with short fingers. Traditionally associated with passion, instinct, energy, and rapid ambition.",
    },
    Earth: {
      color: "#10B981",
      label: "Earth Hand",
      desc: "Square palm with short fingers. Associated with practicality, grounded stability, realism, and mechanical skill.",
    },
    Air: {
      color: "#22D3EE",
      label: "Air Hand",
      desc: "Square palm with long fingers. Associated with intellectual curiosity, communication, analytical logic, and idea generation.",
    },
    Water: {
      color: "#8B5CF6",
      label: "Water Hand",
      desc: "Long rectangular palm with long slender fingers. Associated with intuition, deep emotional sensitivity, and creative imagination.",
    },
  };

  const elementInfo = elementEmblems[palm.palmistry_hand_type] || {
    color: "#A78BFA",
    label: `${palm.palmistry_hand_type} Hand`,
    desc: "Calculated based on silhouette palm-to-finger ratio.",
  };

  return (
    <div>
      {/* Header and Side Switcher */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "20px",
          flexWrap: "wrap",
          gap: "14px",
        }}
      >
        <div>
          <h2 style={{ fontSize: "1.6rem", color: "#F8FAFC", marginBottom: "4px" }}>
            Anatomical Palm Features & Geometry
          </h2>
          <p style={{ color: "#94A3B8", fontSize: "0.9rem" }}>
            Computer vision crease detection, directional vectors, and hand shape
            morphology.
          </p>
        </div>

        <div
          style={{
            display: "flex",
            background: "rgba(16, 21, 37, 0.8)",
            padding: "4px",
            borderRadius: "10px",
            border: "1px solid var(--border-glass)",
          }}
        >
          <button
            onClick={() => setSide("Left")}
            style={{
              padding: "8px 18px",
              borderRadius: "8px",
              border: "none",
              background: side === "Left" ? "var(--violet)" : "transparent",
              color: side === "Left" ? "#FFFFFF" : "#94A3B8",
              fontWeight: 600,
              fontSize: "0.85rem",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
          >
            Left Palm Features
          </button>
          <button
            onClick={() => setSide("Right")}
            style={{
              padding: "8px 18px",
              borderRadius: "8px",
              border: "none",
              background: side === "Right" ? "var(--violet)" : "transparent",
              color: side === "Right" ? "#FFFFFF" : "#94A3B8",
              fontWeight: 600,
              fontSize: "0.85rem",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
          >
            Right Palm Features
          </button>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: "24px" }}>
        {/* Left Column: Visual Annotation */}
        <div className="glass-panel" style={{ padding: "24px" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "14px",
            }}
          >
            <h3 style={{ fontSize: "1.15rem", color: "#F8FAFC" }}>
              {side} Palm: Annotated Canvas
            </h3>
            <span className="badge badge-purple">CV Skeleton Verified</span>
          </div>

          <div
            style={{
              background: "rgba(0, 0, 0, 0.5)",
              borderRadius: "12px",
              overflow: "hidden",
              border: "1px solid var(--border-glass)",
              marginBottom: "16px",
            }}
          >
            <img
              src={annImg}
              alt={`${side} palm annotated`}
              style={{
                width: "100%",
                height: "380px",
                objectFit: "contain",
                display: "block",
                background: "#080B14",
              }}
            />
          </div>

          {/* Color Legend */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "10px",
              background: "rgba(11, 16, 29, 0.7)",
              padding: "14px",
              borderRadius: "10px",
              border: "1px solid var(--border-glass)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <div
                style={{
                  width: "12px",
                  height: "12px",
                  borderRadius: "50%",
                  background: "#E63946",
                  boxShadow: "0 0 8px #E63946",
                }}
              />
              <span style={{ fontSize: "0.82rem", color: "#F8FAFC", fontWeight: 500 }}>
                Heart Line (Red)
              </span>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <div
                style={{
                  width: "12px",
                  height: "12px",
                  borderRadius: "50%",
                  background: "#1D78DC",
                  boxShadow: "0 0 8px #1D78DC",
                }}
              />
              <span style={{ fontSize: "0.82rem", color: "#F8FAFC", fontWeight: 500 }}>
                Head Line (Cyan)
              </span>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <div
                style={{
                  width: "12px",
                  height: "12px",
                  borderRadius: "50%",
                  background: "#2EAA5A",
                  boxShadow: "0 0 8px #2EAA5A",
                }}
              />
              <span style={{ fontSize: "0.82rem", color: "#F8FAFC", fontWeight: 500 }}>
                Life Line (Green)
              </span>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <div
                style={{
                  width: "12px",
                  height: "12px",
                  borderRadius: "50%",
                  background: "#F0A014",
                  boxShadow: "0 0 8px #F0A014",
                }}
              />
              <span style={{ fontSize: "0.82rem", color: "#F8FAFC", fontWeight: 500 }}>
                Fate Line (Amber)
              </span>
            </div>
          </div>
        </div>

        {/* Right Column: Morphology & Feature Cards */}
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {/* Hand Morphology Card */}
          <div
            className="glass-panel"
            style={{
              padding: "20px",
              borderColor: elementInfo.color,
              background:
                "radial-gradient(circle at 90% 10%, rgba(139, 92, 246, 0.12) 0%, transparent 50%), rgba(18, 25, 44, 0.8)",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "12px",
              }}
            >
              <div>
                <span
                  style={{
                    fontSize: "0.72rem",
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                    color: elementInfo.color,
                    fontWeight: 700,
                  }}
                >
                  ELEMENTAL MORPHOLOGY
                </span>
                <h3 style={{ fontSize: "1.25rem", color: "#F8FAFC" }}>
                  {elementInfo.label}
                </h3>
              </div>
              <div
                style={{
                  padding: "6px 14px",
                  borderRadius: "8px",
                  background: "rgba(255, 255, 255, 0.05)",
                  border: `1px solid ${elementInfo.color}`,
                  color: elementInfo.color,
                  fontWeight: 700,
                  fontSize: "0.88rem",
                }}
              >
                {palm.palmistry_hand_type}
              </div>
            </div>

            <p
              style={{
                fontSize: "0.86rem",
                color: "#CBD5E1",
                lineHeight: 1.5,
                marginBottom: "14px",
              }}
            >
              {elementInfo.desc}
            </p>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "8px",
              }}
            >
              <div
                style={{
                  background: "rgba(255, 255, 255, 0.03)",
                  padding: "8px 12px",
                  borderRadius: "8px",
                }}
              >
                <div style={{ fontSize: "0.72rem", color: "#94A3B8" }}>
                  Palm Aspect Ratio:
                </div>
                <div
                  style={{
                    fontSize: "0.9rem",
                    fontWeight: 600,
                    color: "#F8FAFC",
                  }}
                >
                  {palm.palm_length_to_width.toFixed(2)}{" "}
                  <span style={{ fontSize: "0.75rem", color: "#94A3B8" }}>
                    ({palm.palm_shape})
                  </span>
                </div>
              </div>

              <div
                style={{
                  background: "rgba(255, 255, 255, 0.03)",
                  padding: "8px 12px",
                  borderRadius: "8px",
                }}
              >
                <div style={{ fontSize: "0.72rem", color: "#94A3B8" }}>
                  Finger-to-Palm Ratio:
                </div>
                <div
                  style={{
                    fontSize: "0.9rem",
                    fontWeight: 600,
                    color: "#F8FAFC",
                  }}
                >
                  {palm.finger_to_palm_length.toFixed(2)}{" "}
                  <span style={{ fontSize: "0.75rem", color: "#94A3B8" }}>
                    ({palm.finger_length})
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Individual Line Cards */}
          {Object.entries(lines).map(([key, item]) => {
            const color = lineColors[key] || "#8B5CF6";
            const title = key.replace("_", " ").toUpperCase();
            const isDetected = item.status === "detected";
            const isUncertain = item.status === "uncertain";

            return (
              <div
                key={key}
                className="glass-panel"
                style={{
                  padding: "16px 20px",
                  borderLeft: `4px solid ${color}`,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "10px",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <div
                      style={{
                        width: "10px",
                        height: "10px",
                        borderRadius: "50%",
                        background: color,
                        boxShadow: `0 0 8px ${color}`,
                      }}
                    />
                    <strong style={{ fontSize: "0.95rem", color: "#F8FAFC" }}>
                      {title}
                    </strong>
                  </div>

                  <span
                    className={`badge ${
                      isDetected
                        ? "badge-emerald"
                        : isUncertain
                        ? "badge-amber"
                        : "badge-purple"
                    }`}
                  >
                    {item.status.replace("_", " ")}
                  </span>
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(3, 1fr)",
                    gap: "8px",
                    fontSize: "0.82rem",
                  }}
                >
                  <div>
                    <span style={{ color: "#94A3B8" }}>Confidence: </span>
                    <strong style={{ color: "#F8FAFC" }}>
                      {(item.confidence * 100).toFixed(0)}%
                    </strong>
                  </div>
                  <div>
                    <span style={{ color: "#94A3B8" }}>Curvature: </span>
                    <strong style={{ color: "#F8FAFC" }}>
                      {item.curvature || "N/A"}
                    </strong>
                  </div>
                  <div>
                    <span style={{ color: "#94A3B8" }}>Prominence: </span>
                    <strong style={{ color: "#F8FAFC" }}>
                      {item.prominence || "N/A"}
                    </strong>
                  </div>
                </div>

                {item.start_region && item.end_region && (
                  <div
                    style={{
                      fontSize: "0.78rem",
                      color: "#94A3B8",
                      marginTop: "8px",
                      borderTop: "1px solid rgba(255, 255, 255, 0.05)",
                      paddingTop: "6px",
                    }}
                  >
                    Trajectory:{" "}
                    <span style={{ color: "#CBD5E1" }}>
                      {item.start_region} → {item.end_region}
                    </span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
