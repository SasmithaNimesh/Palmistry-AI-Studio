import React, { useState } from "react";
import {
  Cpu,
  Sliders,
  BarChart2,
  Maximize2,
  Info,
} from "lucide-react";
import type { AnalysisResult } from "../api";

interface CvLabViewProps {
  analysis: AnalysisResult | null;
  onNavigateToUpload: () => void;
}

export const CvLabView: React.FC<CvLabViewProps> = ({
  analysis,
  onNavigateToUpload,
}) => {
  const [side, setSide] = useState<"Left" | "Right">("Left");
  const [selectedComparison, setSelectedComparison] = useState<number>(0);
  const [modalImage, setModalImage] = useState<{ url: string; title: string } | null>(
    null
  );

  if (!analysis) {
    return (
      <div className="glass-panel" style={{ textAlign: "center", padding: "60px 20px" }}>
        <Cpu size={48} color="#8B5CF6" style={{ marginBottom: "16px" }} />
        <h2 style={{ fontSize: "1.4rem", color: "#F8FAFC", marginBottom: "8px" }}>
          No Active Computer Vision Session
        </h2>
        <p style={{ color: "#94A3B8", maxWidth: "500px", margin: "0 auto 24px auto" }}>
          Upload both palms and run the analysis to unlock the 10-stage digital
          image processing laboratory.
        </p>
        <button className="btn-primary" onClick={onNavigateToUpload}>
          Go to Palm Upload
        </button>
      </div>
    );
  }

  const stages = analysis.stages[side];
  const comparisons = analysis.comparisons;
  const currentComp = comparisons[selectedComparison] || comparisons[0];

  return (
    <div>
      {/* Header & Side Switcher */}
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
            Computer Vision Processing Laboratory
          </h2>
          <p style={{ color: "#94A3B8", fontSize: "0.9rem" }}>
            Explore intermediate stages, edge filters, and adaptive histogram
            transformations.
          </p>
        </div>

        {/* Left / Right Switcher */}
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
            Left Palm Lab
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
            Right Palm Lab
          </button>
        </div>
      </div>

      {/* Comparison Selector Chips */}
      <div
        style={{
          display: "flex",
          gap: "8px",
          overflowX: "auto",
          paddingBottom: "10px",
          marginBottom: "20px",
        }}
      >
        {comparisons.map((c, i) => {
          const isSel = i === selectedComparison;
          return (
            <button
              key={i}
              onClick={() => setSelectedComparison(i)}
              style={{
                padding: "8px 14px",
                borderRadius: "8px",
                fontSize: "0.82rem",
                fontWeight: 500,
                whiteSpace: "nowrap",
                cursor: "pointer",
                background: isSel
                  ? "linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(34, 211, 238, 0.2) 100%)"
                  : "rgba(255, 255, 255, 0.04)",
                color: isSel ? "#FFFFFF" : "#94A3B8",
                border: isSel
                  ? "1px solid var(--border-cyan)"
                  : "1px solid var(--border-glass)",
                transition: "all 0.2s ease",
              }}
            >
              {c.title}
            </button>
          );
        })}
      </div>

      {/* Active Comparison Stage Card */}
      <div className="glass-panel" style={{ padding: "24px", marginBottom: "24px" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "16px",
            borderBottom: "1px solid var(--border-glass)",
            paddingBottom: "12px",
          }}
        >
          <div>
            <span className="badge badge-purple" style={{ marginBottom: "6px" }}>
              Stage Comparison {selectedComparison + 1} of {comparisons.length}
            </span>
            <h3 style={{ fontSize: "1.25rem", color: "#F8FAFC" }}>
              {currentComp.title}
            </h3>
          </div>
        </div>

        {/* Before vs After Panels */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: `repeat(${currentComp.panels.length}, 1fr)`,
            gap: "16px",
            marginBottom: "18px",
          }}
        >
          {currentComp.panels.map((panelKey, idx) => {
            const imgData = stages[panelKey];
            const isBefore = idx === 0;

            return (
              <div
                key={idx}
                style={{
                  background: "rgba(0, 0, 0, 0.4)",
                  borderRadius: "12px",
                  overflow: "hidden",
                  border: "1px solid var(--border-glass)",
                  position: "relative",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    top: "10px",
                    left: "10px",
                    background: isBefore
                      ? "rgba(100, 116, 139, 0.85)"
                      : "rgba(139, 92, 246, 0.85)",
                    color: "#FFFFFF",
                    fontSize: "0.72rem",
                    fontWeight: 700,
                    padding: "3px 8px",
                    borderRadius: "4px",
                    backdropFilter: "blur(4px)",
                    zIndex: 2,
                  }}
                >
                  {isBefore ? "BEFORE" : "AFTER"}
                </div>

                <div
                  style={{
                    position: "absolute",
                    top: "10px",
                    right: "10px",
                    zIndex: 2,
                  }}
                >
                  <button
                    onClick={() =>
                      setModalImage({ url: imgData, title: panelKey })
                    }
                    style={{
                      background: "rgba(0, 0, 0, 0.6)",
                      border: "none",
                      color: "#FFFFFF",
                      padding: "6px",
                      borderRadius: "6px",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                    title="Fullscreen Zoom"
                  >
                    <Maximize2 size={14} />
                  </button>
                </div>

                <img
                  src={imgData}
                  alt={panelKey}
                  style={{
                    width: "100%",
                    height: "300px",
                    objectFit: "contain",
                    display: "block",
                    background: "#05070D",
                  }}
                />

                <div
                  style={{
                    padding: "10px 14px",
                    fontSize: "0.82rem",
                    fontWeight: 600,
                    color: "#CBD5E1",
                    background: "rgba(11, 16, 29, 0.9)",
                    borderTop: "1px solid var(--border-glass)",
                  }}
                >
                  {panelKey}
                </div>
              </div>
            );
          })}
        </div>

        {/* Technical Rationale Box */}
        <div
          style={{
            background: "rgba(139, 92, 246, 0.08)",
            border: "1px solid rgba(139, 92, 246, 0.25)",
            borderRadius: "10px",
            padding: "14px 18px",
            display: "flex",
            alignItems: "flex-start",
            gap: "12px",
          }}
        >
          <Info size={18} color="#A78BFA" style={{ flexShrink: 0, marginTop: "2px" }} />
          <div style={{ fontSize: "0.86rem", color: "#CBD5E1", lineHeight: 1.5 }}>
            <strong style={{ color: "#F8FAFC" }}>Scientific Rationale: </strong>
            {currentComp.why}
          </div>
        </div>
      </div>

      {/* CLAHE Histogram Analyzer */}
      {stages["4h Histogram before/after CLAHE"] && (
        <div className="glass-panel" style={{ padding: "24px", marginBottom: "24px" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "16px",
            }}
          >
            <h3
              style={{
                fontSize: "1.15rem",
                color: "#F8FAFC",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              <BarChart2 size={18} color="#22D3EE" /> CLAHE Dynamic Contrast
              Distribution
            </h3>
            <span className="badge badge-cyan">Tile Grid: 8×8 • Clip: 3.0</span>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "20px" }}>
            <div
              style={{
                background: "rgba(0, 0, 0, 0.4)",
                borderRadius: "12px",
                padding: "12px",
                border: "1px solid var(--border-glass)",
              }}
            >
              <img
                src={stages["4h Histogram before/after CLAHE"]}
                alt="CLAHE Histogram"
                style={{
                  width: "100%",
                  height: "220px",
                  objectFit: "contain",
                  display: "block",
                }}
              />
            </div>

            <div style={{ display: "flex", flexDirection: "column", justifyContent: "center" }}>
              <h4 style={{ fontSize: "0.95rem", color: "#F8FAFC", marginBottom: "8px" }}>
                Why Local Equalization is Essential
              </h4>
              <p
                style={{
                  fontSize: "0.84rem",
                  color: "#94A3B8",
                  lineHeight: 1.55,
                  marginBottom: "12px",
                }}
              >
                Global histogram equalisation flattens overall image contrast,
                blowing out bright palm regions and darkening creases excessively.
              </p>
              <p style={{ fontSize: "0.84rem", color: "#94A3B8", lineHeight: 1.55 }}>
                <strong style={{ color: "#34D399" }}>CLAHE</strong> operates on
                localized 8×8 contextual pixel tiles with an enforced slope clip
                limit of 3.0. Faint crease lines gain crisp local definition
                without amplifying high-frequency skin sensor noise.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Complete Gallery of All Stages */}
      <div className="glass-panel" style={{ padding: "24px" }}>
        <h3
          style={{
            fontSize: "1.15rem",
            color: "#F8FAFC",
            marginBottom: "16px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <Sliders size={18} color="#A78BFA" /> Complete Intermediate Stage Gallery
        </h3>

        <div className="grid-4">
          {Object.entries(stages).map(([name, b64], i) => (
            <div
              key={i}
              style={{
                background: "rgba(0, 0, 0, 0.4)",
                borderRadius: "10px",
                overflow: "hidden",
                border: "1px solid var(--border-glass)",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
              onClick={() => setModalImage({ url: b64, title: name })}
            >
              <img
                src={b64}
                alt={name}
                style={{
                  width: "100%",
                  height: "140px",
                  objectFit: "contain",
                  display: "block",
                  background: "#080B14",
                }}
              />
              <div
                style={{
                  padding: "8px 10px",
                  fontSize: "0.75rem",
                  color: "#CBD5E1",
                  fontWeight: 500,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  background: "rgba(11, 16, 29, 0.9)",
                }}
                title={name}
              >
                {name}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Fullscreen Modal Preview */}
      {modalImage && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0, 0, 0, 0.85)",
            backdropFilter: "blur(8px)",
            zIndex: 100,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "40px",
          }}
          onClick={() => setModalImage(null)}
        >
          <div
            style={{
              maxWidth: "900px",
              width: "100%",
              background: "rgba(16, 21, 37, 0.95)",
              borderRadius: "16px",
              border: "1px solid var(--border-cyan)",
              overflow: "hidden",
              boxShadow: "0 20px 60px rgba(0, 0, 0, 0.8)",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "16px 20px",
                borderBottom: "1px solid var(--border-glass)",
              }}
            >
              <h4 style={{ color: "#F8FAFC", fontSize: "1rem" }}>
                {modalImage.title}
              </h4>
              <button
                onClick={() => setModalImage(null)}
                style={{
                  background: "transparent",
                  border: "none",
                  color: "#94A3B8",
                  fontSize: "1.2rem",
                  cursor: "pointer",
                }}
              >
                ✕
              </button>
            </div>
            <div style={{ padding: "20px", background: "#05070D" }}>
              <img
                src={modalImage.url}
                alt={modalImage.title}
                style={{
                  width: "100%",
                  maxHeight: "70vh",
                  objectFit: "contain",
                  display: "block",
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
