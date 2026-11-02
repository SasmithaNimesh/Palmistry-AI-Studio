import React, { useRef, useState } from "react";
import {
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Cpu,
  Layers,
  ArrowRight,
  RefreshCw,
  Trash2,
  Zap,
} from "lucide-react";
import type { PalmSlot } from "../api";
import { validateUpload } from "../api";

interface UploadViewProps {
  leftPalm: PalmSlot | null;
  rightPalm: PalmSlot | null;
  setLeftPalm: (slot: PalmSlot | null) => void;
  setRightPalm: (slot: PalmSlot | null) => void;
  onRunAnalysis: () => void;
  onLoadSample: (pair: string) => void;
  isAnalyzing: boolean;
  sharpenStrength: number;
  setSharpenStrength: (val: number) => void;
}

export const UploadView: React.FC<UploadViewProps> = ({
  leftPalm,
  rightPalm,
  setLeftPalm,
  setRightPalm,
  onRunAnalysis,
  onLoadSample,
  isAnalyzing,
  sharpenStrength,
  setSharpenStrength,
}) => {
  const [validatingSide, setValidatingSide] = useState<string | null>(null);
  const [draggingSide, setDraggingSide] = useState<string | null>(null);

  const leftInputRef = useRef<HTMLInputElement>(null);
  const rightInputRef = useRef<HTMLInputElement>(null);

  const processFile = async (file: File, side: "Left" | "Right") => {
    if (!file) return;

    setValidatingSide(side);
    try {
      const res = await validateUpload(side, file);
      const slot: PalmSlot = {
        name: file.name,
        raw_b64: res.raw_b64,
        preview_url: res.preview_url,
        ok: res.ok,
        metrics: res.metrics,
        errors: res.errors,
        warnings: res.warnings,
      };

      if (side === "Left") setLeftPalm(slot);
      else setRightPalm(slot);
    } catch (err: any) {
      alert(`Validation error: ${err.message}`);
    } finally {
      setValidatingSide(null);
    }
  };

  const handleFileChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    side: "Left" | "Right"
  ) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file, side);
    }
    // Reset input value so selecting the same file triggers onChange again
    e.target.value = "";
  };

  const handleDragOver = (e: React.DragEvent, side: "Left" | "Right") => {
    e.preventDefault();
    e.stopPropagation();
    if (draggingSide !== side) {
      setDraggingSide(side);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDraggingSide(null);
  };

  const handleDrop = (e: React.DragEvent, side: "Left" | "Right") => {
    e.preventDefault();
    e.stopPropagation();
    setDraggingSide(null);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      processFile(files[0], side);
    }
  };

  const isReady = leftPalm?.ok && rightPalm?.ok;

  const renderSlot = (
    side: "Left" | "Right",
    slot: PalmSlot | null,
    inputRef: React.RefObject<HTMLInputElement | null>
  ) => {
    const isValidating = validatingSide === side;
    const isDragging = draggingSide === side;

    return (
      <div
        className="glass-panel"
        style={{
          display: "flex",
          flexDirection: "column",
          position: "relative",
          borderColor: isDragging
            ? "var(--cyan)"
            : slot?.ok
            ? "rgba(16, 185, 129, 0.4)"
            : "var(--border-glass)",
          boxShadow: isDragging
            ? "0 0 30px rgba(34, 211, 238, 0.35)"
            : undefined,
          transition: "all 0.2s ease",
        }}
        onDragOver={(e) => handleDragOver(e, side)}
        onDragEnter={(e) => handleDragOver(e, side)}
        onDragLeave={(e) => handleDragLeave(e)}
        onDrop={(e) => handleDrop(e, side)}
      >
        {/* Hidden File Input ALWAYS mounted in DOM */}
        <input
          type="file"
          ref={inputRef}
          style={{ display: "none" }}
          accept="image/jpeg,image/png,image/jpg"
          onChange={(e) => handleFileChange(e, side)}
        />

        {/* Dragging Overlay */}
        {isDragging && (
          <div
            style={{
              position: "absolute",
              inset: 0,
              background: "rgba(14, 19, 34, 0.9)",
              borderRadius: "16px",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 30,
              border: "2px dashed #22D3EE",
              pointerEvents: "none",
            }}
          >
            <UploadCloud size={48} color="#22D3EE" />
            <div
              style={{
                fontSize: "1.1rem",
                fontWeight: 700,
                color: "#F8FAFC",
                marginTop: "12px",
              }}
            >
              Drop to {slot ? "Replace" : "Upload"} {side} Palm
            </div>
            <div style={{ fontSize: "0.82rem", color: "#94A3B8" }}>
              JPG, JPEG or PNG
            </div>
          </div>
        )}

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "16px",
          }}
        >
          <h3 style={{ fontSize: "1.15rem", color: "#F8FAFC" }}>{side} Palm</h3>
          {slot && (
            <span
              className={`badge ${
                slot.ok ? "badge-emerald" : "badge-amber"
              }`}
            >
              {slot.ok ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
              {slot.ok ? "Accepted" : "Action Required"}
            </span>
          )}
        </div>

        {/* Upload Zone / Preview */}
        {slot?.preview_url ? (
          <div style={{ position: "relative", marginBottom: "16px" }}>
            <img
              src={slot.preview_url}
              alt={`${side} palm preview`}
              style={{
                width: "100%",
                height: "260px",
                objectFit: "contain",
                background: "rgba(0, 0, 0, 0.4)",
                borderRadius: "12px",
                border: "1px solid var(--border-glass)",
                display: "block",
              }}
            />
            {/* Top action buttons */}
            <div
              style={{
                position: "absolute",
                top: "10px",
                right: "10px",
                display: "flex",
                gap: "8px",
                zIndex: 10,
              }}
            >
              <button
                type="button"
                className="btn-secondary"
                style={{
                  padding: "6px 12px",
                  fontSize: "0.8rem",
                  background: "rgba(18, 25, 44, 0.9)",
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  inputRef.current?.click();
                }}
                title="Replace photo"
              >
                <RefreshCw size={13} color="#22D3EE" /> Replace
              </button>

              <button
                type="button"
                className="btn-secondary"
                style={{
                  padding: "6px 10px",
                  fontSize: "0.8rem",
                  background: "rgba(18, 25, 44, 0.9)",
                  color: "#F87171",
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  if (side === "Left") setLeftPalm(null);
                  else setRightPalm(null);
                }}
                title="Remove photo"
              >
                <Trash2 size={13} />
              </button>
            </div>

            <div
              style={{
                fontSize: "0.78rem",
                color: "#94A3B8",
                marginTop: "6px",
                textAlign: "center",
              }}
            >
              Drag & drop a new image here anytime to replace
            </div>
          </div>
        ) : (
          <div
            onClick={() => inputRef.current?.click()}
            style={{
              height: "240px",
              border: "2px dashed rgba(139, 92, 246, 0.35)",
              borderRadius: "14px",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer",
              background: "rgba(16, 21, 37, 0.5)",
              transition: "all 0.2s ease",
              marginBottom: "16px",
              padding: "20px",
              textAlign: "center",
            }}
            onMouseEnter={(e) =>
              (e.currentTarget.style.borderColor = "#22D3EE")
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.borderColor = "rgba(139, 92, 246, 0.35)")
            }
          >
            <div
              style={{
                width: "56px",
                height: "56px",
                borderRadius: "50%",
                background: "rgba(139, 92, 246, 0.15)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#A78BFA",
                marginBottom: "12px",
              }}
            >
              <UploadCloud size={28} />
            </div>
            <div
              style={{
                fontSize: "0.95rem",
                fontWeight: 600,
                color: "#F8FAFC",
                marginBottom: "4px",
              }}
            >
              {isValidating
                ? "Running Quality Diagnostics…"
                : `Click to Browse or Drag ${side} Palm Photo Here`}
            </div>
            <div style={{ fontSize: "0.78rem", color: "#94A3B8" }}>
              JPG, JPEG or PNG • Max 15MB • Plain Background
            </div>
          </div>
        )}

        {/* Quality Metrics Scorecard */}
        {slot?.metrics && (
          <div
            style={{
              background: "rgba(11, 16, 29, 0.7)",
              border: "1px solid var(--border-glass)",
              borderRadius: "10px",
              padding: "14px",
              marginTop: "auto",
            }}
          >
            <div
              style={{
                fontSize: "0.75rem",
                textTransform: "uppercase",
                letterSpacing: "0.06em",
                color: "#94A3B8",
                fontWeight: 700,
                marginBottom: "8px",
              }}
            >
              Quality Verification Scorecard
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
              <div
                style={{
                  background: "rgba(255, 255, 255, 0.03)",
                  padding: "8px 10px",
                  borderRadius: "6px",
                }}
              >
                <div style={{ fontSize: "0.72rem", color: "#94A3B8" }}>
                  Sharpness (Edge):
                </div>
                <div
                  style={{
                    fontSize: "0.85rem",
                    fontWeight: 600,
                    color:
                      slot.metrics.edge_width_px < 4.0
                        ? "#34D399"
                        : slot.metrics.edge_width_px < 5.0
                        ? "#FCD34D"
                        : "#F87171",
                  }}
                >
                  {slot.metrics.edge_width_px.toFixed(2)} px{" "}
                  {slot.metrics.edge_width_px < 4.0
                    ? "(Sharp)"
                    : slot.metrics.edge_width_px < 5.0
                    ? "(Fair)"
                    : "(Blurry)"}
                </div>
              </div>

              <div
                style={{
                  background: "rgba(255, 255, 255, 0.03)",
                  padding: "8px 10px",
                  borderRadius: "6px",
                }}
              >
                <div style={{ fontSize: "0.72rem", color: "#94A3B8" }}>
                  Exposure / Bright:
                </div>
                <div
                  style={{
                    fontSize: "0.85rem",
                    fontWeight: 600,
                    color:
                      slot.metrics.brightness >= 50 &&
                      slot.metrics.brightness <= 210
                        ? "#34D399"
                        : "#FCD34D",
                  }}
                >
                  {slot.metrics.brightness.toFixed(1)} / 255
                </div>
              </div>

              <div
                style={{
                  background: "rgba(255, 255, 255, 0.03)",
                  padding: "8px 10px",
                  borderRadius: "6px",
                }}
              >
                <div style={{ fontSize: "0.72rem", color: "#94A3B8" }}>
                  Hand Coverage:
                </div>
                <div
                  style={{
                    fontSize: "0.85rem",
                    fontWeight: 600,
                    color:
                      slot.metrics.hand_fraction >= 0.15 ? "#34D399" : "#F87171",
                  }}
                >
                  {(slot.metrics.hand_fraction * 100).toFixed(1)}% of frame
                </div>
              </div>

              <div
                style={{
                  background: "rgba(255, 255, 255, 0.03)",
                  padding: "8px 10px",
                  borderRadius: "6px",
                }}
              >
                <div style={{ fontSize: "0.72rem", color: "#94A3B8" }}>
                  Segmentation:
                </div>
                <div
                  style={{
                    fontSize: "0.85rem",
                    fontWeight: 600,
                    color: "#A78BFA",
                  }}
                >
                  {slot.metrics.segmentation}
                </div>
              </div>
            </div>

            {/* Error alerts */}
            {slot.errors && slot.errors.length > 0 && (
              <div style={{ marginTop: "10px" }}>
                {slot.errors.map((err, i) => (
                  <div
                    key={i}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      color: "#F87171",
                      fontSize: "0.78rem",
                      marginTop: "4px",
                    }}
                  >
                    <XCircle size={14} style={{ flexShrink: 0 }} />
                    <span>{err}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Warnings */}
            {slot.warnings && slot.warnings.length > 0 && (
              <div style={{ marginTop: "6px" }}>
                {slot.warnings.map((w, i) => (
                  <div
                    key={i}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      color: "#FCD34D",
                      fontSize: "0.78rem",
                      marginTop: "4px",
                    }}
                  >
                    <AlertTriangle size={14} style={{ flexShrink: 0 }} />
                    <span>{w}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div>
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
            Palm Capture & Quality Gate
          </h2>
          <p style={{ color: "#94A3B8", fontSize: "0.9rem" }}>
            Drag & drop images directly, click to browse, or select a demo pair.
          </p>
        </div>

        {/* Demo Fast Loaders */}
        <div style={{ display: "flex", gap: "10px" }}>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => onLoadSample("pair1")}
            style={{ fontSize: "0.85rem", padding: "8px 14px" }}
          >
            <Cpu size={15} color="#22D3EE" />
            <span>Load Demo (Pair 1)</span>
          </button>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => onLoadSample("pair2")}
            style={{ fontSize: "0.85rem", padding: "8px 14px" }}
          >
            <Cpu size={15} color="#A78BFA" />
            <span>Load Demo (Pair 2)</span>
          </button>
        </div>
      </div>

      {/* 2-Slot Grid */}
      <div className="grid-2" style={{ marginBottom: "20px" }}>
        {renderSlot("Left", leftPalm, leftInputRef)}
        {renderSlot("Right", rightPalm, rightInputRef)}
      </div>

      {/* Pre-Processing Sharpness Enhancement Bar */}
      <div
        className="glass-panel"
        style={{
          marginBottom: "20px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "14px",
          padding: "14px 20px",
          background: "rgba(139, 92, 246, 0.08)",
          borderColor: "rgba(139, 92, 246, 0.28)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <Zap size={20} color="#22D3EE" />
          <div>
            <div style={{ fontSize: "0.88rem", fontWeight: 600, color: "#F8FAFC" }}>
              Pre-Processing Sharpness Enhancement (Unsharp Mask)
            </div>
            <div style={{ fontSize: "0.74rem", color: "#94A3B8" }}>
              Sharpen edge gradients and fine creases before CLAHE, segmentation, and skeletonization.
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {[
            { val: 0.0, label: "Off (0.0x)" },
            { val: 0.3, label: "Mild (0.3x)" },
            { val: 0.6, label: "Normal (0.6x)" },
            { val: 1.0, label: "High (1.0x)" },
          ].map((lvl) => (
            <button
              key={lvl.val}
              type="button"
              onClick={() => setSharpenStrength(lvl.val)}
              style={{
                padding: "6px 12px",
                borderRadius: "6px",
                fontSize: "0.78rem",
                fontWeight: 600,
                background:
                  sharpenStrength === lvl.val
                    ? "rgba(34, 211, 238, 0.2)"
                    : "rgba(255, 255, 255, 0.04)",
                border: `1px solid ${
                  sharpenStrength === lvl.val
                    ? "#22D3EE"
                    : "rgba(255, 255, 255, 0.1)"
                }`,
                color: sharpenStrength === lvl.val ? "#22D3EE" : "#94A3B8",
                cursor: "pointer",
                transition: "all 0.2s ease",
              }}
            >
              {lvl.label}
            </button>
          ))}
        </div>
      </div>

      {/* Action Bar */}
      <div
        className="glass-panel"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "16px",
          borderColor: isReady ? "rgba(34, 211, 238, 0.4)" : "var(--border-glass)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div
            style={{
              width: "40px",
              height: "40px",
              borderRadius: "10px",
              background: isReady
                ? "rgba(16, 185, 129, 0.2)"
                : "rgba(255, 255, 255, 0.05)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: isReady ? "#34D399" : "#64748B",
            }}
          >
            {isReady ? <CheckCircle2 size={22} /> : <Layers size={22} />}
          </div>
          <div>
            <div
              style={{
                fontSize: "0.95rem",
                fontWeight: 600,
                color: "#F8FAFC",
              }}
            >
              {isReady
                ? "Both Palms Successfully Verified"
                : "Awaiting Palm Photo Uploads"}
            </div>
            <div style={{ fontSize: "0.8rem", color: "#94A3B8" }}>
              {isReady
                ? "Ready to execute the 10-stage digital image processing pipeline."
                : "Drag & drop photos or select a demo pair to continue."}
            </div>
          </div>
        </div>

        <button
          className="btn-primary"
          disabled={!isReady || isAnalyzing}
          onClick={onRunAnalysis}
          style={{ minWidth: "220px", justifyContent: "center" }}
        >
          {isAnalyzing ? (
            <>
              <RefreshCw size={18} className="animate-spin" />
              <span>Analyzing Pipeline…</span>
            </>
          ) : (
            <>
              <span>⚡ Start Full Analysis</span>
              <ArrowRight size={18} />
            </>
          )}
        </button>
      </div>
    </div>
  );
};
