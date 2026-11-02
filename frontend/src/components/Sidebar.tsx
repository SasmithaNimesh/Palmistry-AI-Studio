import React from "react";
import {
  LayoutDashboard,
  UploadCloud,
  Cpu,
  Scan,
  BookOpenCheck,
  BotMessageSquare,
  Clock,
  FileText,
  Settings,
  CheckCircle2,
  Sparkles,
  RotateCcw,
} from "lucide-react";
import type { SystemStatus, PalmSlot, AnalysisResult } from "../api";

interface SidebarProps {
  currentTab: string;
  setTab: (tab: string) => void;
  status: SystemStatus | null;
  leftPalm: PalmSlot | null;
  rightPalm: PalmSlot | null;
  analysis: AnalysisResult | null;
  hasReading: boolean;
  onReset: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  setTab,
  status,
  leftPalm,
  rightPalm,
  analysis,
  hasReading,
  onReset,
}) => {
  const navItems = [
    { id: "dashboard", label: "Overview", icon: LayoutDashboard },
    { id: "upload", label: "Palm Upload", icon: UploadCloud },
    { id: "cvlab", label: "Image Processing", icon: Cpu },
    { id: "features", label: "Detected Features", icon: Scan },
    { id: "reading", label: "AI Reading", icon: BookOpenCheck },
    { id: "assistant", label: "AI Assistant", icon: BotMessageSquare },
    { id: "history", label: "History", icon: Clock },
    { id: "methodology", label: "Methodology", icon: FileText },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  const hasUploads = Boolean(leftPalm && rightPalm);
  const isValidated = Boolean(leftPalm?.ok && rightPalm?.ok);
  const isProcessed = Boolean(analysis);
  const hasFeatures = Boolean(analysis?.features);

  return (
    <aside className="sidebar">
      {/* Brand Logo & Header */}
      <div className="sidebar-header">
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div
            style={{
              width: "40px",
              height: "40px",
              borderRadius: "10px",
              background: "linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "1.3rem",
              boxShadow: "0 0 16px rgba(124, 58, 237, 0.45)",
            }}
          >
            🖐
          </div>
          <div>
            <div
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 700,
                fontSize: "1.05rem",
                color: "#F8FAFC",
                letterSpacing: "-0.01em",
              }}
            >
              Palmistry AI
            </div>
            <div
              style={{
                fontSize: "0.7rem",
                color: "#94A3B8",
                fontWeight: 400,
              }}
            >
              AI-Powered Palm Analysis
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav style={{ flex: 1, padding: "12px 0", overflowY: "auto" }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <div
              key={item.id}
              className={`nav-item ${isActive ? "active" : ""}`}
              onClick={() => {
                if (item.id === "history" || item.id === "settings") {
                  alert(`${item.label} preferences are active.`);
                  return;
                }
                setTab(item.id);
              }}
            >
              <Icon size={17} color={isActive ? "#FFFFFF" : "#94A3B8"} />
              <span>{item.label}</span>
            </div>
          );
        })}
      </nav>

      {/* SESSION STATUS HUD */}
      <div
        style={{
          padding: "16px 18px",
          borderTop: "1px solid var(--border-glass)",
          background: "rgba(6, 9, 20, 0.6)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: "12px",
          }}
        >
          <span
            style={{
              fontSize: "0.7rem",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: "#94A3B8",
              fontWeight: 700,
            }}
          >
            SESSION STATUS
          </span>
          <span
            style={{
              fontSize: "0.68rem",
              padding: "2px 8px",
              borderRadius: "9999px",
              background: "rgba(16, 185, 129, 0.2)",
              color: "#34D399",
              fontWeight: 600,
              border: "1px solid rgba(16, 185, 129, 0.4)",
            }}
          >
            Active
          </span>
        </div>

        {/* Steps with Checkmarks */}
        <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginBottom: "16px" }}>
          {[
            { label: "Images Uploaded", done: hasUploads },
            { label: "Quality Validation", done: isValidated },
            { label: "Processing", done: isProcessed },
            { label: "Features Extracted", done: hasFeatures },
            { label: "AI Reading Generated", done: hasReading },
          ].map((st, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                fontSize: "0.76rem",
                color: st.done ? "#E2E8F0" : "#64748B",
              }}
            >
              <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <CheckCircle2
                  size={14}
                  color={st.done ? "#10B981" : "#475569"}
                  fill={st.done ? "rgba(16, 185, 129, 0.2)" : "transparent"}
                />
                {st.label}
              </span>
              {st.done && (
                <span style={{ color: "#818CF8", fontSize: "0.75rem" }}>✓</span>
              )}
            </div>
          ))}

          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              fontSize: "0.76rem",
              color: hasReading ? "#E2E8F0" : "#94A3B8",
            }}
          >
            <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <div
                style={{
                  width: "14px",
                  height: "14px",
                  borderRadius: "50%",
                  background: "#7C3AED",
                  color: "#FFFFFF",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "0.6rem",
                  fontWeight: 700,
                }}
              >
                6
              </div>
              AI Assistant Ready
            </span>
            <span style={{ color: "#34D399", fontSize: "0.75rem" }}>●</span>
          </div>
        </div>

        {/* Gemini API Status Box */}
        <div
          style={{
            background: "rgba(255, 255, 255, 0.03)",
            border: "1px solid var(--border-glass)",
            borderRadius: "10px",
            padding: "10px 12px",
            marginBottom: "12px",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "4px",
            }}
          >
            <span
              style={{
                fontSize: "0.72rem",
                color: "#E2E8F0",
                fontWeight: 600,
                display: "flex",
                alignItems: "center",
                gap: "5px",
              }}
            >
              <Sparkles size={12} color="#F59E0B" /> Gemini API Status
            </span>
            <span
              style={{
                fontSize: "0.65rem",
                color: "#34D399",
                background: "rgba(16, 185, 129, 0.15)",
                padding: "1px 6px",
                borderRadius: "9999px",
                fontWeight: 600,
              }}
            >
              ● Connected
            </span>
          </div>
          <div
            style={{
              fontSize: "0.68rem",
              color: "#94A3B8",
              fontFamily: "'JetBrains Mono', monospace",
              marginBottom: "2px",
            }}
          >
            Model: {status?.model || "gemini-1.5-flash-latest"}
          </div>
          <div style={{ fontSize: "0.65rem", color: "#64748B" }}>
            Last checked: Just now
          </div>
        </div>

        {/* Reset Session Button */}
        <button
          onClick={onReset}
          style={{
            width: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "6px",
            padding: "7px 12px",
            borderRadius: "8px",
            background: "rgba(239, 68, 68, 0.08)",
            border: "1px solid rgba(239, 68, 68, 0.35)",
            color: "#F87171",
            fontSize: "0.78rem",
            fontWeight: 600,
            cursor: "pointer",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(239, 68, 68, 0.18)")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(239, 68, 68, 0.08)")}
        >
          <RotateCcw size={13} /> Reset Session
        </button>
      </div>
    </aside>
  );
};
