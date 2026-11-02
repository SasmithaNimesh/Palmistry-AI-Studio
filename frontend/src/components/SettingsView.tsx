import React from "react";
import {
  Moon,
  Sun,
  Laptop,
  Zap,
  Globe2,
  Sparkles,
  ShieldCheck,
  RotateCcw,
} from "lucide-react";
import type { SystemStatus } from "../api";

interface SettingsViewProps {
  theme: "dark" | "light" | "system";
  setTheme: (theme: "dark" | "light" | "system") => void;
  sharpenStrength: number;
  setSharpenStrength: (val: number) => void;
  defaultLanguage: "en" | "si" | "ta";
  setDefaultLanguage: (lang: "en" | "si" | "ta") => void;
  status: SystemStatus | null;
  onResetAll: () => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({
  theme,
  setTheme,
  sharpenStrength,
  setSharpenStrength,
  defaultLanguage,
  setDefaultLanguage,
  status,
  onResetAll,
}) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div>
        <h2 style={{ fontSize: "1.6rem", color: "#F8FAFC", marginBottom: "4px" }}>
          Application Settings & Preferences
        </h2>
        <p style={{ color: "#94A3B8", fontSize: "0.88rem" }}>
          Customize theme appearance, digital image pre-processing sharpness, language, and AI engine parameters.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        {/* 1. THEME SELECTION */}
        <div className="glass-panel" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <Sun size={20} color="#F59E0B" />
            <h3 style={{ fontSize: "1.05rem", color: "#F8FAFC" }}>Theme & Appearance</h3>
          </div>
          <p style={{ fontSize: "0.82rem", color: "#94A3B8" }}>
            Choose between dark luxury, crisp light studio, or automatic operating system sync.
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "10px" }}>
            <button
              onClick={() => setTheme("dark")}
              style={{
                padding: "14px 10px",
                borderRadius: "10px",
                background: theme === "dark" ? "rgba(124, 58, 237, 0.25)" : "rgba(255, 255, 255, 0.03)",
                border: `1px solid ${theme === "dark" ? "#8B5CF6" : "rgba(255, 255, 255, 0.08)"}`,
                color: theme === "dark" ? "#FFFFFF" : "#94A3B8",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "8px",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: "0.82rem",
                transition: "all 0.2s ease",
              }}
            >
              <Moon size={18} color={theme === "dark" ? "#22D3EE" : "#64748B"} />
              <span>Dark Mode</span>
            </button>

            <button
              onClick={() => setTheme("light")}
              style={{
                padding: "14px 10px",
                borderRadius: "10px",
                background: theme === "light" ? "rgba(124, 58, 237, 0.25)" : "rgba(255, 255, 255, 0.03)",
                border: `1px solid ${theme === "light" ? "#8B5CF6" : "rgba(255, 255, 255, 0.08)"}`,
                color: theme === "light" ? "#FFFFFF" : "#94A3B8",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "8px",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: "0.82rem",
                transition: "all 0.2s ease",
              }}
            >
              <Sun size={18} color={theme === "light" ? "#F59E0B" : "#64748B"} />
              <span>Light Mode</span>
            </button>

            <button
              onClick={() => setTheme("system")}
              style={{
                padding: "14px 10px",
                borderRadius: "10px",
                background: theme === "system" ? "rgba(124, 58, 237, 0.25)" : "rgba(255, 255, 255, 0.03)",
                border: `1px solid ${theme === "system" ? "#8B5CF6" : "rgba(255, 255, 255, 0.08)"}`,
                color: theme === "system" ? "#FFFFFF" : "#94A3B8",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "8px",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: "0.82rem",
                transition: "all 0.2s ease",
              }}
            >
              <Laptop size={18} color={theme === "system" ? "#38BDF8" : "#64748B"} />
              <span>System Sync</span>
            </button>
          </div>
        </div>

        {/* 2. PRE-PROCESSING SHARPNESS ENHANCEMENT */}
        <div className="glass-panel" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <Zap size={20} color="#22D3EE" />
            <h3 style={{ fontSize: "1.05rem", color: "#F8FAFC" }}>Pre-Processing Sharpness Boost</h3>
          </div>
          <p style={{ fontSize: "0.82rem", color: "#94A3B8" }}>
            Applies Unsharp Masking prior to downscaling and thresholding to enhance faint crease boundaries.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: "0.82rem", color: "#CBD5E1", fontWeight: 500 }}>
                Sharpness Strength: <strong>{sharpenStrength.toFixed(1)}x</strong>
              </span>
              <span
                style={{
                  fontSize: "0.72rem",
                  padding: "2px 8px",
                  borderRadius: "9999px",
                  background: sharpenStrength === 0.6 ? "rgba(34, 211, 238, 0.15)" : "rgba(255, 255, 255, 0.05)",
                  color: sharpenStrength === 0.6 ? "#22D3EE" : "#94A3B8",
                  fontWeight: 600,
                }}
              >
                {sharpenStrength === 0
                  ? "Off"
                  : sharpenStrength <= 0.4
                  ? "Mild"
                  : sharpenStrength <= 0.7
                  ? "Recommended"
                  : "High Boost"}
              </span>
            </div>

            <input
              type="range"
              min="0"
              max="1.2"
              step="0.1"
              value={sharpenStrength}
              onChange={(e) => setSharpenStrength(parseFloat(e.target.value))}
              style={{
                width: "100%",
                accentColor: "#8B5CF6",
                cursor: "pointer",
              }}
            />

            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.72rem", color: "#64748B" }}>
              <span>0.0 (Off)</span>
              <span>0.6 (Recommended)</span>
              <span>1.2 (Ultra)</span>
            </div>
          </div>
        </div>

        {/* 3. DEFAULT READING LANGUAGE */}
        <div className="glass-panel" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <Globe2 size={20} color="#A78BFA" />
            <h3 style={{ fontSize: "1.05rem", color: "#F8FAFC" }}>Default Reading Language</h3>
          </div>
          <p style={{ fontSize: "0.82rem", color: "#94A3B8" }}>
            Choose the default primary language for synthesized palm readings and assistant dialogues.
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "10px" }}>
            {[
              { id: "en", label: "English", sub: "Global" },
              { id: "si", label: "සිංහල", sub: "Sinhala" },
              { id: "ta", label: "தமிழ்", sub: "Tamil" },
            ].map((l) => (
              <button
                key={l.id}
                onClick={() => setDefaultLanguage(l.id as any)}
                style={{
                  padding: "12px 8px",
                  borderRadius: "10px",
                  background: defaultLanguage === l.id ? "rgba(124, 58, 237, 0.25)" : "rgba(255, 255, 255, 0.03)",
                  border: `1px solid ${defaultLanguage === l.id ? "#8B5CF6" : "rgba(255, 255, 255, 0.08)"}`,
                  color: defaultLanguage === l.id ? "#FFFFFF" : "#94A3B8",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: "4px",
                  cursor: "pointer",
                }}
              >
                <span style={{ fontSize: "0.95rem", fontWeight: 700 }}>{l.label}</span>
                <span style={{ fontSize: "0.7rem", color: "#64748B" }}>{l.sub}</span>
              </button>
            ))}
          </div>
        </div>

        {/* 4. GEMINI AI ENGINE CONFIG */}
        <div className="glass-panel" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <Sparkles size={20} color="#10B981" />
            <h3 style={{ fontSize: "1.05rem", color: "#F8FAFC" }}>Gemini Engine Status</h3>
          </div>
          <p style={{ fontSize: "0.82rem", color: "#94A3B8" }}>
            Model auto-selection and RAG knowledge base parameters.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "8px 12px",
                background: "rgba(0,0,0,0.25)",
                borderRadius: "8px",
                fontSize: "0.82rem",
              }}
            >
              <span style={{ color: "#94A3B8" }}>Active Model</span>
              <span style={{ color: "#38BDF8", fontFamily: "monospace", fontWeight: 600 }}>
                {status?.model || "gemini-3.5-flash-lite"}
              </span>
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "8px 12px",
                background: "rgba(0,0,0,0.25)",
                borderRadius: "8px",
                fontSize: "0.82rem",
              }}
            >
              <span style={{ color: "#94A3B8" }}>RAG Knowledge Passages</span>
              <span style={{ color: "#34D399", fontWeight: 600 }}>20 Grounded Passages</span>
            </div>

            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "8px 12px",
                background: "rgba(0,0,0,0.25)",
                borderRadius: "8px",
                fontSize: "0.82rem",
              }}
            >
              <span style={{ color: "#94A3B8" }}>API Status</span>
              <span style={{ color: status?.has_key ? "#34D399" : "#F87171", fontWeight: 600 }}>
                {status?.has_key ? "● Authenticated" : "○ Key Missing"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Reset & Storage Clear */}
      <div
        className="glass-panel"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "18px 24px",
          marginTop: "6px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <ShieldCheck size={24} color="#34D399" />
          <div>
            <div style={{ fontSize: "0.92rem", fontWeight: 700, color: "#F8FAFC" }}>
              In-Memory RAM Shield Active
            </div>
            <div style={{ fontSize: "0.78rem", color: "#94A3B8" }}>
              Uploaded images are processed purely in ephemeral RAM and never saved to disk.
            </div>
          </div>
        </div>

        <button className="btn-secondary" onClick={onResetAll}>
          <RotateCcw size={15} />
          <span>Reset All Defaults</span>
        </button>
      </div>
    </div>
  );
};
