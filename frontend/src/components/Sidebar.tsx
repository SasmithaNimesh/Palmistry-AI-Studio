import React from "react";
import {
  LayoutDashboard,
  UploadCloud,
  Cpu,
  HandMetal,
  BookOpenCheck,
  BotMessageSquare,
  Sparkles,
  ShieldCheck,
  Activity,
  RotateCcw,
} from "lucide-react";
import type { SystemStatus } from "../api";

interface SidebarProps {
  currentTab: string;
  setTab: (tab: string) => void;
  status: SystemStatus | null;
  hasAnalysis: boolean;
  onReset: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  setTab,
  status,
  hasAnalysis,
  onReset,
}) => {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "upload", label: "Palm Capture & Gate", icon: UploadCloud },
    { id: "cvlab", label: "Computer Vision Lab", icon: Cpu },
    { id: "features", label: "Detected Features", icon: HandMetal },
    { id: "reading", label: "My Reading", icon: BookOpenCheck },
    { id: "assistant", label: "AI Assistant", icon: BotMessageSquare },
    { id: "methodology", label: "Methodology & Science", icon: Sparkles },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Logo & Header */}
      <div className="sidebar-header">
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div
            style={{
              width: "44px",
              height: "44px",
              borderRadius: "12px",
              background:
                "linear-gradient(135deg, rgba(139, 92, 246, 0.3) 0%, rgba(34, 211, 238, 0.2) 100%)",
              border: "1px solid rgba(139, 92, 246, 0.5)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "1.4rem",
              boxShadow: "0 0 20px rgba(139, 92, 246, 0.3)",
            }}
          >
            🖐
          </div>
          <div>
            <div
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 700,
                fontSize: "1.1rem",
                color: "#F8FAFC",
                letterSpacing: "-0.01em",
              }}
            >
              PALMISTRY AI
            </div>
            <div
              style={{
                fontSize: "0.72rem",
                color: "#22D3EE",
                fontWeight: 600,
                letterSpacing: "0.06em",
              }}
            >
              CV & GEMINI STUDIO
            </div>
          </div>
        </div>
      </div>

      {/* Navigation List */}
      <nav style={{ flex: 1, padding: "16px 0", overflowY: "auto" }}>
        <div
          style={{
            padding: "0 22px 10px 22px",
            fontSize: "0.72rem",
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            color: "#64748B",
            fontWeight: 700,
          }}
        >
          Navigation
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <div
              key={item.id}
              className={`nav-item ${isActive ? "active" : ""}`}
              onClick={() => setTab(item.id)}
            >
              <Icon size={18} color={isActive ? "#22D3EE" : "#94A3B8"} />
              <span>{item.label}</span>
              {item.id === "reading" && hasAnalysis && (
                <span
                  style={{
                    marginLeft: "auto",
                    width: "8px",
                    height: "8px",
                    borderRadius: "50%",
                    background: "#22D3EE",
                    boxShadow: "0 0 8px #22D3EE",
                  }}
                />
              )}
            </div>
          );
        })}
      </nav>

      {/* System Status HUD */}
      <div
        style={{
          padding: "18px",
          borderTop: "1px solid var(--border-glass)",
          background: "rgba(8, 11, 20, 0.6)",
        }}
      >
        <div style={{ marginBottom: "12px" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "6px",
            }}
          >
            <span
              style={{
                fontSize: "0.75rem",
                color: "#94A3B8",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <Activity size={13} color="#10B981" /> Gemini Engine:
            </span>
            <span
              style={{
                fontSize: "0.72rem",
                color: status?.has_key ? "#34D399" : "#F87171",
                fontWeight: 600,
              }}
            >
              {status?.has_key ? "Connected" : "Key Missing"}
            </span>
          </div>
          <div
            style={{
              fontSize: "0.75rem",
              color: "#CBD5E1",
              fontFamily: "'JetBrains Mono', monospace",
              background: "rgba(255, 255, 255, 0.04)",
              padding: "4px 8px",
              borderRadius: "6px",
              border: "1px solid var(--border-glass)",
            }}
          >
            {status?.model || "gemini-3.5-flash-lite"}
          </div>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            fontSize: "0.72rem",
            color: "#64748B",
            marginBottom: "14px",
          }}
        >
          <ShieldCheck size={14} color="#A78BFA" />
          <span>RAM-Only Privacy Active</span>
        </div>

        <button
          className="btn-secondary"
          style={{
            width: "100%",
            justifyContent: "center",
            padding: "8px 12px",
            fontSize: "0.82rem",
          }}
          onClick={onReset}
        >
          <RotateCcw size={14} /> Reset Session
        </button>
      </div>
    </aside>
  );
};
